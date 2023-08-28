from django.urls import path
from .views import (
    FAQPageApiView,
    FAQHTMLApiView,
    FAQActionApiView,
    FAQGroupPaginate,

    FAQuestionHTMLApiView,
    FAQuestionActionApiView,
    FAQuestionPaginate,

    FAQListApi,
)
urlpatterns = [
    path("", FAQPageApiView.as_view(), name='faq'),
    path("faq-html/", FAQHTMLApiView.as_view(), name='faq-action'),
    path("faq-action/", FAQActionApiView.as_view()),
    path("faq-action/<int:pk>/", FAQActionApiView.as_view()),
    path("faq-paginate/", FAQGroupPaginate.as_view()),

    path("faq-question-html/", FAQuestionHTMLApiView.as_view(), name='faq-question-action'),
    path("faq-question-action/", FAQuestionActionApiView.as_view()),
    path("faq-question-action/<int:pk>/", FAQuestionActionApiView.as_view()),
    path("faq-question-paginate/", FAQuestionPaginate.as_view()),

    path("faq-list/", FAQListApi.as_view()),
]
