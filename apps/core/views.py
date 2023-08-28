
import datetime
import mimetypes

from django.http import Http404
from django.shortcuts import render
from django.http import FileResponse
from django.http.response import HttpResponse
from django.db.models import Value, Func
from django.db.models import F, CharField
from django.db.models.functions import Concat, Upper, Substr

from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from core.models import Orgs, UserInfo
from core.managers import SalbarManager
from core.models import Employee
from core.models import TimeScheduleRegister

from core.models import Attachments
from core.models import OrgPosition
from core.models import SubOrgs
from core.models import TimeScheduleRegister
from core.models import WorkingTimeSchedule
from core.models import WorkingTimeScheduleType

from .serializer import OrgPositionJsonSerializer
from .serializer import SubOrgJsonSerializer
from .serializer import OrgToEmployeeSerializer
from .serializer import EmployeeJsonSerializer
from .serializer import HomeTimeRegisterSerializer

from main.decorators import login_required
from main.utils.datatable import data_table


class HomeApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    @login_required()
    def get(self, request):

        # --------- Цаг бүртгэл хэсэг ----------

        # Аль товчлуур байхыг заана
        irsenee_burtguuleh_btn = 'none_active'
        time_register_id = None

        # Ажилчин байвал цаг бүртгэл харуулна
        if (request.employee):

            irsenee_burtguuleh_btn = 'blue_active'

            time_schedule_code = WorkingTimeSchedule.objects.filter(employees=request.employee).last()

            if time_schedule_code:

                code = int(time_schedule_code.type.code)

                if WorkingTimeScheduleType.TYPE_CODE.get('xy_days') == code:

                    # Хамгийн сүүлийн утгыг авж шалгана
                    check_register_btn = TimeScheduleRegister.objects.filter(
                        employee_id=request.employee.id
                    ).last()

                    if check_register_btn:

                        # Цагаа бүртгүүлчээд явуулахаа дараагүй бол товчлуур харагдахгүй
                        if check_register_btn.in_dt and not check_register_btn.out_dt:
                            irsenee_burtguuleh_btn = 'pink_active'

                        # # цагаа аль хэдийн явуулзан бол харуулахгүй
                        # if (check_register_btn.in_dt and check_register_btn.out_dt and check_register_btn.worked_time) or (check_register_btn.kind in [TimeScheduleRegister.KIND_AMRALT, TimeScheduleRegister.KIND_AMRALT_SHALTGAAN]):
                        #     irsenee_burtguuleh_btn = 'none_active'


                if WorkingTimeScheduleType.TYPE_CODE.get('seven_days') == code or WorkingTimeScheduleType.TYPE_CODE.get('independent_days') == code:

                    # Хамгийн сүүлийн утгыг авж шалгана
                    check_register_btn = TimeScheduleRegister.objects.filter(
                        employee_id=request.employee.id,
                        date=datetime.datetime.now().date()
                    ).last()

                    # Цагаа явуулаагүй бол
                    if check_register_btn:

                        # Цайны цагт орохоо явуулах бол
                        if check_register_btn.in_dt and not check_register_btn.out_dt and not check_register_btn.lunch_in_dt and not check_register_btn.lunch_out_dt:
                            time_register_id = check_register_btn.id
                            irsenee_burtguuleh_btn = 'blue_lunch_start_active'

                        # Цайны цаг дууссанаа явуулах бол
                        elif check_register_btn.in_dt and not check_register_btn.out_dt and check_register_btn.lunch_in_dt and not check_register_btn.lunch_out_dt:
                            time_register_id = check_register_btn.id
                            irsenee_burtguuleh_btn = 'blue_lunch_end_active'

                        # Цагаа бүртгүүлчээд явуулахаа дараагүй бол товчлуур харагдахгүй
                        elif check_register_btn.in_dt and not check_register_btn.out_dt and check_register_btn.lunch_in_dt and check_register_btn.lunch_out_dt:
                            time_register_id = check_register_btn.id
                            irsenee_burtguuleh_btn = 'pink_active'

                        # цагаа аль хэдийн явуулзан бол харуулахгүй
                        elif (check_register_btn.in_dt and check_register_btn.out_dt and check_register_btn.worked_time) or (check_register_btn.kind in [TimeScheduleRegister.KIND_AMRALT, TimeScheduleRegister.KIND_AMRALT_SHALTGAAN]):
                            irsenee_burtguuleh_btn = 'none_active'

        return Response(
        {
            'irsenee_burtguuleh_btn': irsenee_burtguuleh_btn,
            "today": datetime.datetime.now(),
            'time_register_id': time_register_id
        })


class OrgToEmployeeJsonApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin
):

    queryset = SubOrgs.objects
    serializer_class = SubOrgJsonSerializer

    @login_required()
    def get(self, request):
        """ Зөвхөн байгууллага доторх media файлуудаа харж болно """

        query = request.GET.get("choices")
        filters = dict()

        if query == 'songolt-sub-org' and request.exactly_org_filter.get("sub_org"):
            filters['id'] = request.exactly_org_filter.get("sub_org").pk
            self.queryset = self.queryset.filter(**filters)

        elif query == 'songolt-salbar':
            _filters = SalbarManager.get_filters(request)
            if _filters.get("sub_orgs"):
                self.queryset = self.queryset.filter(id=_filters.get("sub_orgs").pk)
            else:
                self.queryset = SubOrgs.objects.filter(org=request.org_filter.get("org"))
                self.serializer_class = SubOrgJsonSerializer

        elif query == 'songolt-position':
            self.queryset = OrgPosition.objects.filter(org=request.exactly_org_filter.get("org"))
            self.serializer_class = OrgPositionJsonSerializer

        elif query == 'songolt-employee':
            self.serializer_class = OrgToEmployeeSerializer
            self.queryset = Orgs.objects.filter(id=request.org_filter.get("org").id)

        data = self.list(request).data
        if query == 'songolt-employee':
            qs = Employee.objects.filter(**request.org_filter)
            extra_data = EmployeeJsonSerializer(qs, many=True).data
            data = {
                "employees": extra_data,
                "data": data
            }
        return request.send_data(data)


class AttachmentAPIView(APIView):

    @login_required()
    def get(self, request, pk):
        """ Зөвхөн байгууллага доторх media файлуудаа харж болно """

        try:
            attachment = Attachments.objects.get(pk=pk, org=request.exactly_org_filter.get("org"))
            _path = attachment.file.path
            _file = open(_path, 'rb')
            response = FileResponse(_file)
        except Exception as e:
            raise Http404

        return response


class ComingEmpsApiView(APIView):

    @login_required()
    def get(self, request):

        employee_ids = Employee.objects.filter(**request.exactly_org_filter, state=Employee.STATE_WORKING).values_list("id", flat=True)
        today_date = datetime.datetime.now().date()

        qs = TimeScheduleRegister \
                .objects \
                .filter(
                    kind=TimeScheduleRegister.KIND_WORKING,
                    employee_id__in=employee_ids,
                    date=today_date,
                    employee__user__userinfo__action_status=UserInfo.APPROVED,
                    employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                ) \
                .annotate(
                    f_in_dt=Func(
                        F('in_dt'),
                        Value('HH24:MM'),
                        function='to_char',
                        output_field=CharField()
                    ),
                    f_out_dt=Func(
                        F('out_dt'),
                        Value('HH24:MM'),
                        function='to_char',
                        output_field=CharField()
                    ),
                    full_name=Concat(Upper(Substr("employee__user__userinfo__last_name", 1, 1)), Value(". "), "employee__user__userinfo__first_name"),
                    pos_name=F("employee__org_position__name"),
                )

        paginated = data_table(qs, request)
        paginated['data'] = HomeTimeRegisterSerializer(paginated['data'], many=True).data
        return Response(paginated)


def workerID(request):
    return render(request, 'worker-profile.html')

def subCompanyRegister(request):
    return render(request, "sub-company-register.html")

def leaveToVote(request):
    return render(request, 'leave-to-vote.html')

def scheduleType(request):
    return render(request, 'schedule-type.html')

def timetableList(request):
    return render(request, 'timetable-list.html')

def orgregister(request):
    return render(request, 'org-register.html')

def lineGraph(request):
    return render(request, 'line-graph.html')

# def forgotPassword(request):
#     return render(request, 'forgot-password.html')

# def signUp(request):
#     return render(request, 'sign-up.html')

def newEmployeeOrientation(request):
    return render(request, 'new-employee-orientation.html')

def trainingPlanRegister(request):
    return render(request, 'training-plan-register.html')

def settings(request):
    return render(request, 'settings.html')

def commandDecisionRegister(request):
    return render(request, 'command-decision-register.html')

def putToWork(request):
    return render(request, 'put-to-work.html')

def designation(request):
    return render(request, 'designation.html')

def humanResourceReport(request):
    return render(request, 'human-resource-report.html')

def kpiTypeRegister(request):
    return render(request, 'kpi-type-register.html')

def toirohHuudas(request):
    return render(request, 'toiroh-huudas.html')


class DownloadFile(APIView):
    def get(self, request):
        attach_id = request.GET.get("attachId")
        try:
            attachment = Attachments.objects.get(pk=attach_id, org_id=request.exactly_org_filter.get("org").id)
            _path = attachment.file.path
            mime_type, _ = mimetypes.guess_type(_path)

            path = open(_path, 'rb')
            response = HttpResponse(path, content_type=mime_type)

            response['Content-Disposition'] = "attachment; filename=%s" % attachment.file.name
            return response
        except Exception as e:
            raise Http404
