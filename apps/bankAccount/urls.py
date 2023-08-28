from django.urls import path

from .views import BankInfoApiView
from .views import BankInfoListApiView
from .views import BankInfoDeleteApiView
from .views import BankInfoChangeOrder

from .views import BankAccountInfoApiView
from .views import BankAccountInfoListApiView

from .views import BankAccountPaginationApiView
from .views import BankAccountRequestActionApiView

urlpatterns = [
    path('', BankInfoApiView.as_view(), name="static-bank"),
    path('<int:pk>/', BankInfoApiView.as_view(), name="static-bank"),
    path('bank-info/change-order/', BankInfoChangeOrder.as_view(), name="bank-info-change-order"),
    path('bank-info-delete/<int:pk>/', BankInfoDeleteApiView.as_view(), name='static-bank-delete'),
    path('bank-info-list/', BankInfoListApiView.as_view(), name="bank_info_list"),

    path('bank-account-info-create/', BankAccountInfoApiView.as_view(), name="bank-account-info-create"),
    path('bank-account-info-create/<int:pk>/', BankAccountInfoApiView.as_view(), name="bank-account-info-create"),
    path('bank-account-info-create/<int:pk>/<int:userId>/', BankAccountInfoApiView.as_view(), name="bank-account-info-create"),
    path('bank-account-list/', BankAccountInfoListApiView.as_view(), name='bank-account-list'),
    path('bank-account-list/<int:pk>/', BankAccountInfoListApiView.as_view(), name='bank-account-list'),

    path('bank-account-info-pagination/', BankAccountPaginationApiView.as_view(), name='bank-account-info-pagination'),
    path('bank-account-info-pagination-action/', BankAccountRequestActionApiView.as_view(), name='bank-account-info-pagination'),
]
