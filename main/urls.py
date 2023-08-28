"""HR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('org/', include('apps.org.urls')),
    path('suborg/', include('apps.suborg.urls')),
    path('account/', include('apps.account.urls')),
    path('salbar/', include('apps.salbar.urls')),
    path('role/', include('apps.role.urls'), name="rolemain"),
    path('schedule/', include('apps.schedule.urls')),
    path('worker/', include('apps.worker.urls')),
    path('work-calendar/', include('apps.work_calendar.urls')),
    path('surgalt/', include('apps.surgalt.urls')),
    path('command/', include('apps.command.urls')),
    path('feedback/', include('apps.feedback.urls')),
    path('survey/', include('apps.survey.urls')),
    path('shagnal/', include('apps.shagnal.urls')),
    path('sahilga/', include('apps.sahilga.urls')),
    path('notif/', include('apps.notif.urls')),
    path('faq/', include('apps.faq.urls')),
    path('work-ad/', include('apps.work_ad.urls')),
    path('report/', include('apps.report.urls')),
    path('bank/', include('apps.bankAccount.urls')),
    path('device/', include('apps.device.urls')),
    path('kpi/', include('apps.kpi.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler404 = 'core.views.handler404'
# handler500 = 'core.views.handler500'
