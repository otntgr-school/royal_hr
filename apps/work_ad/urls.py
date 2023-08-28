from django.urls import path

from .views import (
    WorkAdsenseListApiView,
    UserWorkJoinRequest,
    MyJoinRequestsApiView,
    WorkAdsenseGetApiView,
    WorkJoinRequest,
    RequestedManApiView,
    WorkAdsenseRequestsApiView,
    WorkAdsensePaginate,
    CreateEmployeeApiView,

    WorkAdsenseApiView,
    WorkAdsenseCRUDApiView,
    WorkAdsensePaginateApiView,

    SendChigluulehApiView,
    GetChigluulehAPIView,
)

urlpatterns = [
    path('work-adsense-list/', WorkAdsenseListApiView.as_view(), name='work-adsense-list'),
    path('ads-my-request/<int:pk>/', UserWorkJoinRequest.as_view()),
    path('ads-my-requests/<str:state>/', UserWorkJoinRequest.as_view(), name="ads-my-requests"),

    path('my-join-requests/', MyJoinRequestsApiView.as_view(), name='my-join-requests'),

    path('work-adsense-get/', WorkAdsenseGetApiView.as_view(), name="work-adsense-get"),
    path('work-join-request/', WorkJoinRequest.as_view(), name="work-join-request"),

    path('work-adsense-requested/', RequestedManApiView.as_view(), name='work-adsense-requested'),
    path('work-adsense-request/', WorkAdsenseRequestsApiView.as_view(), name='work-adsense-request'),
    path('work-adsense-request-paginate/', WorkAdsensePaginate.as_view(), name="org-work-adsense-request-reject"),
    path('work-adsense-request-paginate/<str:state>/', WorkAdsensePaginate.as_view(), name="org-work-adsense-request-paginate"),

    path("send-chigluuleh/", SendChigluulehApiView.as_view(), name='send-chigluuleh'),
    path("create-employee-request/", CreateEmployeeApiView.as_view(), name='create-employee-request'),

    path('work-adsense/', WorkAdsenseApiView.as_view(), name="work-adsense"),
    path('work-adsense-crud/<int:pk>/', WorkAdsenseCRUDApiView.as_view()),
    path('work-adsense-crud/', WorkAdsenseCRUDApiView.as_view()),
    path('work-adsense-paginate/', WorkAdsensePaginateApiView.as_view(), name='org-work-adsense-paginate'),
    path("<int:pk>/chigluuleh/", GetChigluulehAPIView.as_view(), name='get-chigluuleh'),
]
