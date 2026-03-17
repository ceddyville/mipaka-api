import django_filters
from .models import Division, DivisionName


class DivisionFilter(django_filters.FilterSet):
    country     = django_filters.CharFilter(field_name="country__code",    lookup_expr="iexact")
    level       = django_filters.NumberFilter(field_name="level")
    parent      = django_filters.NumberFilter(field_name="parent__id")
    parent_name = django_filters.CharFilter(field_name="parent__name",     lookup_expr="icontains")
    q           = django_filters.CharFilter(field_name="name",             lookup_expr="icontains")
    code        = django_filters.CharFilter(field_name="code",             lookup_expr="iexact")

    class Meta:
        model  = Division
        fields = ["country", "level", "parent", "q", "code"]


class DivisionNameFilter(django_filters.FilterSet):
    country   = django_filters.CharFilter(field_name="division__country__code", lookup_expr="iexact")
    era_type  = django_filters.CharFilter(field_name="era__era_type",           lookup_expr="iexact")
    language  = django_filters.CharFilter(field_name="language",                lookup_expr="icontains")
    name_type = django_filters.CharFilter(field_name="name_type",               lookup_expr="iexact")
    q         = django_filters.CharFilter(field_name="name",                    lookup_expr="icontains")

    class Meta:
        model  = DivisionName
        fields = ["country", "era_type", "language", "name_type", "q"]
