from django.urls import path

from .views import (
    KpiRegisterApiView,
    KpiRegisterOrgPositionApiView,
    RegisterJsonApiView,
    KpiRegisterAjaxAPIView,

    KpiAssessmentApiView,
    KpiAssessmentEmployeeJsonApiView,
    KpiAssessmentAjaxAPIView,
    EmployeeNameAjaxApiView,
    ReportApiView,
    KpiReportJsonApiView,
)

urlpatterns = [
    path('org-positions/', KpiRegisterOrgPositionApiView.as_view()),
    path('get-employee-name/<int:pk>/', EmployeeNameAjaxApiView.as_view()),

    path('register/', KpiRegisterApiView.as_view(), name="kpi-register"),
    path('register/<int:pk>/', KpiRegisterApiView.as_view(), name="kpi-register"),
    path('register-json/', RegisterJsonApiView.as_view(), name="register-json"),
    path('register-json/<int:pk>/', RegisterJsonApiView.as_view(), name="register-json"),
    path('register-ajax/<int:pk>/', KpiRegisterAjaxAPIView.as_view()),

    path('assessment/', KpiAssessmentApiView.as_view(), name="kpi-assessment"),
    path('assessment-employee-json/', KpiAssessmentEmployeeJsonApiView.as_view(), name="assessment-employee-json"),
    path('assessment-employee-json/<int:pk>/', KpiAssessmentEmployeeJsonApiView.as_view(), name="assessment-employee-json"),
    path('assessment-ajax/', KpiAssessmentAjaxAPIView.as_view()),
    path('assessment-ajax/<int:pk>/', KpiAssessmentAjaxAPIView.as_view()),

    path('report/', ReportApiView.as_view(), name='kpi-report'),
    path('report-json/', KpiReportJsonApiView.as_view(), name='kpi-report-json'),
]
