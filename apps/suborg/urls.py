from django.urls import path
from apps.suborg import views

urlpatterns = [
    path('sub-company-register/', views.SubCompanyRegisterAPIView.as_view(), name="sub-company-register"),
    path('sub-company-register/<int:pk>/', views.SubCompanyRegisterAPIView.as_view(), name="sub-company-register"),
    path('suborg-delete/<int:pk>/', views.SubOrgDeleteApiView.as_view(), name="suborg-delete"),
    path('json/', views.SubCompanyRegisterJsonApiView.as_view(), name='subCompanyRegisterJson'),

    path('user-list-json/', views.UserListTableJsonApiView.as_view(), name='user-list-json')
]
