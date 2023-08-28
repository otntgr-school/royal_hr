from django.urls import path
from .views import (

    RegisterApiView,
    LoginApiView,
    LogoutApiView,
    ResetPasswordApiView,

    NormalRegisterApiView,
    NormalRegisterPageApiView,
    NormalRegisterVerifyMail,
    ResendVerifyMail,
    ErrorVerifyMail,
    ForgotPassordApiView,
    ForgotPassordHTMLApiView,
    ForgotPasswordSendMailApiView,
    ForgotPassordChangePasswordApiView,

    UserGeneralInfoViews,
    UserGeneralInfoOneViews,

    UserRewardApiView,
    UserRewardApiViewDetail,
    UserRewardPaginationApiView,

    UserTalentApiView,
    UserTalentPaginationApiView,

    UserExtraInfoViews,
    UserExtraInfoUnits,
    UserExtraInfoOneViews,

    UserContactInfoViews,
    UserContactInfoOneViews,

    UserProfileImageApiView,

    HRAnketApiView,
    UserContactInfoHrApiView,
    UserGeneralInfoHrApiViews,
    UserExtraInfoHrApiViews,

    ApproveUserExtraInfoViews,
    ApproveUserContactInfoViews,
    ApproveUserGeneralInfoViews,
    UserContactInfoPaginationViews,
    UserExtraInfoPaginationViews,
    UserGeneralInfoPaginationViews,
    GeneralInfoChangeRequest,

    WorkerPageUpdateApiView,
    WorkerPageApiView,
    UserInfoApiView,

    UserAnketApiView,

    UserCholooPaginateApiView,
    UserSanalHvseltApiView,

    AccessHistoryApiView,

    PageBookmarksApiView,

    UserMedicalApiView,
    UserMedicalMainAjaxApiView,
    UserMedicalMainJsonApiView,
    UserMedicalAdditiveAjaxApiView,
    UserMedicalAdditiveJsonApiView,
    UserMedicalInpectionJsonApiView,
    UserMedicalInpectionAjaxApiView,

    UserEmployeeSalaryEditApiView,

    ExcelAddEmployeeCode,
    UserEmployeeRankLevelDegreeEditApiView,
)

