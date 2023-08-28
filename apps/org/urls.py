from django.urls import path
from .views import (
    OrgAPIView,
    OrgDelete,
    OrgRegisterJsonAPIView,
    SuperUserChangeOrg,
    UserRegisterOrg,
    OrgSystemEmailApiView,
)

urlpatterns = [
    path('org-register/', OrgAPIView.as_view(), name="org-register"),
    path("org-system-email/", OrgSystemEmailApiView.as_view(), name="org-system-email"),
    path("org-system-email/<int:pk>/", OrgSystemEmailApiView.as_view(), name="org-system-email"),
    path('org-register/<int:pk>/', OrgAPIView.as_view(), name="org-register"),
    path('org-register/<int:pk>/org-user-register/', UserRegisterOrg.as_view(), name="org-user-register"),


    path('org-delete/<int:pk>/', OrgDelete.as_view(), name="org-delete"),
    path('org-superuser/<int:pk>/', SuperUserChangeOrg.as_view(), name="org-superuser"),
    path('org-info/<int:pk>/', OrgAPIView.as_view(), name="org-info"),
    path('org-info/', OrgAPIView.as_view(), name="org-info"),

    path('json/', OrgRegisterJsonAPIView.as_view(), name='orgRegisterJson'),
]
