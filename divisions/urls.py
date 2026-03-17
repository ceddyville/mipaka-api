from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, DivisionViewSet, EraViewSet, DivisionNameViewSet

router = DefaultRouter()
router.register(r"countries", CountryViewSet,    basename="country")
router.register(r"divisions", DivisionViewSet,   basename="division")
router.register(r"eras",      EraViewSet,        basename="era")
router.register(r"names",     DivisionNameViewSet, basename="divisionname")

urlpatterns = router.urls
