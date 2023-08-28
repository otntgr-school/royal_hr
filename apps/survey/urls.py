from django.urls import path
from .views import (
    BoglohListApiView,
    BoglosonApiView,

    SurveyTemplateView,
    SurveyActionApiView,
    PolleeTemplateView,
    SurveyListApiView,
    SurveyRejectApiView,
    SurveyImageApiView,
    PollesQuestionApiView,
    SurveyDeleteQuestion,
    SurveyDeleteChoice,
)

urlpatterns = [
    path('', SurveyTemplateView.as_view(), name="survey"),
    path('list/', SurveyListApiView.as_view(), name="survey-list"),
    path('list/<int:pk>/', SurveyListApiView.as_view(), name="survey-list"),
    path('create/', SurveyActionApiView.as_view(), name="survey-action"),
    path('pollee/', PolleeTemplateView.as_view(), name="pollee"),
    path('image/<int:survey_id>/', SurveyImageApiView.as_view(), name="pollee"),
    path("reject/", SurveyRejectApiView.as_view(), name="survey-reject"),
    path("update/<int:pk>/", SurveyActionApiView.as_view(), name="survey-update"),
    path("delete-question/<int:pk>/", SurveyDeleteQuestion.as_view(), name="delete-question"),
    path("delete-choice/<int:pk>/", SurveyDeleteChoice.as_view(), name="delete-choice"),
    path("update/<int:pk>/", SurveyActionApiView.as_view(), name="survey-update"),

    path('boglohList/', BoglohListApiView.as_view()),
    path('question/<int:pk>/', BoglohListApiView.as_view()),
    path('bogloson/<int:pk>/', BoglosonApiView.as_view()),
    path('<int:pk>/pollees/', PollesQuestionApiView.as_view()),
]
