from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'product_record', views.ProductionVectorRecordViewSet, 'product_record')

urlpatterns = [
    path('', include(router.urls)),
    path("quick_search", views.QuickSearchAPIView.as_view(), name="quick_search"),
    path("ai_search", views.AiSearchAPIView.as_view(), name="ai_search"),
    path("ai_search_with_context", views.AiSearchWithContextAPIView.as_view(), name="ai_search_with_context"),
]