from django.urls import path
from .views import (
    AlbaTushaalCRUDApiView,

    HomeApiView,
    RoleListApiView,
    PermissionApiView,
    PermissionActionApiView,
    PositionActionApiView,
    PositionsTreeApiView,
    RolePaginationApiView,
    PermPaginationApiView,
    PositionDeleteApiView,
    GETRolePermsApiView,
)

urlpatterns = [
    path('', RoleListApiView.as_view(), name="role"),
    path('role-pagination/', RolePaginationApiView.as_view()),
    path('role-action/', HomeApiView.as_view(), name="role-action"),
    path('role-action/<int:pk>/', HomeApiView.as_view(), name="role-action"),

    path('permission-list/', PermissionApiView.as_view(), name="permission-list"),
    path('permission-pagination/', PermPaginationApiView.as_view()),
    path('permission/', PermissionActionApiView.as_view(), name="permission-action"),
    path('permission/<int:pk>/', PermissionActionApiView.as_view(), name="permission-action"),

    path('alban-tushaal-todorhoilolt/', AlbaTushaalCRUDApiView.as_view()),
    path('alban-tushaal-todorhoilolt/<int:pk>/', AlbaTushaalCRUDApiView.as_view()),

    path('position/', PositionActionApiView.as_view(), name="position-action"),
    path('position/perms/', GETRolePermsApiView.as_view(), name="role-perms"),
    path('positions-tree/', PositionsTreeApiView.as_view()),
    path('position/<int:pk>/', PositionActionApiView.as_view(), name="position-action"),
    path('orgpos-delete/<int:pk>/', PositionDeleteApiView.as_view(), name="orgpos-delete"),
]
