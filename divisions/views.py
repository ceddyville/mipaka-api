from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Country, Division, Era, DivisionName
from .serializers import (
    CountrySerializer,
    DivisionSerializer,
    DivisionDetailSerializer,
    EraSerializer,
    DivisionNameSerializer,
)
from .filters import DivisionFilter, DivisionNameFilter

CACHE_TTL = 60 * 60 * 24  # 24 hours


# ── COUNTRY ───────────────────────────────────────────────────────────────────

class CountryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    GET /api/v1/countries/              List all active countries (with eras)
    GET /api/v1/countries/UG/           Uganda detail
    GET /api/v1/countries/UG/top/       Level-1 divisions for Uganda
    GET /api/v1/countries/UG/eras/      All historical eras for Uganda
    """
    permission_classes = [AllowAny]
    queryset = (
        Country.objects
        .filter(is_active=True)
        .prefetch_related("division_levels", "eras")
    )
    serializer_class = CountrySerializer
    lookup_field = "code"

    @method_decorator(cache_page(CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="top")
    @method_decorator(cache_page(CACHE_TTL))
    def top_level(self, request, code=None):
        country = self.get_object()
        divisions = Division.objects.filter(
            country=country, level=1, is_active=True
        ).order_by("name")
        serializer = DivisionSerializer(divisions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="eras")
    @method_decorator(cache_page(CACHE_TTL))
    def eras(self, request, code=None):
        """Returns all historical eras for a country in chronological order."""
        country = self.get_object()
        eras = country.eras.all().order_by("started")
        return Response(EraSerializer(eras, many=True).data)


# ── ERA ───────────────────────────────────────────────────────────────────────

class EraViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    GET /api/v1/eras/                       All eras across all countries
    GET /api/v1/eras/?country=UG            Uganda eras
    GET /api/v1/eras/?era_type=colonial     All colonial eras
    GET /api/v1/eras/?colonial_power=belgian Belgian-controlled eras
    """
    permission_classes = [AllowAny]
    queryset = Era.objects.select_related("country").all()
    serializer_class = EraSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["era_type", "colonial_power"]
    search_fields = ["name", "name_local", "notes"]
    ordering_fields = ["started", "era_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        country = self.request.query_params.get("country")
        if country:
            qs = qs.filter(country__code__iexact=country)
        return qs


# ── DIVISION ──────────────────────────────────────────────────────────────────

class DivisionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    GET /api/v1/divisions/                          List with filters
    GET /api/v1/divisions/?country=UG&level=1       Ugandan regions
    GET /api/v1/divisions/?country=CD&level=2       DRC territories
    GET /api/v1/divisions/?parent=42                Children of division #42
    GET /api/v1/divisions/?q=kampala                Search by name
    GET /api/v1/divisions/?name=Léopoldville        Search incl. historical names
    GET /api/v1/divisions/?year=1923&country=CD     Divisions as named in 1923
    GET /api/v1/divisions/{id}/                     Detail + historical names
    GET /api/v1/divisions/{id}/?year=1923           Detail + name as of 1923
    GET /api/v1/divisions/{id}/children/            Direct children
    GET /api/v1/divisions/{id}/names/               All historical names
    """
    permission_classes = [AllowAny]
    queryset = (
        Division.objects
        .filter(is_active=True)
        .select_related("country", "parent")
        .prefetch_related("children", "historical_names__era")
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DivisionFilter
    search_fields = ["name", "name_sw", "code", "historical_names__name"]
    ordering_fields = ["name", "level"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DivisionDetailSerializer
        return DivisionSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()

        # ?name= searches both current and historical names
        name = self.request.query_params.get("name")
        if name:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=name) |
                Q(historical_names__name__icontains=name)
            ).distinct()

        # ?year= filters to divisions that existed in that year
        # and annotates which era they belonged to
        year = self.request.query_params.get("year")
        if year:
            try:
                y = int(year)
                # Return divisions that have at least one era covering this year
                from django.db.models import Q
                qs = qs.filter(
                    Q(historical_names__era__started__lte=str(y)) &
                    (Q(historical_names__era__ended__gte=str(y)) |
                     Q(historical_names__era__ended=""))
                ).distinct()
            except ValueError:
                pass

        return qs

    @method_decorator(cache_page(CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        division = self.get_object()
        qs = division.children.filter(is_active=True).order_by("name")
        return Response(DivisionSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"])
    def names(self, request, pk=None):
        """
        Returns all historical names for a division, sorted chronologically.
        GET /api/v1/divisions/42/names/
        GET /api/v1/divisions/42/names/?era_type=colonial
        GET /api/v1/divisions/42/names/?language=Luganda
        """
        division = self.get_object()
        qs = division.historical_names.select_related(
            "era").order_by("era__started")

        era_type = request.query_params.get("era_type")
        language = request.query_params.get("language")
        if era_type:
            qs = qs.filter(era__era_type=era_type)
        if language:
            qs = qs.filter(language__icontains=language)

        return Response(DivisionNameSerializer(qs, many=True).data)


# ── DIVISION NAME (global search) ─────────────────────────────────────────────

class DivisionNameViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Searchable index of all historical names across all divisions.

    GET /api/v1/names/                            All historical names
    GET /api/v1/names/?q=Léopoldville             Search historical names
    GET /api/v1/names/?era_type=colonial          All colonial-era names
    GET /api/v1/names/?country=CD                 DRC historical names
    GET /api/v1/names/?language=Luganda           Names in Luganda
    GET /api/v1/names/?name_type=indigenous       Pre-colonial indigenous names
    GET /api/v1/names/?year=1923                  Names active in 1923
    """
    permission_classes = [AllowAny]
    serializer_class = DivisionNameSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "etymology", "notes"]
    ordering_fields = ["era__started", "name"]

    def get_queryset(self):
        qs = DivisionName.objects.select_related(
            "division", "division__country", "era"
        ).all()

        q = self.request.query_params.get("q")
        country = self.request.query_params.get("country")
        era_type = self.request.query_params.get("era_type")
        language = self.request.query_params.get("language")
        name_type = self.request.query_params.get("name_type")
        year = self.request.query_params.get("year")

        if q:
            qs = qs.filter(name__icontains=q)
        if country:
            qs = qs.filter(division__country__code__iexact=country)
        if era_type:
            qs = qs.filter(era__era_type=era_type)
        if language:
            qs = qs.filter(language__icontains=language)
        if name_type:
            qs = qs.filter(name_type=name_type)
        if year:
            try:
                from django.db.models import Q as DQ
                y = int(year)
                qs = qs.filter(
                    era__started__lte=str(y)
                ).filter(
                    DQ(era__ended__gte=str(y)) | DQ(era__ended="")
                )
            except ValueError:
                pass
        return qs
