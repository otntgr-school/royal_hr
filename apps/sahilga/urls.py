from django.urls import path

from .views import (
    SahilgaApiView,
    SahilgaListApiView,
    SahilgaActionApiView,
    SahilgaEmployeeApiView,
    SahilgaOneApiView,
)

urlpatterns = [
    path('', SahilgaApiView.as_view(), name="sahilga"),
    path("list/", SahilgaListApiView.as_view(), name='sahilga-list'),

    path("action/", SahilgaActionApiView.as_view(), name='sahilga-action'),
    path("employee/<int:employee_id>/", SahilgaEmployeeApiView.as_view(), name='sahilga-employee'),
    path("detail/<int:pk>/", SahilgaListApiView.as_view(), name='sahilga-detail'),
    path("<str:state>/<int:pk>/", SahilgaEmployeeApiView.as_view(), name='sahilga-refuse'),
    path("sahilga-one/", SahilgaOneApiView.as_view())
]
