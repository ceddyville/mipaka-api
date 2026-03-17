import pytest
from rest_framework.test import APIClient

from divisions.models import Country, DivisionLevel, Division, Era, DivisionName


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def kenya(db):
    country = Country.objects.create(code="KE", name="Kenya", max_levels=3)
    DivisionLevel.objects.create(country=country, level=1, name="County")
    DivisionLevel.objects.create(country=country, level=2, name="Constituency")
    DivisionLevel.objects.create(country=country, level=3, name="Ward")
    return country


@pytest.fixture
def uganda(db):
    country = Country.objects.create(code="UG", name="Uganda", max_levels=6)
    DivisionLevel.objects.create(country=country, level=1, name="Region")
    DivisionLevel.objects.create(country=country, level=2, name="District")
    return country


@pytest.fixture
def nairobi(kenya):
    return Division.objects.create(
        country=kenya, level=1, name="Nairobi", code="047",
    )


@pytest.fixture
def westlands(kenya, nairobi):
    return Division.objects.create(
        country=kenya, level=2, name="Westlands",
        parent=nairobi,
    )


@pytest.fixture
def karura(kenya, westlands):
    return Division.objects.create(
        country=kenya, level=3, name="Karura",
        parent=westlands,
    )


@pytest.fixture
def colonial_era(kenya):
    return Era.objects.create(
        country=kenya,
        name="British East Africa",
        era_type="colonial",
        colonial_power="british",
        started="1895",
        ended="1963",
    )


@pytest.fixture
def current_era(kenya):
    return Era.objects.create(
        country=kenya,
        name="Republic of Kenya",
        era_type="current",
        started="1963",
        ended="",
    )


@pytest.fixture
def historical_name(nairobi, colonial_era):
    return DivisionName.objects.create(
        division=nairobi,
        era=colonial_era,
        name="Nairobi Township",
        language="English",
        name_type="colonial",
        etymology="Railway depot established 1899",
    )


