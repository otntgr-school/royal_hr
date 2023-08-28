from django.urls import path
from .views import *

urlpatterns = [
    path('pagination/<str:state>/', WorkerPaginationApiView.as_view()),
    path('command/<int:pk>/', CommandInfoPaginationViews.as_view()),
    path('worker-list/', WorkerListAPIView.as_view(), name="worker-list"),
    path('worker-list/<int:pk>/', CommandAPIView.as_view(), name="command-list"),
    path('<int:pk>/', WorkerApiView.as_view()),

    path('donation/', DonationHTMLAPIView.as_view(), name="donation"),
    path('donations/', DonationList.as_view()),
    path('donations/<int:pk>/', DonationDetail.as_view()),

    path('fortomilolt/', ForTomiloltAPIView.as_view(), name="fortomilolt"),
    path('fortomiloltcrud/', ForTomiloltCRApiView.as_view()),
    path('fortomiloltcrud/<int:pk>/', ForTomiloltCRApiView.as_view()),

    path('designation/', TomiloltAPIView.as_view(), name="designation"),
    path('designationcrud/', TomiloltCRUDApiView.as_view()),
    path('designation-attachments/<int:pk>/', TomiloltAttachmets.as_view()),
    path('designationcrudPaginate/<str:type>/<str:state>/', TomiloltPaginateAPIView.as_view()),
    path('designationcrud/<int:pk>/', TomiloltCRUDApiView.as_view()),

    path('new-employee-orientation/', NewWorkerOrientationApiView.as_view(), name="new-employee-orientation"),
    path('new-employee-orientation-action/', NewWorkerOrientationActionApiView.as_view()),
    path('new-employee-orientation-action/<int:pk>/', NewWorkerOrientationActionOneApiView.as_view()),
    path('new-employee-orientation-action/image/', SaveChigluulehImageApiView.as_view()),
    path('new-employee-orientation-paginate/', NewWorkerOrientationPaginateApiView.as_view()),

    path("register/", WorkerRegisterApiView.as_view(), name="user-info-register-v2"),
    path("create/", WorkerCreateApiView.as_view()),

    path("find-worker/", FindWorkerApiView.as_view(), name="find-worker"),

    path("static/skills/", StaticSkillsApiView.as_view(), name="static-skills"),

    path('slip/<str:state>/', RoutingSlipPaginationApiView.as_view()),
    path("routing-slip/", RoutingSlipPageAPIView.as_view(), name="routing-slip-list"),
    path("routing-slip/create/", RoutingSlipApiView.as_view(), name="routing-slip-create"),
    path("routing-slip/create/<int:pk>/", RoutingSlipApiView.as_view(), name="routing-slip-have_slup"),

    path("routing-slip-demployee/", RoutingSlipEmployee.as_view(), name="routing-slup-info"),
    path("routing-slip-list/<int:pk>/", RoutingSlipListApiView.as_view(), name="routing-slup-info"),
    path("routing-slip-info/<int:pk>/", RoutingSlupCommanderPaginationApiView.as_view(), name="routing-slup-info"),
    path("routing-slip-employee/<int:pk>/", RoutingSlupEmployeePaginationApiView.as_view(), name="routing-slup-info"),

    path("employee-migrations/", EmployeeMigrationsApiView.as_view(), name="employee-migrations"),
    path("employee-migrations/<int:pk>/", EmployeeMigrationsApiView.as_view(), name="employee-migrations"),
    path("employee-migrations-info/<int:pk>/", CommandUsedEmployeeListApiView.as_view(), name="employee-migrations-info"),

    path("khodolmoriin-geree-ajax/", KhodolmoriinGereeApiView.as_view(), name="khodolmoriin-geree"),
    path("khodolmoriin-geree-ajax/<int:pk>/", KhodolmoriinGereeApiView.as_view(), name="khodolmoriin-geree"),

    path("definition/<int:pk>/", DefinitionApiView.as_view(), name="definition"),

    path("anket/", AnketApiView.as_view(), name="anket"),
    path("anket-register/", AnketRegisterApiView.as_view(), name="anket-register"),
    path("anket-register-action/", AnketRegisterActionApiView.as_view(), name="anket-register-action"),

    path("new-employee-registration-form/", NewEmployeeRegistrationFormApiView.as_view(), name="new-employee-registration-form"),
    path("new-employee-registration-form-action/", NewEmployeeRegistrationFormActionApiView.as_view(), name="new-employee-registration-form-action"),

]
