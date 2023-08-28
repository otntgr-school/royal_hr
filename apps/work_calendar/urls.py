from django.urls import path

from .views import (
    IndexApiView,
    WorkCalendarKindsApiView,
    WorkCalendarKindListApiView,
    WorkCalendarKindDeleteApiView,
    WorkCalendarFormAPIView,
    WorkCalendarEmployeeAPIView,
    WorkTodayApiView
)

urlpatterns = [
    path('', IndexApiView.as_view(), name="work-calendar"),

    path('kinds/', WorkCalendarKindsApiView.as_view(), name="work-calendar-kinds"),
    path('kinds/<int:pk>/', WorkCalendarKindsApiView.as_view(), name="work-calendar-kinds"),
    path('kind-delete/<int:pk>/', WorkCalendarKindDeleteApiView.as_view(), name="work-calendar-kind-delete"),
    path('kind-list/', WorkCalendarKindListApiView.as_view(), name="work-calendar-kind-list"),

    path('employee/<int:pk>/', WorkCalendarEmployeeAPIView.as_view(), name="work-calendar-employee"),

    path("today/", WorkTodayApiView.as_view(), name="work-today"),

    path('create/', WorkCalendarFormAPIView.as_view(), name="work-calendar-form"),
    path('list/', WorkCalendarFormAPIView.as_view(), name="work-calendar-list"),
    path('<int:pk>/', WorkCalendarFormAPIView.as_view(), name="work-calendar-form"),

]
