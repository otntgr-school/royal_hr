from django.urls import path
from .views import (
    IndexAPIView,
    FeedbackKindApiView,
    FeedbackKindDeleteApiView,
    FeedbackKindListApiView,
    FeedBackDatatableAPIView,
    FeedBackFormAPIView,
    FeedBackDecideAPIView,
    FeedBackAPIView,
    GetMyFeedBackAttachments,
    MyFeedBackDecideAPIView,
    GetMyFeedBackCommands,
    GetUpOrgsApiView,
    GetEmployeeLvlApiView,
)

urlpatterns = [
    path('', IndexAPIView.as_view(), name="sanal-gomdol"),

    path('kinds/', FeedbackKindApiView.as_view(), name="sanal-gomdol-turul"),
    path('kinds/<int:pk>/', FeedbackKindApiView.as_view(), name="sanal-gomdol-turul"),
    path('kind-delete/<int:pk>/', FeedbackKindDeleteApiView.as_view(), name="sanal-gomdol-turul-delete"),
    path('kind-list/', FeedbackKindListApiView.as_view(), name="sanal-gomdol-turul-list"),

    path('dt/', FeedBackDatatableAPIView.as_view(), name="sanal-gomdol-dt"),
    path('dt/<int:pk>/', FeedBackDatatableAPIView.as_view(), name="sanal-gomdol-dt"),
    path('action/', FeedBackFormAPIView.as_view(), name="sanal-gomdol-action"),
    path('action/<int:pk>/', FeedBackFormAPIView.as_view(), name="sanal-gomdol-action"),
    path('get-attachmets-gg/<int:pk>/', GetMyFeedBackAttachments.as_view()),
    path('get-commands/<int:pk>/', GetMyFeedBackCommands.as_view()),

    path('decide/', FeedBackDecideAPIView.as_view(), name="sanal-gomdol-decide"),
    path('my-decide/', MyFeedBackDecideAPIView.as_view(), name="my-feedback-decide"),
    path('decide-list/', FeedBackAPIView.as_view(), name="sanal-gomdol-decide-list"),
    path('decide-list/<int:pk>/', FeedBackAPIView.as_view(), name="sanal-gomdol-decide-list"),

    path('get-up-orgs/', GetUpOrgsApiView.as_view(), name="get-up-orgs"),
    path('get-employees-lvl/<str:pk>/', GetEmployeeLvlApiView.as_view())

]
