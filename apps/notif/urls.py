from django.urls import path
from .views import (
    NotificationAPIView,
    NotifCreteView,
    NotifListView,
    NotifKindsApiView,
    NotifChangeStateApiView,
    NotifTypeView,
    NotifTypeListApiView,
    NotifTypeDeleteApiView,
    NotifInfoApiView,
)

urlpatterns = [
    path("create/", NotifCreteView.as_view(), name="notif-action"),
    path("list/", NotifListView.as_view(), name="notif-list"),
    path("choice/<int:kind>/", NotifKindsApiView.as_view(), name="notif-choices"),
    path('action/', NotificationAPIView.as_view()),
    path('action-read-count/', NotifInfoApiView.as_view(), name="action-read-count"),
    path('state/<str:pk>/', NotifChangeStateApiView.as_view()),

    path('type/', NotifTypeView.as_view(), name="notif-type"),
    path('type/<int:pk>/', NotifTypeView.as_view(), name="notif-type"),
    path('kind-delete/<int:pk>/', NotifTypeDeleteApiView.as_view(), name="notif-type-delete"),
    path('kind-list/', NotifTypeListApiView.as_view(), name="notif-type-list"),
]
