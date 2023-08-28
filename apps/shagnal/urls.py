from django.urls import path

from .views import (
    StaticShagnalApiView,
    StaticShagnalListApiView,
    StaticShagnalDeleteApiView,
    StaticShagnalChangeOrder,

    DynamicShagnalApiView,
    DynamicShagnalListApiView,
    DynamicShagnalDeleteApiView,
    DynamicShagnalChangeOrder,

    ShagnalToEmployeeAPiView,
    ShagnalToEmployeeFormAPiView,

    ShagnalTailanApiView,
    ShagnalTailanHTML,
    ShagnalList
)

urlpatterns = [
    path('', ShagnalToEmployeeAPiView.as_view(), name="shagnal-to-employee"),
    path('set/', ShagnalToEmployeeFormAPiView.as_view(), name="shagnal-set-employee"),

    path('static/', StaticShagnalApiView.as_view(), name="static-shagnal"),
    path('static/change-order/', StaticShagnalChangeOrder.as_view(), name="static-shagnal-change-order"),
    path('static/<int:pk>/', StaticShagnalApiView.as_view(), name="static-shagnal"),
    path('static-delete/<int:pk>/', StaticShagnalDeleteApiView.as_view(), name="static-shagnal-delete"),
    path('static-list/', StaticShagnalListApiView.as_view(), name="static-shagnal-list"),

    path('dynamic/', DynamicShagnalApiView.as_view(), name="dynamic-shagnal"),
    path('dynamic/change-order/', DynamicShagnalChangeOrder.as_view(), name="dynamic-shagnal-change-order"),
    path('dynamic/<int:pk>/', DynamicShagnalApiView.as_view(), name="dynamic-shagnal"),
    path('dynamic-delete/<int:pk>/', DynamicShagnalDeleteApiView.as_view(), name="dynamic-shagnal-delete"),
    path('dynamic-list/', DynamicShagnalListApiView.as_view(), name="dynamic-shagnal-list"),

    path("shagnal-tailan-html/", ShagnalTailanHTML.as_view(), name='shagnal-tailan'),
    path("shagnal-tailan/", ShagnalTailanApiView.as_view()),
    path("all-shagnal-list/", ShagnalList.as_view()),
]
