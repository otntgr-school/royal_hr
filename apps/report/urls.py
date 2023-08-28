from django.urls import path

from .views import *

urlpatterns = [
    path('urgudul/', ReportUrgudulApiView.as_view(), name='report-urgudul'),
    path('urgudul/dt/', ReportUrgudulDTApiView.as_view(), name='report-urgudul-dt'),

    # Хүний нөөцийн захиалгын хуудас
    path('order-form/', HrOrderFormApiView.as_view(), name='order-form'),
    path('order-form-create-json/', HrOrderFormCreateJsonApiView.as_view(), name='order-form-create-json'),
    path('order-form-create/', HrOrderFormCreateApiView.as_view(), name='order-form-create'),
    path('order-form-create-action/', HrOrderFormCreateActionApiView.as_view(), name='order-form-create-action'),
    path('order-form-create-action/<int:pk>/', HrOrderFormCreateActionApiView.as_view(), name='order-form-create-action'),
    path('order-form-answer-json/', HrOrderFormAnswerJsonApiView.as_view(), name='order-form-answer-json'),

    # Зөрчил
    path('violation-registration/', ViolationRegistrationApiView.as_view(), name='violation-registration'),
    path('violation-registration-action/', ViolationRegistrationActionApiView.as_view(), name='violation-registration-action'),
    path('violation-registration-action/<int:pk>/', ViolationRegistrationActionApiView.as_view(), name='violation-registration-action'),
    path('violation-registration-json/', ViolationRegistrationJsonApiView.as_view(), name='violation-registration-json'),
    path('violation-registration-list/', ViolationRegistrationListApiView.as_view(), name='violation-registration-list'),
    path('violation-registration-list-json/', ViolationRegistrationListJsonApiView.as_view(), name='violation-registration-list-json'),

    # Ажилтны сахилгын шийтгэлийн тухай тэмдэглэл
    path('note-on-disciplinary/', NoteOnDisciplinaryApiView.as_view(), name='note-on-disciplinary'),
]
