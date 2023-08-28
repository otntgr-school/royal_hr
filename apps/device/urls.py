from django.urls import path

from .views import (
    DeviceRegister,
    GetTimeScheduleRegisterDataFromExcel
)

urlpatterns = [
    path('', DeviceRegister.as_view()),
    path('excel/', GetTimeScheduleRegisterDataFromExcel.as_view()),
]
