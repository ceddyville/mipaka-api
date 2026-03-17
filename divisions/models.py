from django.db import models


class Country(models.Model):
    code         = models.CharField(max_length=2, unique=True)
    name         = models.CharField(max_length=100)
    native_name  = models.CharField(max_length=100, blank=True)
    max_levels   = models.PositiveSmallIntegerField(default=4)
    is_active    = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Era(models.Model):
    """
    A named historical period for a country.
    e.g. "Uganda Protectorate", "Belgian Congo", "Buganda Kingdom"
    """

    ERA_TYPE_CHOICES = [
        ("precolonial",   "Pre-colonial"),
        ("colonial",      "Colonial"),
        ("independence",  "Independence"),
        ("current",       "Current"),
    ]

    COLONIAL_POWER_CHOICES = [
        ("british",  "British"),
        ("belgian",  "Belgian"),
        ("german",   "German"),
        ("french",   "French"),
        ("italian",  "Italian"),
        ("portuguese", "Portuguese"),
        ("",         "N/A"),
    ]

    country         = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="eras")
    name            = models.CharField(max_length=200)          # "Uganda Protectorate"
    name_local      = models.CharField(max_length=200, blank=True)  # local language name
    era_type        = models.CharField(max_length=20, choices=ERA_TYPE_CHOICES)
    colonial_power  = models.CharField(max_length=20, blank=True, choices=COLONIAL_POWER_CHOICES)
    started         = models.CharField(max_length=20, blank=True)   # "1894" | "~1300" | "pre-1500"
    ended           = models.CharField(max_length=20, blank=True)   # blank = current/ongoing
    notes           = models.TextField(blank=True)
    source          = models.CharField(max_length=255, blank=True)
    source_url      = models.URLField(blank=True)

    class Meta:
        ordering = ["country", "started"]
        unique_together = ("country", "name")

    def __str__(self):
        return f"{self.country.code} | {self.name} ({self.started}–{self.ended or 'present'})"

    @property
    def is_current(self):
        return self.ended == ""


class DivisionLevel(models.Model):
    country  = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="division_levels")
    level    = models.PositiveSmallIntegerField()
    name     = models.CharField(max_length=100)
    name_sw  = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("country", "level")
        ordering = ["country", "level"]

    def __str__(self):
        return f"{self.country.code} L{self.level}: {self.name}"


class Division(models.Model):
    """
    Any administrative division at any level in any country.
    Self-referential parent/child hierarchy supports unlimited depth.
    """
    country    = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="divisions")
    parent     = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="children"
    )
    level      = models.PositiveSmallIntegerField()
    name       = models.CharField(max_length=255)          # current official name
    name_sw    = models.CharField(max_length=255, blank=True)
    code       = models.CharField(max_length=50, blank=True)
    native_id  = models.CharField(max_length=100, blank=True)
    source     = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        ordering = ["country", "level", "name"]
        indexes = [
            models.Index(fields=["country", "level"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.country.code} | L{self.level} | {self.name}"

    @property
    def level_name(self):
        try:
            return DivisionLevel.objects.get(country=self.country, level=self.level).name
        except DivisionLevel.DoesNotExist:
            return f"Level {self.level}"

    def get_ancestors(self):
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_name_for_year(self, year: int):
        """
        Returns the DivisionName record that was active in the given year,
        falling back to the current name if no historical record exists.
        """
        names = self.historical_names.filter(
            era__country=self.country
        ).select_related("era")

        for hn in names:
            era = hn.era
            try:
                start = int("".join(filter(str.isdigit, era.started or "0")) or 0)
                end   = int("".join(filter(str.isdigit, era.ended   or "9999")) or 9999)
                if start <= year <= end:
                    return hn
            except (ValueError, TypeError):
                continue
        return None


class DivisionName(models.Model):
    """
    A name a division held during a specific era.
    One division can have multiple names across different eras and languages.
    """

    NAME_TYPE_CHOICES = [
        ("official",    "Official"),
        ("indigenous",  "Indigenous / Pre-colonial"),
        ("colonial",    "Colonial"),
        ("colloquial",  "Colloquial"),
        ("historical",  "Historical"),
    ]

    division  = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="historical_names")
    era       = models.ForeignKey(Era, on_delete=models.CASCADE, related_name="division_names")
    name      = models.CharField(max_length=255)
    language  = models.CharField(max_length=100, blank=True)   # "Luganda", "French", "Kikongo"
    name_type = models.CharField(max_length=20, choices=NAME_TYPE_CHOICES, default="official")
    etymology = models.TextField(blank=True)   # e.g. "Hill of impala in Luganda"
    notes     = models.TextField(blank=True)
    source    = models.CharField(max_length=255, blank=True)
    source_url= models.URLField(blank=True)

    class Meta:
        ordering = ["era__started", "name_type"]
        unique_together = ("division", "era", "language", "name_type")

    def __str__(self):
        return f"{self.division.name} → '{self.name}' ({self.era.name}, {self.language})"