urlpatterns = [
    path('', RegisterApiView.as_view()),
    path('user-register-page/', NormalRegisterPageApiView.as_view(), name='user-register'),
    path('user-register/', NormalRegisterApiView.as_view()),
    path('user-login/', LoginApiView.as_view(), name='account-user-login'),
    path('user-logout/', LogoutApiView.as_view(), name='account-user-logout'),
    path('user-reset-password/', ResetPasswordApiView.as_view(), name='account-user-password'),

    path('forgot-password/', ForgotPassordApiView.as_view(), name='forgot-password'),
    path("forgot-password-send-mail/", ForgotPasswordSendMailApiView.as_view()),
    path("forgot-password-change-pass/", ForgotPassordHTMLApiView.as_view()),
    path("forgot-password-change-pass-post/", ForgotPassordChangePasswordApiView.as_view()),
    path('verifymail/', NormalRegisterVerifyMail.as_view()),
    path('resend-verify-mail/', ResendVerifyMail.as_view()),
    path('token-error/', ErrorVerifyMail.as_view(), name='token-error'),

    path('worker/', WorkerPageApiView.as_view(), name='worker-profile'),
    path('worker/<int:pk>/', WorkerPageUpdateApiView.as_view(), name='worker-profile'),

    path('user-reward/', UserRewardApiView.as_view()),
    path('user-reward/<int:pk>/', UserRewardApiViewDetail.as_view()),
    path('user-reward-pagination/', UserRewardPaginationApiView.as_view()),

    path('user-talent/', UserTalentApiView.as_view()),
    path('user-talent/<int:pk>/', UserTalentApiView.as_view()),
    path('user-talent-pagination/', UserTalentPaginationApiView.as_view()),

    # Хүний нөөцийн хүн шууд мэдээллийг өөрчлөx
    path('user-talent-pagination/<int:pk>/', UserTalentPaginationApiView.as_view()),

    path('user-reward/hr/<int:pk>/', UserRewardApiView.as_view()),
    path('user-reward-pagination/<int:pk>/', UserRewardPaginationApiView.as_view()),

    path('user-general-info/hr/<int:pk>/', UserGeneralInfoHrApiViews.as_view()),
    path('user-extra-info/hr/<int:pk>/', UserExtraInfoHrApiViews.as_view()),
    path('user-contact-info/hr/<int:pk>/', UserContactInfoHrApiView.as_view()),
    path('user-anket/hr/', HRAnketApiView.as_view()),

    path('user-profile-image/', UserProfileImageApiView.as_view()),
    path('user-profile-image/<int:pk>/', UserProfileImageApiView.as_view()),

    path('user-general-info/', UserGeneralInfoViews.as_view()),
    path('user-general-info/<int:pk>/', UserGeneralInfoOneViews.as_view()),

    path('user-extra-info/', UserExtraInfoViews.as_view()),
    path('user-extra-info/<int:pk>/', UserExtraInfoOneViews.as_view()),
    path('user-extra-info-units/', UserExtraInfoUnits.as_view()),

    path('user-contact-info/', UserContactInfoViews.as_view()),
    path('user-contact-info/<int:pk>/', UserContactInfoOneViews.as_view()),

    path('user-contact-info-pagination/', UserContactInfoPaginationViews.as_view()),
    path('user-contact-info-pagination-action/', ApproveUserContactInfoViews.as_view()),
    path('user-extra-info-pagination/', UserExtraInfoPaginationViews.as_view()),
    path('user-extra-info-pagination-action/', ApproveUserExtraInfoViews.as_view()),
    path('user-general-info-pagination/', UserGeneralInfoPaginationViews.as_view()),
    path('user-general-info-pagination-action/', ApproveUserGeneralInfoViews.as_view()),
    path('requests-general-info/', GeneralInfoChangeRequest.as_view(), name='requests-general-info'),

    path('user-info-register/', UserInfoApiView.as_view(), name='user-info-register'),
    path('user-info-register/<int:pk>/', UserInfoApiView.as_view(), name='user-info-register'),

    path("anket/", UserAnketApiView.as_view(), name='user-anket'),
    path("anket/<int:pk>/<str:modeltype>/", UserAnketApiView.as_view(), name='user-anket'),

    path("my-choloo/<int:pk>/", UserCholooPaginateApiView.as_view()),
    path("user-sanal-hvselt/<int:pk>/", UserSanalHvseltApiView.as_view()),

    path("access-history/", AccessHistoryApiView.as_view(), name='access-history'),

    path("page-bookmark/", PageBookmarksApiView.as_view(), name='page-bookmarks'),

    path("medical/", UserMedicalApiView.as_view(), name='medical'),
    path("medical/<int:pk>/", UserMedicalApiView.as_view(), name='medical'),

    path("medical-main-ajax/", UserMedicalMainAjaxApiView.as_view(), name='medical-main-ajax'),
    path("medical-main-json/", UserMedicalMainJsonApiView.as_view(), name='medical-main-json'),

    path("medical-additive-ajax/", UserMedicalAdditiveAjaxApiView.as_view(), name='medical-additive-ajax'),
    path("medical-additive-json/", UserMedicalAdditiveJsonApiView.as_view(), name='medical-additive-json'),

    path("medical-inpection-ajax/", UserMedicalInpectionAjaxApiView.as_view(), name='medical-inpection-ajax'),
    path("medical-inpection-json/", UserMedicalInpectionJsonApiView.as_view(), name='medical-inpection-json'),

    path("employee-salary-edit/<int:pk>/", UserEmployeeSalaryEditApiView.as_view(), name='employee-salary-edit'),
    path("rank-level-degree-edit/<int:pk>/", UserEmployeeRankLevelDegreeEditApiView.as_view(), name='rank-level-degree-edit'),

    path("excel/", ExcelAddEmployeeCode.as_view(), name='excel-add-employee-code'),

]
