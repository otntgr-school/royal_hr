from django.urls import path

from .views import (
    SurgaltListAPIView,
    SurgaltPaginationViews,
    SurgaltCreateEditApiView,
    SurgaltDeleteApiView,
)

urlpatterns = [
    # Сураглтын бааз дээрх өгөгдлийг datatble-д авах
    path('', SurgaltPaginationViews.as_view(), name="surgalt-info-pagination"),

    path('surgalt-list/', SurgaltListAPIView.as_view(), name="surgalt-list"),
    path('surgalt-delete/<int:pk>/', SurgaltDeleteApiView.as_view(), name="surgalt-delete"),
    # create Сургалт
    path('surgalt-list/surgalt-create-edit/', SurgaltCreateEditApiView.as_view(), name="surgalt-create"),
    path('surgalt-list/surgalt-create-edit/<int:pk>/', SurgaltCreateEditApiView.as_view(), name="surgalt-create"),
    path('<int:pk>/', SurgaltPaginationViews.as_view(), name="surgalt-info-pagination"),
]
