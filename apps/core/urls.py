from django.urls import path
from .views import (
    DownloadFile,
    HomeApiView,
    AttachmentAPIView,
    OrgToEmployeeJsonApiView,
    ComingEmpsApiView,

    leaveToVote,
    scheduleType,
    timetableList,
    orgregister,
    lineGraph,
    # forgotPassword,
    # signUp,
    newEmployeeOrientation,
    trainingPlanRegister,
    settings,
    commandDecisionRegister,
    putToWork,
    designation,
    humanResourceReport,
    kpiTypeRegister,
    toirohHuudas
)

urlpatterns = [
    path('', HomeApiView.as_view(), name='home'),

    path("coming-employees/", ComingEmpsApiView.as_view(), name="coming-emps"),

    path('download-attachment/', DownloadFile.as_view(), name="download-attachment"),
    path("attachments/<int:pk>/", AttachmentAPIView.as_view(), name='attachment'),
    path("helper/org-to-employee/", OrgToEmployeeJsonApiView.as_view(), name='org-to-employee'),

    path('leave-to-vote', leaveToVote, name='leave-to-vote'),
    path('schedule-type', scheduleType, name='schedule-type'),
    path('timetable-list', timetableList, name='timetable-list'),
    # path('org-register', orgregister, name='org-register'),
    path('line-graph', lineGraph, name='line-graph'),
    # path('forgot-password', forgotPassword, name='forgot-password'),
    # path('sign-up', signUp, name='sign-up'),
    path('new-employee-orientation', newEmployeeOrientation, name="new-employee-orientation"),
    path('training-plan-register', trainingPlanRegister, name='training-plan-register'),
    path('settings', settings, name='settings'),
    path('command-decision-register', commandDecisionRegister, name='command-decision-register'),
    path('put-to-work', putToWork, name='put-to-work'),
    path('designation', designation, name='designation'),
    path('human-resource-report', humanResourceReport, name='human-resource-report'),
    path('kpi-type-register', kpiTypeRegister, name='kpi-type-register'),
    path('toiroh-huudas', toirohHuudas, name='toiroh-huudas'),

]
