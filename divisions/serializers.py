from rest_framework import serializers
from .models import Country, Division, DivisionLevel, Era, DivisionName


# ── ERA ───────────────────────────────────────────────────────────────────────

class EraSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(source="country.code", read_only=True)
    is_current   = serializers.ReadOnlyField()

    class Meta:
        model  = Era
        fields = [
            "id", "country_code", "name", "name_local",
            "era_type", "colonial_power",
            "started", "ended", "is_current",
            "notes", "source", "source_url",
        ]


# ── DIVISION NAME ─────────────────────────────────────────────────────────────

class DivisionNameSerializer(serializers.ModelSerializer):
    era_name    = serializers.CharField(source="era.name", read_only=True)
    era_type    = serializers.CharField(source="era.era_type", read_only=True)
    era_started = serializers.CharField(source="era.started", read_only=True)
    era_ended   = serializers.CharField(source="era.ended", read_only=True)

    class Meta:
        model  = DivisionName
        fields = [
            "id", "name", "language", "name_type",
            "era_name", "era_type", "era_started", "era_ended",
            "etymology", "notes", "source", "source_url",
        ]


# ── DIVISION LEVEL ────────────────────────────────────────────────────────────

class DivisionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DivisionLevel
        fields = ["level", "name", "name_sw"]


# ── COUNTRY ───────────────────────────────────────────────────────────────────

class CountrySerializer(serializers.ModelSerializer):
    division_levels = DivisionLevelSerializer(many=True, read_only=True)
    eras            = EraSerializer(many=True, read_only=True)

    class Meta:
        model  = Country
        fields = ["code", "name", "native_name", "max_levels", "division_levels", "eras"]


# ── DIVISION — BRIEF ──────────────────────────────────────────────────────────

class DivisionBriefSerializer(serializers.ModelSerializer):
    level_name = serializers.ReadOnlyField()

    class Meta:
        model  = Division
        fields = ["id", "name", "name_sw", "code", "level", "level_name"]


# ── DIVISION — LIST ───────────────────────────────────────────────────────────

class DivisionSerializer(serializers.ModelSerializer):
    level_name     = serializers.ReadOnlyField()
    country_code   = serializers.CharField(source="country.code",   read_only=True)
    country_name   = serializers.CharField(source="country.name",   read_only=True)
    parent         = DivisionBriefSerializer(read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model  = Division
        fields = [
            "id", "country_code", "country_name",
            "level", "level_name", "name", "name_sw",
            "code", "parent", "children_count",
            "native_id", "source",
        ]

    def get_children_count(self, obj):
        return obj.children.filter(is_active=True).count()


# ── DIVISION — DETAIL (includes historical names) ─────────────────────────────

class DivisionDetailSerializer(DivisionSerializer):
    children         = DivisionBriefSerializer(many=True, read_only=True)
    ancestors        = serializers.SerializerMethodField()
    historical_names = DivisionNameSerializer(many=True, read_only=True)
    name_in_year     = serializers.SerializerMethodField()

    class Meta(DivisionSerializer.Meta):
        fields = DivisionSerializer.Meta.fields + [
            "children", "ancestors",
            "historical_names", "name_in_year",
        ]

    def get_ancestors(self, obj):
        return DivisionBriefSerializer(obj.get_ancestors(), many=True).data

    def get_name_in_year(self, obj):
        """
        If ?year= query param is present, return the era-specific name.
        e.g. GET /api/v1/divisions/42/?year=1923
        """
        request = self.context.get("request")
        if not request:
            return None
        year = request.query_params.get("year")
        if not year:
            return None
        try:
            hn = obj.get_name_for_year(int(year))
            if hn:
                return DivisionNameSerializer(hn).data
        except (ValueError, TypeError):
            pass
        return None
