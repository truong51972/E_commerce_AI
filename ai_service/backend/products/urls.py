from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'product_record', views.ProductionVectorRecordViewSet, 'product_record')

urlpatterns = [
    path('', include(router.urls)),
    path("context_search_api", views.ContextSearchAPIView.as_view(), name="context_search_api"),
    path("agent_search_api", views.AgentSearchAPIView.as_view(), name="agent_search_api"),
]