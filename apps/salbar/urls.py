from django.urls import path
from .views import (
    HomeApiView,
    SubOrgSalbarApiView,
    SalbarApiView,
    SalbarDelete
)

urlpatterns = [
    path('salbar-list/', HomeApiView.as_view(), name='salbar-list'),
    path('salbar-list/<int:sub_org_id>/<str:action>/', HomeApiView.as_view(), name='salbar-0-list'),
    path('salbar-list/<int:sub_org_id>/<str:pk>/<str:action>/', HomeApiView.as_view(), name='salbar-list'),
    path('salbar-get/<int:pk>/', SalbarApiView.as_view()),
    path('salbar-register/', HomeApiView.as_view(), name='salbar-register'),
    path('salbar-0-register/<int:sub_org_id>/<str:action>/', HomeApiView.as_view(), name='salbar-0-register'),
    path('salbar-register/<str:pk>/<str:action>/', HomeApiView.as_view(), name='salbar-register'),
    path('salbar-delete/<str:pk>/', SalbarDelete.as_view(), name='salbar-delete'),

    path("sub-org-list/", SubOrgSalbarApiView.as_view())
]
