from django.urls import path
from apps.schedule import views

urlpatterns = [
    # Ажлийн цагийн төрөл
    path('work-time-type/', views.WorkTimeTypeAPIView.as_view(), name='work-time-type'),
    path('work-time-type/<int:pk>/', views.WorkTimeTypeAPIView.as_view(), name='work-time-type'),
    path('work-time-type-ajax/<int:pk>/', views.WorkTimeTypeAjaxAPIView.as_view()),
    path('work-time-type-json/', views.WorkTimeTypeJson.as_view(), name='work-time-type-json'),

    # Цагийн хуваарийн төрөл
    path('working-time-schedule/', views.WorkingTimeScheduleAPIView.as_view(), name='working-time-schedule'),
    path('working-time-schedule/<int:pk>/', views.WorkingTimeScheduleAPIView.as_view(), name='working-time-schedule'),
    path('working-time-schedule-ajax/<int:pk>/', views.WorkingTimeScheduleAjaxAPIView.as_view()),
    path('working-time-schedule-json/', views.WorkingTimeScheduleJson.as_view(), name='working-time-schedule-json'),
    path('working-time-schedule-registered-employee-json/', views.WorkingTimeScheduleRegisteredEmployeeJson.as_view(), name='working-time-schedule-registered-employee-json'),
    path('working-time-schedule-not-registered-employee-json/', views.WorkingTimeScheduleNotRegisteredEmployeeJson.as_view(), name='working-time-schedule-not-registered-employee-json'),
    path('working-time-schedule-employee-remove/<int:pk>/', views.WorkingTimeScheduleAjaxEmployeeRemoveAPIView.as_view()),
    path('working-time-schedule-employee-add/<int:pk>/', views.WorkingTimeScheduleAjaxEmployeeAddAPIView.as_view()),

    path('working-time-schedule-employee-xy-add/<int:pk>/', views.WorkingTimeScheduleAjaxEmployeeXyAddAPIView.as_view()),

    # Цаг бүртгэл
    path('time-schedule-register/', views.TimeScheduleRegisterAPIView.as_view(), name='time-schedule-register'),
    path('time-schedule-register/<int:pk>/<str:type>/', views.TimeScheduleRegisterAPIView.as_view(), name='time-schedule-register'),
    path('time-schedule-register-out', views.TimeScheduleRegisterOutAPIView.as_view(), name='time-schedule-register-out'),
    path('time-schedule-register-ajax/<int:pk>/', views.TimeScheduleRegisterAjaxAPIView.as_view()),
    path('time-schedule-register-json/', views.TimeScheduleJson.as_view(), name='time-schedule-register-json'),
    path('time-schedule-register/change-order/', views.TimeScheduleOrder.as_view(), name='time-schedule-register-order'),

    # Хүсэлт илгээх
    path('time-register-request/', views.TimeRegisterRequestAPIView.as_view(), name='time-register-request'),
    path('time-register-request-org-pos/<int:pk>/<int:req_id>/', views.TimeRegisterRequestOrgPosAPIView.as_view(), name='time-register-request-org-pos'),
    path('time-register-request-json/', views.TimeRegisterRequestJson.as_view(), name='time-register-request-json'),
    path('time-register-request-check-date/', views.TimeRegisterRequestCheckDate.as_view(), name='time-register-request-json-check-date'),
    path('time-register-request-print/<int:pk>/', views.TimeRegisterRequestPrintAPIView.as_view(), name='time-register-request-print'),

    # Хүсэлт шийдвэрлэх
    path('time-register-request-solve/', views.TimeRegisterRequestSolveAPIView.as_view(), name='time-register-request-solve'),
    path('time-register-request-decline/<int:pk>/', views.TimeRegisterRequestDeclineAPIView.as_view()),
    path('time-register-request-agree/<int:pk>/', views.TimeRegisterRequestAgreeAPIView.as_view()),
    path('time-register-request-user-waiting-json/', views.TimeRegisterRequestUserWaitingJson.as_view(), name='time-register-request-user-waiting-json'),
    path('time-register-request-ended-json/', views.TimeRegisterRequestUserEndedJson.as_view(), name='time-register-request-ended-json'),
    path('time-register-request-waiting-json/', views.TimeRegisterRequestWaitingJson.as_view(), name='time-register-request-waiting-json'),

    path('time-register-request-org-pos-agree/<int:pk>/', views.TimeRegisterRequestOrgPosAgreeAPIView.as_view()),
    path('time-register-request-org-pos-decline/<int:pk>/', views.TimeRegisterRequestOrgPosDeclineAPIView.as_view()),

    # Шинээр байгууллага үүсгэх
    path('create-vacation-type/', views.CreateVacationTypeAPIView.as_view(), name='create-vacation-type'),
    path('create-vacation-type-ajax/<int:pk>/', views.OrgVacationTypesAjaxAPIView.as_view(), name='create-vacation-type-ajax'),
    path('create-vacation-type-json/', views.CreateVacationTypeJson.as_view(), name='create-vacation-type-json'),
    path('create-vacation-reason-json/', views.CreateVacationReasonJson.as_view(), name='create-vacation-reason-json'),
    path('create-vacation-reason-draggable/', views.CreateVacationReasonDraggableJson.as_view(), name='create-vacation-reason-draggable'),
    path('create-vacation-reason-ajax/<int:pk>/', views.CreateVacationReasonAjaxAPIView.as_view(), name='create-vacation-reason-ajax'),
    path('create-vacation-reason-ajax/', views.CreateVacationReasonAjaxAPIView.as_view(), name='create-vacation-reason-ajax'),

    # Цаг бүртгэлийн ажилтны тайлан
    path('time-register-report/', views.TimeRegisterReportAPIView.as_view(), name='time-register-report'),
    path('time-register-report/<int:pk>/', views.TimeRegisterReportAPIView.as_view(), name='time-register-report'),
    path('time-register-report-ajax/', views.TimeRegisterReportAjaxAPIView.as_view(), name='time-register-report-ajax'),
    path('time-register-report-employee-json/', views.TimeRegisterReportEmployeeAPIView.as_view(), name='time-register-report-employee-json'),

    # Автомат цагийн баланс
    path('auto-time-balance/', views.AutoTimeBalanceAPIView.as_view(), name='auto-time-balance'),
    path('auto-time-balance-seven-ajax/', views.AutoTimeBalanceSevenAjaxAPIView.as_view(), name='auto-time-balance-seven-ajax'),

    # Тусгай баярын ажлын өдрүүд
    path('special-leave/', views.SpecialLeaveAPIView.as_view(), name='special-leave'),
    path('special-leave-every-year-json/', views.SpecialLeaveEveryYearJson.as_view(), name='special-leave-every-year-json'),
    path('special-leave-every-ajax/<int:pk>/', views.SpecialLeaveEveryYearAjaxAPIView.as_view(), name='special-leave-every-ajax'),
    path('special-leave-every-ajax/', views.SpecialLeaveEveryYearAjaxAPIView.as_view(), name='special-leave-every-ajax'),

    path('special-leave-chosed-year-json/', views.SpecialLeaveChosedYearJsonAPIView.as_view(), name='special-leave-chosed-year-json'),
    path('special-leave-chosed-year-ajax/', views.SpecialLeaveChosedYearAjaxAPIView.as_view(), name='special-leave-chosed-year-ajax'),
    path('special-leave-chosed-year-ajax/<int:pk>/', views.SpecialLeaveChosedYearAjaxAPIView.as_view(), name='special-leave-chosed-year-ajax'),

    # Ээлжийн амралт
    path('vacation/', views.Vacation.as_view(), name='vacation'),
    path('year-vacation/', views.YearVacationAPIView.as_view(), name='year-vacation'),
    path('year-vacation-cancel/', views.YearVacationCancelAPIView.as_view(), name='year-vacation-cancel'),
    path('year-vacation-json/', views.YearVacationJson.as_view(), name='year-vacation-json'),

    # Ээлжийн амралт шийдвэрлэх
    path('year-vacation-deciding/', views.YearVacationDecidingAPIView.as_view(), name='year-vacation-deciding'),
    path('year-vacation-deciding-json/', views.YearVacationDecidingJson.as_view(), name='year-vacation-deciding-json'),
    path('year-vacation-deciding-decline/', views.YearVacationDeclineAPIView.as_view(), name='year-vacation-deciding-decline'),
    path('year-vacation-deciding-approve/', views.YearVacationApproveAPIView.as_view(), name='year-vacation-deciding-approve'),
]