# ── Health ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_health(api):
    r = api.get("/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["api"] == "mipaka"


# ── Countries ─────────────────────────────────────────────────────────────────

class TestCountries:

    @pytest.mark.django_db
    def test_list(self, api, kenya):
        r = api.get("/api/v1/countries/")
        assert r.status_code == 200
        data = r.json()["results"]
        assert len(data) == 1
        assert data[0]["code"] == "KE"

    @pytest.mark.django_db
    def test_list_excludes_inactive(self, api, kenya):
        Country.objects.create(code="XX", name="Inactive", is_active=False)
        r = api.get("/api/v1/countries/")
        codes = [c["code"] for c in r.json()["results"]]
        assert "XX" not in codes

    @pytest.mark.django_db
    def test_retrieve(self, api, kenya):
        r = api.get("/api/v1/countries/KE/")
        assert r.status_code == 200
        assert r.json()["name"] == "Kenya"
        assert len(r.json()["division_levels"]) == 3

    @pytest.mark.django_db
    def test_retrieve_not_found(self, api, kenya):
        r = api.get("/api/v1/countries/ZZ/")
        assert r.status_code == 404

    @pytest.mark.django_db
    def test_top_level(self, api, kenya, nairobi, westlands):
        r = api.get("/api/v1/countries/KE/top/")
        assert r.status_code == 200
        names = [d["name"] for d in r.json()]
        assert "Nairobi" in names
        assert "Westlands" not in names  # level 2, not included

    @pytest.mark.django_db
    def test_eras(self, api, kenya, colonial_era, current_era):
        r = api.get("/api/v1/countries/KE/eras/")
        assert r.status_code == 200
        assert len(r.json()) == 2


# ── Eras ──────────────────────────────────────────────────────────────────────

class TestEras:

    @pytest.mark.django_db
    def test_list(self, api, colonial_era, current_era):
        r = api.get("/api/v1/eras/")
        assert r.status_code == 200
        assert r.json()["count"] == 2

    @pytest.mark.django_db
    def test_retrieve(self, api, colonial_era):
        r = api.get(f"/api/v1/eras/{colonial_era.pk}/")
        assert r.status_code == 200
        assert r.json()["name"] == "British East Africa"
        assert r.json()["country_code"] == "KE"

    @pytest.mark.django_db
    def test_filter_by_era_type(self, api, colonial_era, current_era):
        r = api.get("/api/v1/eras/?era_type=colonial")
        results = r.json()["results"]
        assert len(results) == 1
        assert results[0]["era_type"] == "colonial"

    @pytest.mark.django_db
    def test_filter_by_country(self, api, colonial_era, uganda):
        Era.objects.create(
            country=uganda, name="Uganda Protectorate",
            era_type="colonial", started="1894", ended="1962",
        )
        r = api.get("/api/v1/eras/?country=UG")
        results = r.json()["results"]
        assert len(results) == 1
        assert results[0]["country_code"] == "UG"

    @pytest.mark.django_db
    def test_is_current_flag(self, api, current_era):
        r = api.get(f"/api/v1/eras/{current_era.pk}/")
        assert r.json()["is_current"] is True


# ── Divisions ─────────────────────────────────────────────────────────────────

class TestDivisions:

    @pytest.mark.django_db
    def test_list(self, api, nairobi):
        r = api.get("/api/v1/divisions/")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    @pytest.mark.django_db
    def test_list_excludes_inactive(self, api, kenya):
        Division.objects.create(country=kenya, level=1,
                                name="Ghost", is_active=False)
        r = api.get("/api/v1/divisions/")
        names = [d["name"] for d in r.json()["results"]]
        assert "Ghost" not in names

    @pytest.mark.django_db
    def test_filter_by_country(self, api, nairobi, uganda):
        Division.objects.create(country=uganda, level=1, name="Central")
        r = api.get("/api/v1/divisions/?country=KE")
        results = r.json()["results"]
        assert all(d["country_code"] == "KE" for d in results)

    @pytest.mark.django_db
    def test_filter_by_level(self, api, nairobi, westlands):
        r = api.get("/api/v1/divisions/?level=2")
        results = r.json()["results"]
        assert all(d["level"] == 2 for d in results)

    @pytest.mark.django_db
    def test_filter_by_parent(self, api, nairobi, westlands, karura):
        r = api.get(f"/api/v1/divisions/?parent={nairobi.pk}")
        names = [d["name"] for d in r.json()["results"]]
        assert "Westlands" in names
        assert "Karura" not in names  # grandchild, not direct child

    @pytest.mark.django_db
    def test_filter_by_q(self, api, nairobi, westlands):
        r = api.get("/api/v1/divisions/?q=west")
        results = r.json()["results"]
        assert any(d["name"] == "Westlands" for d in results)

    @pytest.mark.django_db
    def test_filter_by_name_historical(self, api, nairobi, historical_name):
        r = api.get("/api/v1/divisions/?name=Township")
        results = r.json()["results"]
        assert any(d["name"] == "Nairobi" for d in results)

    @pytest.mark.django_db
    def test_filter_by_year(self, api, nairobi, historical_name):
        r = api.get("/api/v1/divisions/?year=1920")
        results = r.json()["results"]
        assert any(d["name"] == "Nairobi" for d in results)

    @pytest.mark.django_db
    def test_retrieve_detail(self, api, nairobi, westlands, historical_name):
        r = api.get(f"/api/v1/divisions/{nairobi.pk}/")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Nairobi"
        assert data["level_name"] == "County"
        assert len(data["children"]) >= 1
        assert len(data["ancestors"]) == 0  # top-level, no ancestors

    @pytest.mark.django_db
    def test_retrieve_with_ancestors(self, api, karura):
        r = api.get(f"/api/v1/divisions/{karura.pk}/")
        ancestors = r.json()["ancestors"]
        assert len(ancestors) == 2  # Nairobi → Westlands
        assert ancestors[0]["name"] == "Nairobi"
        assert ancestors[1]["name"] == "Westlands"

    @pytest.mark.django_db
    def test_retrieve_year_param(self, api, nairobi, historical_name):
        r = api.get(f"/api/v1/divisions/{nairobi.pk}/?year=1920")
        data = r.json()
        assert data["name_in_year"]["name"] == "Nairobi Township"

    @pytest.mark.django_db
    def test_children_action(self, api, nairobi, westlands, karura):
        r = api.get(f"/api/v1/divisions/{nairobi.pk}/children/")
        assert r.status_code == 200
        names = [d["name"] for d in r.json()]
        assert "Westlands" in names
        assert "Karura" not in names

    @pytest.mark.django_db
    def test_names_action(self, api, nairobi, historical_name):
        r = api.get(f"/api/v1/divisions/{nairobi.pk}/names/")
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["name"] == "Nairobi Township"

    @pytest.mark.django_db
    def test_names_filter_era_type(self, api, nairobi, historical_name, current_era):
        DivisionName.objects.create(
            division=nairobi, era=current_era,
            name="Nairobi City", language="English", name_type="official",
        )
        r = api.get(f"/api/v1/divisions/{nairobi.pk}/names/?era_type=colonial")
        assert len(r.json()) == 1
        assert r.json()[0]["name"] == "Nairobi Township"

    @pytest.mark.django_db
    def test_children_count(self, api, nairobi, westlands):
        r = api.get("/api/v1/divisions/")
        nairobi_data = next(d for d in r.json()[
                            "results"] if d["name"] == "Nairobi")
        assert nairobi_data["children_count"] == 1

    @pytest.mark.django_db
    def test_not_found(self, api, kenya):
        r = api.get("/api/v1/divisions/999999/")
        assert r.status_code == 404


# ── Division Names (global search) ───────────────────────────────────────────

class TestDivisionNames:

    @pytest.mark.django_db
    def test_list(self, api, historical_name):
        r = api.get("/api/v1/names/")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    @pytest.mark.django_db
    def test_filter_by_q(self, api, historical_name):
        r = api.get("/api/v1/names/?q=Township")
        results = r.json()["results"]
        assert len(results) == 1

    @pytest.mark.django_db
    def test_filter_by_country(self, api, historical_name, uganda):
        r = api.get("/api/v1/names/?country=KE")
        results = r.json()["results"]
        assert len(results) == 1
        r2 = api.get("/api/v1/names/?country=UG")
        assert r2.json()["count"] == 0

    @pytest.mark.django_db
    def test_filter_by_era_type(self, api, historical_name):
        r = api.get("/api/v1/names/?era_type=colonial")
        results = r.json()["results"]
        assert len(results) == 1

    @pytest.mark.django_db
    def test_filter_by_language(self, api, historical_name):
        r = api.get("/api/v1/names/?language=English")
        results = r.json()["results"]
        assert len(results) >= 1

    @pytest.mark.django_db
    def test_filter_by_name_type(self, api, historical_name):
        r = api.get("/api/v1/names/?name_type=colonial")
        results = r.json()["results"]
        assert len(results) == 1

    @pytest.mark.django_db
    def test_filter_by_year(self, api, historical_name):
        r = api.get("/api/v1/names/?year=1920")
        results = r.json()["results"]
        assert len(results) == 1

    @pytest.mark.django_db
    def test_year_outside_range(self, api, historical_name):
        r = api.get("/api/v1/names/?year=1800")
        assert r.json()["count"] == 0


# ── OpenAPI Schema ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_schema_endpoint(api):
    r = api.get("/api/schema/")
    assert r.status_code == 200
    assert b"openapi" in r.content


@pytest.mark.django_db
def test_swagger_ui(api):
    r = api.get("/api/docs/")
    assert r.status_code == 200


@pytest.mark.django_db
def test_redoc(api):
    r = api.get("/api/redoc/")
    assert r.status_code == 200


# ── Pagination ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_pagination_structure(api, kenya):
    for i in range(3):
        Division.objects.create(country=kenya, level=1, name=f"County {i}")
    r = api.get("/api/v1/divisions/")
    data = r.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] == 3


# ── Read-only enforcement ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestReadOnly:

    def test_post_countries(self, api, kenya):
        r = api.post("/api/v1/countries/", {"code": "TZ", "name": "Tanzania"})
        assert r.status_code == 405

    def test_put_country(self, api, kenya):
        r = api.put("/api/v1/countries/KE/", {"name": "Kenya2"})
        assert r.status_code == 405

    def test_delete_country(self, api, kenya):
        r = api.delete("/api/v1/countries/KE/")
        assert r.status_code == 405

    def test_post_divisions(self, api, nairobi):
        r = api.post("/api/v1/divisions/", {"name": "Bad"})
        assert r.status_code == 405

    def test_delete_division(self, api, nairobi):
        r = api.delete(f"/api/v1/divisions/{nairobi.pk}/")
        assert r.status_code == 405

    def test_post_eras(self, api, colonial_era):
        r = api.post("/api/v1/eras/", {"name": "Bad"})
        assert r.status_code == 405

    def test_post_names(self, api, historical_name):
        r = api.post("/api/v1/names/", {"name": "Bad"})
        assert r.status_code == 405
