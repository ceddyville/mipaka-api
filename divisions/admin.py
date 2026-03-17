from django.contrib import admin
from .models import Country, DivisionLevel, Division, Era, DivisionName


class DivisionLevelInline(admin.TabularInline):
    model = DivisionLevel
    extra = 0


class EraInline(admin.TabularInline):
    model  = Era
    extra  = 0
    fields = ["name", "era_type", "colonial_power", "started", "ended"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "max_levels", "is_active"]
    list_filter  = ["is_active"]
    inlines      = [DivisionLevelInline, EraInline]


@admin.register(Era)
class EraAdmin(admin.ModelAdmin):
    list_display  = ["country", "name", "era_type", "colonial_power", "started", "ended"]
    list_filter   = ["era_type", "colonial_power", "country"]
    search_fields = ["name", "name_local", "notes"]
    ordering      = ["country", "started"]


class DivisionNameInline(admin.TabularInline):
    model  = DivisionName
    extra  = 0
    fields = ["era", "name", "language", "name_type", "etymology"]


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display  = ["name", "country", "level", "parent", "source", "is_active"]
    list_filter   = ["country", "level", "is_active", "source"]
    search_fields = ["name", "name_sw", "code"]
    raw_id_fields = ["parent"]
    inlines       = [DivisionNameInline]


@admin.register(DivisionName)
class DivisionNameAdmin(admin.ModelAdmin):
    list_display  = ["name", "division", "era", "language", "name_type"]
    list_filter   = ["name_type", "era__era_type", "era__colonial_power"]
    search_fields = ["name", "division__name", "era__name", "language", "etymology"]
    ordering      = ["era__started", "name"]
