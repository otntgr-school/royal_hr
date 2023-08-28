from django.urls import path

from .views import (
    CommandPageAPIView,
    CommandPaginationViews,
    CommandCreateEditApiView,
    CommandDeleteApiView,
    CommandAttachMents
)

urlpatterns = [
    # Сураглтын бааз дээрх өгөгдлийг datatble-д авах
    path('list/<str:types>/', CommandPaginationViews.as_view(), name="Command-info-pagination"),
    path('command-page/', CommandPageAPIView.as_view(), name="command-page"),
    path('get-command-attachmets/<int:pk>/', CommandAttachMents.as_view()),
    # # create Сургалт
    path('command-page/command-create-edit/', CommandCreateEditApiView.as_view(), name="command-create"),
    path('command-page/command-create-edit/<int:pk>/', CommandCreateEditApiView.as_view(), name="command-create"),

    path('command-page/command-create-delete/<int:pk>/', CommandDeleteApiView.as_view(), name="command-create"),

]
