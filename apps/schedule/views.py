
import datetime
import json
from this import d

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

from next_prev import prev_in_order

from django.db.models import F
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Max
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models.functions import Upper
from django.db.models.functions import Substr

from django.db import transaction
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework import generics
from rest_framework import mixins
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from main.decorators import login_required
from main.decorators import has_permission

from core.models import TimeScheduleType
from core.models import WorkingTimeSchedule
from core.models import WorkingTimeScheduleType
from core.models import TimeScheduleRegister
from core.models import UserInfo
from core.models import Employee
from core.models import RequestTimeVacationRegister
from core.models import OrgVacationTypes
from core.models import OrgVacationTypesBranchTypes
from core.models import XyTimeScheduleValues
from core.models import Notification
from core.models import SubOrgs
from core.models import HolidayDayInYear
from core.models import OrgPosition
from core.models import Correspond_Answer
from core.models import VacationEmployee

from .serializer import TimeScheduleTypeSerializer
from .serializer import WorkingTimeScheduleSerializer
from .serializer import WorkingTimeScheduleSerializerAjax
from .serializer import TimeScheduleRegisterSerializer
from .serializer import TimeScheduleRegisterDataTableSerializer
from .serializer import EmployeeSerializer
from .serializer import TimeScheduleTypeAllSerializer
from .serializer import RequestTimeVacationRegisterSerializer
from .serializer import RequestTimeVacationRegisterJsonSerializer
from .serializer import OrgVacationTypesSerializer
from .serializer import OrgVacationTypesBranchTypesSerializer
from .serializer import OrgVacationTypesAndReasonSerializer
from .serializer import TimeScheduleRegisterReportSerializer
from .serializer import RequestTimeVacationRegisterFirstNameJsonSerializer
from .serializer import WorkingTimeScheduleJsonSerializer
from .serializer import HolidayDayInYearSerializer
from .serializer import RequestTimeVacationRegisterGetSerializer
from .serializer import OrgPositionSerializer
from .serializer import OrgVacationTypesDetailSerializer
from .serializer import VacationEmployeeSerializer
from .serializer import VacationEmployeeDecidingSerializer
from .serializer import TimeScheduleTypeFormSerializer

from main.utils.datatable import data_table

# Одоогийн цаг
now_time = datetime.datetime.now()

class WorkTimeTypeJson(APIView):
    def get(self, request):
        ''' Ажлын цагийн төрөлийн datatable-ийн утгыг авна
        '''
        # Байгууллагаар шүүнэ
        org_id = None
        if request.employee.org:
            org_id = request.employee.org.id

        qs = TimeScheduleType.objects.filter(org=org_id)
        paginated = data_table(qs, request)
        paginated['data'] = TimeScheduleTypeSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class WorkingTimeScheduleJson(APIView):
    def get(self, request):
        ''' Цагийн хуваарийн төрөлийн datatable-ийн утгыг авна
        '''
        # Байгууллагаар шүүнэ
        org_id = None
        if request.employee.org:
            org_id = request.employee.org.id

        qs = WorkingTimeSchedule.objects.filter(org=org_id)
        paginated = data_table(qs, request)
        paginated['data'] = WorkingTimeScheduleJsonSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class WorkingTimeScheduleRegisteredEmployeeJson(APIView):
    def get(self, request):
        ''' Бүртгэгдсэн ажилчидийн жагсаалт datatable-ийн утгыг авна
        '''

        # Цагийн хуваарийн төрөл ID
        chosedWtsId = request.GET['wtsEmplooyeChoosedId']

        qs = WorkingTimeSchedule.objects \
            .filter(id=chosedWtsId) \
            .first()

        qs = qs.employees \
            .filter(
                user__userinfo__action_status=UserInfo.APPROVED,
                user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
            ) \
            .annotate(
                first_name=F("user__userinfo__first_name"),
                last_name=F("user__userinfo__last_name"),
                register=F("user__userinfo__register"),
                ex_sub_org_id=F("sub_org__id"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = EmployeeSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class WorkingTimeScheduleNotRegisteredEmployeeJson(APIView):
    def get(self, request):
        ''' Цагийн хуваарийн төрөлд сонгогдоогзй ажилчидийн жагсаалт datatable-ийн утгыг авна
        '''

        filters = Employee.get_filter(request)
        filters['workingtimeschedule__isnull'] = True

        qs = Employee.objects \
            .filter(
                **filters,
                user__userinfo__action_status=UserInfo.APPROVED,
                user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                state=Employee.STATE_WORKING
            ) \
            .annotate(
                first_name=F("user__userinfo__first_name"),
                last_name=F("user__userinfo__last_name"),
                register=F("user__userinfo__register"),
                ex_sub_org_id=F("sub_org__id"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = EmployeeSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class TimeRegisterReportEmployeeAPIView(APIView):
    def get(self, request):
        ''' Цагийн тайлангийн ажилчин сонгох datatable-ын утгууд
        '''

        filters = Employee.get_filter(request)

        qs = Employee.objects \
            .filter(
                **filters,
                user__userinfo__action_status=UserInfo.APPROVED,
                user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
            ) \
            .annotate(
                first_name=F("user__userinfo__first_name"),
                last_name=F("user__userinfo__last_name"),
                register=F("user__userinfo__register"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = EmployeeSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class WorkingTimeScheduleAjaxEmployeeRemoveAPIView(APIView):
    ''' Цагийн хуваарийн төрөл дээр ажилчин хасах
    '''

    @login_required()
    @has_permission(allowed_permissions=['working-time-schedule-add-remove-employee'])
    def put(self, request, pk=None):
        snippet = WorkingTimeSchedule.objects.get(id=pk)

        # XY-ээс ажилчин хасаж байгаа бол start_next_job_date, start_next_vacation_date 2-ыг хоослоно
        if int(snippet.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):
            xy_time_values = XyTimeScheduleValues.objects.filter(employee__in=request.data['checkedUsers'])
            for xy_time_value in xy_time_values:
                xy_time_value.start_next_job_date = None
                xy_time_value.start_next_vacation_date = None
                xy_time_value.save()

        qs_employees = Employee.objects.filter(pk__in=request.data['checkedUsers'])
        snippet.employees.remove(*qs_employees)

        return request.send_info("INF_002")


class WorkingTimeScheduleAjaxEmployeeAddAPIView(APIView):
    ''' Цагийн хуваарийн төрөл дээр ажилчин нэмэх
    '''

    @login_required()
    @has_permission(allowed_permissions=['working-time-schedule-add-remove-employee'])
    def put(self, request, pk=None):
        snippet = WorkingTimeSchedule.objects.filter(id=pk).first()
        qs_employees = Employee.objects.filter(pk__in=request.data['checkedUsers'])
        snippet.employees.add(*qs_employees)

        return request.send_info("INF_002")


class WorkingTimeScheduleAjaxEmployeeXyAddAPIView(APIView):
    ''' Цагийн хуваарийн төрөл дээр ажилчиний эхлэх цагийг нэмэх
    '''

    @login_required()
    def put(self, request, pk=None):

        with transaction.atomic():
            employee = Employee.objects.filter(id=pk).last()

            # Ажилчнаа нэмнэ
            working_snippet = WorkingTimeSchedule.objects.filter(id=request.data.get('wtsEmplooyeChoosedId')).first()
            working_snippet.employees.add(employee)

            xy_start_time = parse(request.data.get('xy_start_time'))
            # Ажлын дараачийн эхлэх өдөр
            start_next_job_date = xy_start_time
            # Ажлын дараачийн амрах өдөр
            start_next_vacation_date = xy_start_time + relativedelta(hours=working_snippet.ajillah_time)

            # Xy ажлын цагийн утгуудаа хадгална
            XyTimeScheduleValues.objects.update_or_create(
                employee=employee,
                defaults={
                    'start_date': xy_start_time,
                    'start_next_job_date': start_next_job_date,
                    'start_next_vacation_date': start_next_vacation_date,
                },
            )

        return request.send_info("INF_002")


class TimeScheduleJson(APIView):

    def get(self, request):
        ''' Цагийн хуваарийн төрөл дээр ажилчин хасах
        '''
        employee_id = None
        if request.employee:
            employee_id = request.employee.id

        qs = TimeScheduleRegister.objects.filter(employee=employee_id)

        paginated = data_table(qs, request)

        paginated['data'] = TimeScheduleRegisterDataTableSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class WorkTimeTypeAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    ''' Ажлын цагийн төрөл CRUD үйлдэл
    '''

    serializer_class = TimeScheduleTypeSerializer
    queryset = TimeScheduleType.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/work-time-type/index.html'

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk=None):

        return Response({
            'serializer': TimeScheduleTypeFormSerializer
        })

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-create'])
    def post(self, request, pk=None):
        """ шинээр үүсгэх нь:
        - ``name`` - Нэр
        - ``org`` - Байгууллага ID
        """

        request.data._mutable = True
        request.data['lunch_time_start_time']= request.data['start_time']
        request.data['lunch_time_end_time']= request.data['start_time']
        request.data._mutable = False

        serializer = TimeScheduleTypeAllSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('work-time-type')


class WorkTimeTypeAjaxAPIView(APIView):
    ''' Ажлын цагийн төрөл ajax үйлдлүүд
    '''

    def get_object(self, pk, request):
        try:
            return TimeScheduleType.objects.get(pk=pk)
        except TimeScheduleType.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = TimeScheduleTypeAllSerializer(snippet)
        return request.send_data(serializer.data)

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-update'])
    def put(self, request, pk=None):
        snippet = TimeScheduleType.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")


class WorkingTimeScheduleAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    ''' Ажлын цагийн төрөл CRUD үйлдэл
    '''

    serializer_class = WorkingTimeScheduleSerializer
    queryset = WorkingTimeSchedule.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/working-time-schedule/index.html'

    @login_required()
    @has_permission(allowed_permissions=['working-time-schedule-read'])
    def get(self, request, pk=None):

        org_id = None
        sub_org_list = list()

        if request.employee.org:
            org_id = request.employee.org.id


        working_time_schedule_type = WorkingTimeScheduleType.objects.all().order_by('-id').values('name', 'id', 'code')
        time_schedule = TimeScheduleType.objects.filter(org=org_id).order_by('-id')

        # Хэрвээ дэд байгууллага харьяалагддаггүй байгууллагын гар бол дэд байгууллагуудаа сонгодог хэсэг харуулах
        if (request.org_filter.get("org") and not request.org_filter.get("sub_org") and not request.org_filter.get("salbar")):
            sub_org_list = SubOrgs.objects.filter(org=request.org_filter.get("org"))
        else:
            sub_org_list = SubOrgs.objects.filter(pk=request.org_filter.get("sub_org").id)


        return Response(
        {
            'serializer': self.serializer_class,
            'working_time_schedule_types': working_time_schedule_type,
            'time_schedules': time_schedule,
            'sub_org_list': sub_org_list
        })

    @login_required()
    @has_permission(allowed_permissions=['working-time-schedule-create-or-update'])
    def post(self, request, pk=None):
        """ шинээр үүсгэх нь:
        - ``name`` - Нэр
        - ``org`` - Байгууллага ID
        """

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('working-time-schedule')


class WorkingTimeScheduleAjaxAPIView(APIView):
    ''' Ажлын цагийн төрөл үйлдэлүүд
    '''

    def get_object(self, pk, request):
        try:
            return WorkingTimeSchedule.objects.get(pk=pk)
        except WorkingTimeSchedule.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['working-time-schedule-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = WorkingTimeScheduleSerializerAjax(snippet)
        return request.send_data(serializer.data)

    @login_required()
    @has_permission(allowed_permissions=['working-time-schedule-create-or-update'])
    def put(self, request, pk=None):

        time_format_inputs = ['registration_start_time', 'registration_end_time', 'lunch_time']
        time_format_inputs_v2 = [ 'hotorch_boloh_limit' ]

        # Цаг утгагуудыг хоосон бол '' гэж ирж баазад хадгалж чадахгүй байсан болохоор хоосон болгож байна
        for time_format_input in time_format_inputs_v2:
            if request.data[time_format_input] == '':
                request.data[time_format_input] = None

        snippet = WorkingTimeSchedule.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")


class TimeScheduleRegisterAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    ''' Цагаа бүртгүүлэх
    '''
    serializer_class = TimeScheduleRegisterSerializer
    queryset = TimeScheduleRegister.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/time-schedule-register/index.html'

    def get(self, request, pk=None):

        # Аль товчлуур байхыг заана
        irsenee_burtguuleh_btn = True
        # Хамгийн сүүлийн утгыг авж шалгана
        check_register_btn = self.queryset.filter(employee_id=request.employee.id, date=now_time.date()).last()

        # Цагийн хуваарийн төрөлд бүртгүүлээгүй бол нүүр хуудас луу буцаана
        qs_working_time_sch = WorkingTimeSchedule.objects.filter(employees=request.employee.id).first()

        if not qs_working_time_sch:
            request.send_message("warning", "ERR_016")
            return HttpResponseRedirect('/')

        if check_register_btn:
            # 7 хоног бол
            if int(check_register_btn.employee.workingtimeschedule_set.last().type.code) == int(WorkingTimeScheduleType.TYPE_CODE.get('seven_days')):
                # Цагаа бүртгүүлчээд явуулахаа дараагүй бол товчлуур харагдахгүй
                if (check_register_btn.in_dt and not check_register_btn.out_dt) or (check_register_btn.in_dt and check_register_btn.out_dt):
                    irsenee_burtguuleh_btn = False

        return Response(
        {
            'serializer': self.serializer_class,
            'irsenee_burtguuleh_btn': irsenee_burtguuleh_btn,
            'working_time_schedule': qs_working_time_sch.type.code,
            "today": datetime.datetime.now(),
        })

    def post(self, request, pk=None, type=None):
        """ шинээр үүсгэх нь:
        - ``name`` - Нэр
        - ``org`` - Байгууллага ID
        """

        # Торгууль
        fine = 0
        hotsorson_time = ''

        # Цагийн хуваарийн төрөлд бүртгүүлээгүй бол нүүр хуудас луу буцаана
        qs_working_time_sch = WorkingTimeSchedule.objects.filter(employees=request.employee.id).first()

        if not qs_working_time_sch:
            request.send_message("warning", "ERR_016")
            return HttpResponseRedirect('/')

        # Ирсэн цагаас бусад үйлдэл гэлгийг нь мэдэж болно
        if pk:

            instance = self.queryset.get(pk=pk)

            if type == 'start_lunch':

                instance.lunch_in_dt = datetime.datetime.now()
                instance.lunch_out_dt = datetime.datetime.now()
                instance.save()

                request.send_message('success', 'INF_015')
                return redirect('time-schedule-register')

            if type == 'end_lunch':

                instance.lunch_out_dt = datetime.datetime.now()
                instance.save()

                request.send_message('success', 'INF_015')
                return redirect('time-schedule-register')

            if type == 'end_work':

                instance = self.queryset.get(pk=pk)

                if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):
                    value = datetime.datetime.now() - instance.in_dt
                else:
                    value = datetime.datetime.now() - instance.in_dt - (instance.lunch_out_dt - instance.lunch_in_dt)

                # Хэдэн цаг ажилссаныг тооцох
                # Нийт хэдэн сек олоод хувиргаад олно
                s = int(value.total_seconds())
                hours = s // 3600
                s = s - (hours * 3600)
                minutes = s // 60
                seconds = s - (minutes * 60)
                worked_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                instance.worked_time = str(worked_time)
                instance.out_dt = datetime.datetime.now()
                instance.save()

                if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):
                    xyTimeScheduleValue = XyTimeScheduleValues.objects.filter(employee=request.employee.id).last()

                    # Дараачийн ажлын эхлэх цагийг шинэчлэнэ
                    start_next_job_date_value = xyTimeScheduleValue.start_next_job_date + relativedelta(hours=qs_working_time_sch.ajillah_time) + relativedelta(hours=qs_working_time_sch.amrah_time)
                    xyTimeScheduleValue.start_next_job_date = start_next_job_date_value
                    xyTimeScheduleValue.save()

                request.send_message('success', 'INF_015')
                return redirect('time-schedule-register')


        # ---------------- 7 хоногийн Цагийн хуваарийн төрөл ----------------
        if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days'):

            # Өдөрт олон удаа цагаа явуулах гээд spam-даад байвал warning буцаана
            qs_check_today = TimeScheduleRegister.objects.filter(
                employee=request.employee.id,
                date=datetime.datetime.now().date()
            ).first()

            # Зөвхөн өдрөөр чөлөө авсаныг шалгаж байна
            today_shaltgaan = RequestTimeVacationRegister.objects.filter(
                Q(start_day=now_time.date()) & Q(end_day__isnull=False)
            ).first()

            if qs_check_today:

                # Алдаа буцаана
                # 1) Олон удаа spamдуул 2) Амралт, Тасалсан, Олон өдөрүүдээр чөлөө авсан бол
                if (
                    qs_check_today.out_dt or
                    qs_check_today.kind == TimeScheduleRegister.KIND_AMRALT or
                    qs_check_today.kind == TimeScheduleRegister.KIND_TAS or
                    qs_check_today.kind == TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN
                ):
                    request.send_message("warning", "ERR_017")
                    return redirect('time-schedule-register')

                # 1 Өдрөөр хүсэлт авсан бол цаг хамаарахгүй хадгална
                if (qs_check_today.kind == TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN and today_shaltgaan):
                    qs_check_today.in_dt = datetime.datetime.now()
                    qs_check_today.save()

                    request.send_message('success', 'INF_015')
                    return redirect('time-schedule-register')

            # Явсан цаг бүртгэж дуусах хугацаа
            today_time_schedule = datetime.datetime.now().strftime('%a').lower() + '_time_schedule'
            if (not getattr(qs_working_time_sch, today_time_schedule)):
                request.send_message("warning", "ERR_018")
                return redirect('time-schedule-register')

            # registration_start_time = (getattr(qs_working_time_sch, today_time_schedule)).registration_start_time
            # start_time = (getattr(qs_working_time_sch, today_time_schedule)).start_time

            hotorch_boloh_limit = (getattr(qs_working_time_sch, today_time_schedule)).hotorch_boloh_limit

            # # Ирсэн цагаа бүртгүүлэх цаг нь одоогийнхоос хэтрээгүй бол цааш явуулахгүй
            # if registration_start_time > now_time.time():
            #     request.send_message("warning", "ERR_018")
            #     return redirect('time-schedule-register')

            # Ажилд ирэх цагаасаа хоцорсон бол торгууль бодно
            if hotorch_boloh_limit < now_time.time():
                # fine = fine + qs_working_time_sch.start_time_penalty

                hotsorj_irsen_tsag = datetime.datetime.strptime(f'{now_time.date()} {hotorch_boloh_limit}', '%Y-%m-%d %H:%M:%S')

                hotsorson_tsag = datetime.datetime.now() - hotsorj_irsen_tsag

                # Хэдэн цаг хоцорсныг тооцох
                s = int(hotsorson_tsag.total_seconds())
                hours = s // 3600
                s = s - (hours * 3600)
                minutes = s // 60
                seconds = s - (minutes * 60)
                hotsorson_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


        # --------------- XY хоногийн Цагийн хуваарийн төрөл ----------------
        if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):

            xyTimeScheduleValue = XyTimeScheduleValues.objects.filter(employee=request.employee.id).last()

            start_time = xyTimeScheduleValue.start_next_job_date
            hotorch_boloh_limit = qs_working_time_sch.hotorch_boloh_limit

            registration_start_time = start_time + relativedelta(hours=hotorch_boloh_limit.hour, minutes=hotorch_boloh_limit.minute, seconds=hotorch_boloh_limit.second)

            # # TODO: Асуух зүйл
            # # Алдаа буцаана
            # # 1) Амралтын цагаар цагаа явуулах
            # if (now_time > xyTimeScheduleValue.start_next_vacation_date):
            #     request.send_message("warning", "ERR_018")
            #     return redirect('time-schedule-register')

            # qs_registration_start_time = qs_working_time_sch.registration_start_time

            # registration_start_time = xyTimeScheduleValue.start_next_job_date - relativedelta(hours=qs_registration_start_time.hour, minutes=qs_registration_start_time.minute, seconds=qs_registration_start_time.second)
            # start_time = xyTimeScheduleValue.start_next_job_date

            # # Ирсэн цагаа бүртгүүлэх цаг нь одоогийнхоос хэтрээгүй бол цааш явуулахгүй
            # if registration_start_time > now_time:
            #     request.send_message("warning", "ERR_018")
            #     return redirect('time-schedule-register')

            if registration_start_time < now_time:

                hotsorson_tsag = datetime.datetime.now() - registration_start_time

                # Хэдэн цаг хоцорсныг тооцох
                s = int(hotsorson_tsag.total_seconds())
                hours = s // 3600
                s = s - (hours * 3600)
                minutes = s // 60
                seconds = s - (minutes * 60)
                hotsorson_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

            # NOTE: XY-д хоцорч болох лимит гэж байхгүй
            # Ажилд ирэх цагаасаа хоцорсон бол торгууль бодно
            # if start_time < now_time:
                # fine = fine + qs_working_time_sch.start_time_penalty

        datas = {}

        for key in request.data:
            datas[key] = request.data[key]
        datas['in_dt'] = datetime.datetime.now()
        datas['lunch_in_dt'] = datetime.datetime.now()
        datas['lunch_out_dt'] = datetime.datetime.now()
        datas['date'] = datetime.datetime.now().date()

        qs_holiday = HolidayDayInYear.objects.filter(
            (Q(every_year=True) & Q(date__month=now_time.month) & Q(date__day=now_time.day)) | (Q(every_year=False) & Q(date__year=now_time.year) & Q(date__month=now_time.month) & Q(date__month=now_time.day))
        )

        datas['kind'] = TimeScheduleRegister.KIND_WORKING
        if qs_holiday:
            datas['kind'] = TimeScheduleRegister.KIND_AMRALT_AJLIIN

        datas['hotsorson_time'] = hotsorson_time
        datas['fine'] = fine

        serializer = self.serializer_class(data=datas)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('time-schedule-register')


class TimeScheduleRegisterOutAPIView(
    generics.GenericAPIView
):
    ''' явсан цагаа бүртгүүлэх (HOME page-ээс)
    '''
    serializer_class = TimeScheduleRegisterSerializer
    queryset = TimeScheduleRegister.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/time-schedule-register/index.html'

    def post(self, request):

        employee_id = request.employee.id

        qs_working_time_sch = WorkingTimeSchedule.objects.filter(employees=employee_id).first()

        instance = self.queryset.filter(
            date=now_time.date(),
            employee=employee_id,
            in_dt__isnull=False,
            out_dt__isnull=True
        ).last()

        value = datetime.datetime.now() - instance.in_dt

        # Хэдэн цаг ажилссаныг тооцох
        # Нийт хэдэн сек олоод хувиргаад олно
        s = int(value.total_seconds())
        hours = s // 3600
        s = s - (hours * 3600)
        minutes = s // 60
        seconds = s - (minutes * 60)
        worked_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

        instance.worked_time = str(worked_time)
        instance.out_dt = datetime.datetime.now()
        instance.save()

        if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):
            xyTimeScheduleValue = XyTimeScheduleValues.objects.filter(employee=request.employee.id).last()

            # Дараачийн ажлын эхлэх цагийг шинэчлэнэ
            start_next_job_date_value = xyTimeScheduleValue.start_next_job_date + relativedelta(hours=qs_working_time_sch.ajillah_time) + relativedelta(hours=qs_working_time_sch.amrah_time)
            xyTimeScheduleValue.start_next_job_date = start_next_job_date_value
            xyTimeScheduleValue.save()

        request.send_message('success', 'INF_015')
        return redirect('time-schedule-register')


class TimeScheduleRegisterAjaxAPIView(APIView):

    def get_object(self, pk, request):
        try:
            return TimeScheduleRegister.objects.get(pk=pk)
        except TimeScheduleRegister.DoesNotExist:
            raise request.send_error("ERR_003")

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = TimeScheduleRegisterDataTableSerializer(snippet)
        return request.send_data(serializer.data)


class TimeRegisterRequestAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """ Хүсэлт илгээх
    """

    serializer_class = RequestTimeVacationRegisterSerializer
    queryset = RequestTimeVacationRegister.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/time-register-request/index.html'

    @login_required()
    @has_permission(allowed_permissions=['request-read'])
    def get(self, request, pk=None):

        org_id = request.org_filter.get('org').id
        employee_id = request.employee.id

        vacation_types = OrgVacationTypes.objects.filter(org=org_id)
        vacation_types_ser = OrgVacationTypesAndReasonSerializer(vacation_types, many=True).data

        vacation_types_reasons_jsons = list(vacation_types_ser)

        # Тухайн сард хэдэн эрх үлдсэнийг тоолно
        for vacation_types_reasons_json in vacation_types_reasons_jsons:
            residual_times = RequestTimeVacationRegister.objects.filter(
                employee=employee_id,
                status=RequestTimeVacationRegister.AGREE,
                start_day__month=datetime.datetime.now().month,
                vacation_type=vacation_types_reasons_json['id']
            )
            len_residual_times = len(residual_times)

            vacation_types_reasons_json['len_residual_times'] = len_residual_times

        return Response({
            'serializer': self.serializer_class,
            'vacation_types_reasons': vacation_types_ser,
            'vacation_types_reasons_json': json.dumps(vacation_types_ser),
        })

    @login_required()
    @has_permission(allowed_permissions=['request-create'])
    def post(self, request, pk=None):
        """ Шинээр үүсгэх
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('time-register-request')


class TimeRegisterRequestJson(APIView):
    def get(self, request):
        ''' Хүсэлт илгээх datatable-ийн утгыг авна
        '''
        qs = RequestTimeVacationRegister.objects.filter(employee=request.employee.id)
        paginated = data_table(qs, request)
        paginated['data'] = RequestTimeVacationRegisterJsonSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class TimeRegisterRequestCheckDate(APIView):
    def post(self, request):
        ''' Тус өдөрт ямар нэгэн чөлөө авзан бас цаг эд нараа илгээзэн эсэхийг шалгах
        '''

        qs = TimeScheduleRegister.objects.filter(
            employee=request.employee.id,
            date=request.data
        ).first()

        if qs:
            return request.send_data(True)
        return request.send_data(False)


class TimeRegisterRequestWaitingJson(APIView):
    def get(self, request):
        ''' Хүсэлт зөвшаарөх татгалзах үеийн хүлээгдэж буй хүмүүсийн datatable-ийн утгыг авна
        '''
        org = request.org_filter.get('org')

        qs = RequestTimeVacationRegister.objects \
            .order_by('-created_at') \
            .filter(
                status=RequestTimeVacationRegister.WAITING,
                employee__user__userinfo__action_status=UserInfo.APPROVED,
                employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                employee__org__id=org.id
                # employee__id=request.employee.id
            ) \
            .annotate(
                first_name=F("employee__user__userinfo__first_name")
            )
        paginated = data_table(qs, request)
        paginated['data'] = RequestTimeVacationRegisterFirstNameJsonSerializer(paginated['data'], context={ 'request': request }, many=True).data
        return JsonResponse(paginated, safe=False)


class TimeRegisterRequestSolveAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """ Хүсэлт шийдвэрлэх
    """

    serializer_class = RequestTimeVacationRegisterSerializer
    queryset = RequestTimeVacationRegister.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/time-register-request-solve/index.html'

    @login_required()
    @has_permission(allowed_permissions=['request-solve-read'])
    def get(self, request, pk=None):


        return Response({
            'serializer': self.serializer_class,
        })


class TimeRegisterRequestAgreeAPIView(APIView):
    ''' Хүсэлтийг зөвшөөрөх
    '''

    @login_required()
    @has_permission(allowed_permissions=['request-solve-agree'])
    def put(self, request, pk=None):
        employeeId = request.employee.id
        todayDatetime = datetime.datetime.strftime(now_time, "%Y-%m-%d")
        today_weekday = now_time.strftime('%a').lower() + '_work'

        qs = RequestTimeVacationRegister.objects.filter(pk=pk)
        qs.update(
            status=RequestTimeVacationRegister.AGREE,
            resolved_date=datetime.datetime.now(),
            agreed=employeeId
        )

        qs_last = qs.last()

        wrokingTimeScheduleType = WorkingTimeSchedule.objects.filter(employees=employeeId).values('type').last()

        if wrokingTimeScheduleType.get('type') == WorkingTimeScheduleType.TYPE_CODE.get('seven_days'):

        # Цаг бүртгэл дээр хадгалж өгнө чөлөөг зөвшөөрвөл
        # 1 өдөрийн чөлөө авч байвал
            if qs_last.end_day is None:

                check_date = TimeScheduleRegister.objects.filter(date=qs_last.start_day, employee=qs_last.employee.id).last()

                # Өнгөрзөн өдөр хүсэлт байвал
                if check_date:
                    if (check_date.kind in [TimeScheduleRegister.KIND_WORKING, TimeScheduleRegister.KIND_TAS, TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN]):
                        kind = TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN
                    else:
                        kind = TimeScheduleRegister.KIND_AMRALT_SHALTGAAN

                    check_date.kind = kind
                    check_date.for_shaltgaan = qs_last
                    check_date.save()

                # Ирээдүйд болох бол
                else:
                    # Өнөөдөр бол
                    if todayDatetime == str(qs_last.start_day):

                        if (getattr(qs_last.employee.workingtimeschedule_set.last(), today_weekday)):
                            TimeScheduleRegister.objects.create(**{
                                'date': qs_last.start_day,
                                'employee': qs_last.employee,
                                'kind': TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN,
                                'for_shaltgaan': qs_last
                            })
                        else:
                            TimeScheduleRegister.objects.create(**{
                                'date': qs_last.start_day,
                                'employee': qs_last.employee,
                                'kind': TimeScheduleRegister.KIND_SHALTGAAN,
                                'for_shaltgaan': qs_last
                            })
                    else:
                        TimeScheduleRegister.objects.create(**{
                            'date': qs_last.start_day,
                            'employee': qs_last.employee,
                            'kind': TimeScheduleRegister.KIND_SHALTGAAN,
                            'for_shaltgaan': qs_last
                        })

            # Олон өдөрийн чөлөө авч байвал
            else:
                days_range = qs_last.end_day - qs_last.start_day
                start_day = qs_last.start_day

                # Өдөр болгоноор нь давтана
                for day in range(int(days_range.days) + 1):

                    check_date = TimeScheduleRegister.objects.filter(date=start_day, employee=qs_last.employee.id).last()

                    # Өнгөрзөн өдөр хүсэлт байвал
                    if check_date:
                        if (check_date.kind in [TimeScheduleRegister.KIND_WORKING, TimeScheduleRegister.KIND_TAS, TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN]):
                            kind = TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN
                        else:
                            kind = TimeScheduleRegister.KIND_AMRALT_SHALTGAAN

                        check_date.kind = kind
                        check_date.for_shaltgaan = qs_last
                        check_date.save()

                    else:

                        if todayDatetime == str(start_day):
                            # Өнөөдөр ажлын өдөр байсан бол
                            if (getattr(qs_last.employee.workingtimeschedule_set.last(), today_weekday)):
                                TimeScheduleRegister.objects.create(**{
                                    'date': start_day,
                                    'employee': qs_last.employee,
                                    'kind': TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN,
                                    'for_shaltgaan': qs_last
                                })
                            else:
                                TimeScheduleRegister.objects.create(**{
                                    'date': start_day,
                                    'employee': qs_last.employee,
                                    'kind': TimeScheduleRegister.KIND_SHALTGAAN,
                                    'for_shaltgaan': qs_last
                                })
                        else:
                            TimeScheduleRegister.objects.create(**{
                                'date': start_day,
                                'employee': qs_last.employee,
                                'kind': TimeScheduleRegister.KIND_SHALTGAAN,
                                'for_shaltgaan': qs_last
                            })

                    start_day = start_day + datetime.timedelta(1)

        # Хэрвээ XY ажилчин бол бүх чөлөөний хүсэлтүүлдийг хадгална
        if wrokingTimeScheduleType.get('type') == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):
            if qs_last.end_day is None:
                TimeScheduleRegister.objects.create(**{
                    'date': qs_last.start_day,
                    'employee': qs_last.employee,
                    'kind': TimeScheduleRegister.KIND_SHALTGAAN,
                    'for_shaltgaan': qs_last
                })
            else:
                days_range = qs_last.end_day - qs_last.start_day
                start_day = qs_last.start_day

                # Өдөр болгоноор нь давтана
                for day in range(int(days_range.days) + 1):
                    TimeScheduleRegister.objects.create(**{
                        'date': start_day,
                        'employee': qs_last.employee,
                        'kind': TimeScheduleRegister.KIND_SHALTGAAN,
                        'for_shaltgaan': qs_last
                    })

                    start_day = start_day + datetime.timedelta(1)

        # Мэдэгдэл
        notification_body = {
            'title': 'Таний хүсэлтийг зөвшөөрсөн байна.',
            'content': 'Таний хүсэлтийг зөвшөөрсөн байна.',
            'ntype': 'normal',
            'url': reverse("time-register-request"),
            'scope_kind': Notification.SCOPE_KIND_EMPLOYEE,
            'from_kind': Notification.FROM_KIND_EMPLOYEE,
            'scope_ids': [ qs_last.employee.id ]
        }
        Notification.objects.create_notif(request, **notification_body)

        return request.send_info("INF_015")


class TimeRegisterRequestDeclineAPIView(APIView):
    ''' Хүсэлтийг татгалзах
    '''

    @login_required()
    @has_permission(allowed_permissions=['request-solve-refuse'])
    def put(self, request, pk=None):
        employeeId = request.employee.id

        snippet = RequestTimeVacationRegister.objects.filter(pk=pk)
        snippet.update(
            status=RequestTimeVacationRegister.DECLINE,
            resolved_date=datetime.datetime.now(),
            agreed=employeeId,
            **request.data
        )

        # Мэдэгдэл
        notification_body = {
            'title': 'Таний хүсэлтийг татгалзсан байна.',
            'content': 'Таний хүсэлтийг татгалзсан байна.',
            'ntype': 'normal',
            'url': reverse("time-register-request"),
            'scope_kind': Notification.SCOPE_KIND_EMPLOYEE,
            'from_kind': Notification.FROM_KIND_EMPLOYEE,
            'scope_ids': [ snippet.last().employee.id ]
        }
        Notification.objects.create_notif(request, **notification_body)

        return request.send_info("INF_002")


class TimeRegisterRequestUserWaitingJson(APIView):
    def get(self, request):
        ''' Сонгосон хүний амжилттай эсвэл татгалзсан хүсэлтүүдийг харуулна
        '''
        employeeId = request.GET['employeeId']

        qs = RequestTimeVacationRegister.objects.order_by('-created_at').filter(
            Q(employee__id=employeeId),
            (
                Q(status=RequestTimeVacationRegister.AGREE) | Q(status=RequestTimeVacationRegister.DECLINE)
            )
        )

        paginated = data_table(qs, request)
        paginated['data'] = RequestTimeVacationRegisterJsonSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class TimeRegisterRequestUserEndedJson(APIView):
    def get(self, request):
        ''' Тухайн байгууллагын амжилттай эсвэл татгалзсан хүсэлтүүдийг харуулна
        '''
        org = request.org_filter.get('org')

        qs = RequestTimeVacationRegister.objects.order_by('-created_at').filter(
            Q(employee__user__userinfo__action_status=UserInfo.APPROVED),
            Q(employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL),
            Q(employee__org=org),
            (
                Q(status=RequestTimeVacationRegister.AGREE) | Q(status=RequestTimeVacationRegister.DECLINE)
            )
        ).annotate(
            first_name=F("employee__user__userinfo__first_name")
        )

        paginated = data_table(qs, request)
        paginated['data'] = RequestTimeVacationRegisterFirstNameJsonSerializer(paginated['data'], context={ 'request': request }, many=True).data

        return JsonResponse(paginated, safe=False)


class CreateVacationTypeAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """ Хүсэлт шийдвэрлэх
    """
    serializer_class = OrgVacationTypesSerializer
    queryset = OrgVacationTypes.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/create-vacation-type/index.html'

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-read'])
    def get(self, request, pk=None):

        orgPosition_qs = OrgPosition.objects.filter()
        data = OrgPositionSerializer(orgPosition_qs, many=True).data

        return Response({
            'serializer': self.serializer_class,
            'org_positions': data,
        })

    @has_permission(allowed_permissions=['create-vacation-type-create-and-edit'])
    def post(self, request, pk=None):
        ''' Шинээр үүсгэх
        '''

        org_id = request.org_filter.get('org').id

        datas = {}

        for key in request.data:
            datas[key] = request.data[key]
        datas['org'] = org_id

        serializer = self.serializer_class(data=datas)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('create-vacation-type')


class CreateVacationTypeJson(APIView):
    def get(self, request):
        ''' Цагийн хуваарийн төрөлийн datatable-ийн утгыг авна
        '''
        org_id = request.org_filter.get('org').id

        qs = OrgVacationTypes.objects.filter(org=org_id)
        paginated = data_table(qs, request)
        paginated['data'] = OrgVacationTypesSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class CreateVacationReasonJson(APIView):
    def get(self, request):
        ''' Цагийн хуваарийн төрөлийн шалтгааны datatable-ийн утгыг авна
        '''

        qs = OrgVacationTypesBranchTypes.objects.filter(
            vacation = request.GET['vacation']
        )
        paginated = data_table(qs, request)
        paginated['data'] = OrgVacationTypesBranchTypesSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class CreateVacationReasonDraggableJson(APIView):
    def get(self, request):
        ''' Цагийн хуваарийн төрөлийн шалтгааны datatable-ийн утгыг авна
        '''

        qs = OrgVacationTypesBranchTypes.objects.filter(vacation=request.GET['vacation']).values("id", 'name', 'org_position', 'org_position__name').order_by("order")
        return request.send_data(qs)


class TimeScheduleOrder(APIView):

    @transaction.atomic()
    def put(self, request):

        from_id = request.data.get("from_id")
        to_id = request.data.get("to_id")

        if not from_id:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from_qs = OrgVacationTypesBranchTypes.objects.filter(id=from_id)
        #  фронтоос хамгийн доор байрлуулахад id ирэхгүй байгаа учраас түүнийг хайж олох нь
        if not to_id:
            _to = OrgVacationTypesBranchTypes.objects.aggregate(most_max=Max("order"))['most_max']
        else:
            _to_qs = OrgVacationTypesBranchTypes.objects.filter(id=to_id)
            if not _to_qs:
                ## warning bolgoh
                raise request.send_error("ERR_013")
            _to = _to_qs.first().order

        if not _from_qs:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from = _from_qs.first().order

        is_down = _from < _to
        _range = [_from, _to] if is_down else [_to, _from]

        changes = []

        qs = OrgVacationTypesBranchTypes.objects.filter(id=from_id, order=_from)
        if qs:
            qs.update(order=_to)
            changes.append([_from, _to, from_id])
            datas = OrgVacationTypesBranchTypes.objects.filter(order__range=_range).exclude(id=from_id).order_by('order')
            for item in datas:
                start = item.order
                item.order = item.order - 1 if is_down else item.order + 1
                end = item.order
                changes.append([start, end, item.id])
                item.save()
        else:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        return request.send_rsp("INF_002", changes)


class OrgVacationTypesAjaxAPIView(APIView):
    ''' Чөлөөний төрөлийн үйлдлүүд
    '''

    def get_object(self, pk, request):
        try:
            return OrgVacationTypes.objects.get(pk=pk)
        except OrgVacationTypes.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = OrgVacationTypesSerializer(snippet)
        return request.send_data(serializer.data)

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-create-and-edit'])
    def put(self, request, pk=None):
        snippet = OrgVacationTypes.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")


class CreateVacationReasonAjaxAPIView(APIView):
    ''' Чөлөөний төрөлийн шалтгааны үйлдлүүд
    '''

    def get_object(self, pk, request):
        try:
            return OrgVacationTypesBranchTypes.objects.get(pk=pk)
        except OrgVacationTypesBranchTypes.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-reason-create'])
    def post(self, request):

        vacation_type = OrgVacationTypes.objects.get(pk=request.data['vacation'])
        org_pos = int(request.data['org_position']) if request.data['org_position'] else None

        max_order = OrgVacationTypesBranchTypes.objects.aggregate(most_max=Max("order"))['most_max']

        OrgVacationTypesBranchTypes.objects.create(**{
            'name': request.data['name'],
            'vacation': vacation_type,
            'org_position_id': org_pos,
            'order': max_order + 1 if max_order else 0
        })
        return request.send_info("INF_001")

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-reason-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")


class TimeRegisterReportAPIView(
    generics.GenericAPIView
):
    """ Хувь хүний тайлангийн хуудас
    """
    serializer_class = OrgVacationTypesSerializer
    queryset = OrgVacationTypes.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/time-register-report/index.html'

    @login_required()
    @has_permission(allowed_permissions=['time-register-report-show'])
    def get(self, request, pk=None):
        type_code = None
        employee_id = request.employee.id
        employee_full_name = request.employee.full_name

        if 'time-register-report-employee-show' not in request.permissions:
            if not request.employee.workingtimeschedule_set.last():
                request.send_message("warning", "ERR_016")
                return HttpResponseRedirect('/')

        if request.employee.workingtimeschedule_set.last():

            if pk:
                qs = WorkingTimeSchedule.objects.filter(employees=pk).last()
                employee_qs = Employee.objects.get(pk=pk)
                # Хэрвээ IDтай хэрэглэгч олдохгүй бол өөрийг нь буцаана
                if not qs:
                    type_code = request.employee.workingtimeschedule_set.last().type.code
                    return redirect(
                        to='/schedule/time-register-report/'
                    )
                type_code = qs.type.code
                employee_full_name = employee_qs.full_name
                employee_id = pk

            else:
                type_code = request.employee.workingtimeschedule_set.last().type.code

        return Response(
        {
            'serializer': self.serializer_class,
            'type': type_code,
            'employee_id': employee_id,
            'employee_full_name': employee_full_name
        })


class TimeRegisterReportAjaxAPIView(APIView):
    ''' Тайлангийн хүснэгтийн хариу бодох
    '''

    @login_required()
    @has_permission(allowed_permissions=['time-register-report-show'])
    def post(self, request):

        employee_id = request.data.get('employee')
        reqTimeScheduleType = request.data.get('timeScheduleType')
        timeScheduleType = reqTimeScheduleType if reqTimeScheduleType == 'None' else int(reqTimeScheduleType)

        # Өмнөх энэ жил болон сар
        this_month = now_time.month
        this_year = now_time.year
        before_month = (now_time - relativedelta(months=1)).month
        before_year = (now_time - relativedelta(months=1)).year

        # Хайх утгуудаа хадгална
        filters = {}

        # Хайсны дараа бүх утгуудаа тоолж бодох функц
        def get_value(datas):

            total_hotsorson_seconds = 0

            hotsorson_times = datas.filter(hotsorson_time__isnull=False)
            for hotsorson_time in hotsorson_times:
                total_hotsorson_seconds += (datetime.datetime.strptime(hotsorson_time.hotsorson_time, '%H:%M:%S') - datetime.datetime(1900, 1, 1)).total_seconds() if hotsorson_time.hotsorson_time else 0

            k = int(total_hotsorson_seconds)
            hours = k // 3600
            k = k - (hours * 3600)
            minutes = k // 60
            seconds = k - (minutes * 60)
            hotsorson_time_value = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

            if timeScheduleType == WorkingTimeScheduleType.TYPE_CODE.get('seven_days'):

                kind_working_count = datas.filter(kind=TimeScheduleRegister.KIND_WORKING).count()
                kind_tas_count = datas.filter(kind=TimeScheduleRegister.KIND_TAS).count()
                kind_ajiltai_shaltgaan_count = datas.filter(kind=TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN).count()
                kind_amralt_count = datas.filter(kind=TimeScheduleRegister.KIND_AMRALT).count()
                kind_amralt_shaltgaan_count = datas.filter(kind=TimeScheduleRegister.KIND_AMRALT_SHALTGAAN).count()
                kind_shaltgaan_count = datas.filter(kind=TimeScheduleRegister.KIND_SHALTGAAN).count()
                fine_count = datas.aggregate(Sum('fine')).get('fine__sum')

                if not fine_count:
                    fine_count = 0

                kind_working_day_count = kind_working_count + kind_tas_count + kind_ajiltai_shaltgaan_count
                kind_vacation_day_count = kind_amralt_count + kind_amralt_shaltgaan_count

                serializer = TimeScheduleRegisterReportSerializer(datas, many=True)

                return ({
                    'fine_count': fine_count,

                    'kind_working_count': kind_working_count,
                    'kind_tas_count': kind_tas_count,
                    'kind_ajiltai_shaltgaan_count': kind_ajiltai_shaltgaan_count,
                    'kind_amralt_count': kind_amralt_count,
                    'kind_amralt_shaltgaan_count': kind_amralt_shaltgaan_count,
                    'kind_shaltgaan_count': kind_shaltgaan_count,

                    'kind_working_day_count': kind_working_day_count,
                    'kind_vacation_day_count': kind_vacation_day_count,
                    'hotsorson_time_value': hotsorson_time_value,

                    'table_datas': serializer.data
                })

            if timeScheduleType == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):

                total_seconds = 0

                # Нийт ажилласан цагийг бодно
                worked_times = datas.filter(worked_time__isnull=False)
                for worked_time in worked_times:
                    total_seconds += (datetime.datetime.strptime(worked_time.worked_time, '%H:%M:%S') - datetime.datetime(1900, 1, 1)).total_seconds()

                s = int(total_seconds)
                hours = s // 3600
                s = s - (hours * 3600)
                minutes = s // 60
                seconds = s - (minutes * 60)
                worked_time_value = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                # kind_working_count = datas.filter(kind=TimeScheduleRegister.KIND_WORKING).count()
                kind_tas_count = datas.filter(kind=TimeScheduleRegister.KIND_TAS).count()
                kind_shaltgaan_count = datas.filter(kind=TimeScheduleRegister.KIND_SHALTGAAN).count()
                fine_count = datas.aggregate(Sum('fine')).get('fine__sum')
                worked_time_value_last = worked_time_value

                if not fine_count:
                    fine_count = 0

                serializer = TimeScheduleRegisterReportSerializer(datas, many=True)

                return ({
                    'fine_count': fine_count,

                    # 'kind_working_count': kind_working_count,
                    'kind_tas_count': kind_tas_count,
                    'kind_shaltgaan_count': kind_shaltgaan_count,

                    'table_datas': serializer.data,
                    'worked_time_value': worked_time_value_last,
                    'hotsorson_time_value': hotsorson_time_value,
                })

        # Search-ээр буюу бичиж хайлт хийсэн үед
        if request.data['type'] == 'search':

            # Эхлэх он сарыг барьж авна
            start_year = request.data['start_day'][0:4]
            start_month = request.data['start_day'][5:7]

            # Дуусах хугацааг бөглөсөн бол эхлэхээс дуусах хүртэлхээр шүүнэ
            if (request.data['end_day']):
                end_year = request.data['end_day'][0:4]
                end_month = request.data['end_day'][5:7]
                filters = {
                    'employee': employee_id,
                    'date__year__gte': start_year,
                    'date__month__gte': start_month,
                    'date__year__lte': end_year,
                    'date__month__lte': end_month,
                }
            # Дуусах хугацаа байхгүй бол тэр сарын үйл явдлыг л шүүнэ
            else:
                filters = {
                    'employee': employee_id,
                    'date__year': start_year,
                    'date__month': start_month,
                }

            datas = TimeScheduleRegister.objects.filter(**filters).order_by('date')
            all_values = get_value(datas)

        # Энэ сарынхаар шүүнэ
        elif request.data['type'] == 'thisMonth':
            filters = {
                'employee': employee_id,
                'date__year': this_year,
                'date__month': this_month,
            }

            datas = TimeScheduleRegister.objects.filter(**filters).order_by('date')
            all_values = get_value(datas)

        # Өмнөх сарынхаар шүүнэ
        elif request.data['type'] == 'beforeMonth':
            filters = {
                'employee': employee_id,
                'date__year': before_year,
                'date__month': before_month,
            }

            datas = TimeScheduleRegister.objects.filter(**filters).order_by('date')
            all_values = get_value(datas)

        return request.send_data(all_values)


class AutoTimeBalanceAPIView(
    generics.GenericAPIView
):
    ''' Автомат цагийн баланс
    '''

    serializer_class = WorkingTimeScheduleSerializer
    queryset = WorkingTimeSchedule.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/auto-time-balance/index.html'

    @login_required()
    def get(self, request, pk=None):

        return Response(
        {
            'serializer': self.serializer_class,
        })


class AutoTimeBalanceSevenAjaxAPIView(APIView):

    def post(self, request):
        ''' Баланс тухайн байгууллагын ажилчдын цаг бүртгэлийн дэлгэрэнгүй
        '''
        org = request.org_filter.get('org')

        # Өмнөх энэ жил болон сар
        this_month = now_time.month
        this_year = now_time.year
        before_month = (now_time - relativedelta(months=1)).month
        before_year = (now_time - relativedelta(months=1)).year

        filters_by_xy = {}
        filters_by_seven = {}

        all_data_seven = []
        all_data_xy = []

        # Хайсны дараа бүх утгуудаа тоолж бодох функц
        def get_value(datas_xy, employees_xy, datas_seven, employees_seven):

            for employee_xy in employees_xy:

                save_dict = {}
                for_keys = [
                    'kind_tas_count', 'kind_shaltgaan_count', 'fine_count', 'worked_time_value_last', 'employee_id', 'last_name', 'first_name', 'org_name', 'sub_org_name', 'salbar_name', 'org_position', 'hotsorson_time'
                ]
                total_seconds = 0
                total_hotsorson_seconds = 0

                employee_id = employee_xy.get('employee')

                qs = datas_xy.filter(employee=employee_id)

                last_name = qs[0].employee.user.info.last_name
                first_name = qs[0].employee.user.info.first_name
                org_name = qs[0].employee.org.name
                org_position = qs[0].employee.org_position.name if qs[0].employee.org_position else '-'

                sub_org_name = qs[0].employee.sub_org.name if qs[0].employee.sub_org else '-'
                salbar_name = qs[0].employee.salbar.name if qs[0].employee.salbar else '-'

                # Нийт ажилласан цагийг бодно
                worked_times = qs.filter(worked_time__isnull=False)
                for worked_time in worked_times:
                    total_seconds += (datetime.datetime.strptime(worked_time.worked_time, '%H:%M:%S') - datetime.datetime(1900, 1, 1)).total_seconds()

                s = int(total_seconds)
                hours = s // 3600
                s = s - (hours * 3600)
                minutes = s // 60
                seconds = s - (minutes * 60)
                worked_time_value = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                hotsorson_times = qs.filter(hotsorson_time__isnull=False)
                for hotsorson in hotsorson_times:
                    total_hotsorson_seconds += (datetime.datetime.strptime(hotsorson.hotsorson_time, '%H:%M:%S') - datetime.datetime(1900, 1, 1)).total_seconds() if hotsorson.hotsorson_time else 0

                k = int(total_hotsorson_seconds)
                hours = k // 3600
                k = k - (hours * 3600)
                minutes = k // 60
                seconds = k - (minutes * 60)
                hotsorson_time_value = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                # kind_working_count = qs.filter(kind=TimeScheduleRegister.KIND_WORKING).count()
                kind_tas_count = qs.filter(kind=TimeScheduleRegister.KIND_TAS).count()
                kind_shaltgaan_count = qs.filter(kind=TimeScheduleRegister.KIND_SHALTGAAN).count()
                fine_count = qs.aggregate(Sum('fine')).get('fine__sum')
                worked_time_value_last = worked_time_value
                hotsorson_time = hotsorson_time_value

                if not fine_count:
                    fine_count = 0

                for for_key in for_keys:
                    save_dict[for_key] = eval(for_key)

                all_data_xy.append(save_dict)


            for employee_seven in employees_seven:

                total_hotsorson_seconds = 0
                save_dict = {}
                for_keys = [
                    'kind_working_count', 'kind_tas_count', 'kind_ajiltai_shaltgaan_count', 'kind_amralt_count', 'kind_amralt_shaltgaan_count', 'org_position',
                    'kind_shaltgaan_count', 'fine_count', 'kind_working_day_count', 'kind_vacation_day_count', 'employee_id', 'last_name', 'first_name', 'org_name', 'sub_org_name', 'salbar_name', 'hotsorson_time'
                ]

                employee_id = employee_seven.get('employee')
                qs = datas_seven.filter(employee=employee_id)

                last_name = qs[0].employee.user.info.last_name
                first_name = qs[0].employee.user.info.first_name
                org_name = qs[0].employee.org.name
                org_position = qs[0].employee.org_position.name if qs[0].employee.org_position else '-'

                sub_org_name = qs[0].employee.sub_org.name if qs[0].employee.sub_org else '-'
                salbar_name = qs[0].employee.salbar.name if qs[0].employee.salbar else '-'

                kind_working_count = qs.filter(kind=TimeScheduleRegister.KIND_WORKING).count()
                kind_tas_count = qs.filter(kind=TimeScheduleRegister.KIND_TAS).count()
                kind_ajiltai_shaltgaan_count = qs.filter(kind=TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN).count()
                kind_amralt_count = qs.filter(kind=TimeScheduleRegister.KIND_AMRALT).count()
                kind_amralt_shaltgaan_count = qs.filter(kind=TimeScheduleRegister.KIND_AMRALT_SHALTGAAN).count()
                kind_shaltgaan_count = qs.filter(kind=TimeScheduleRegister.KIND_SHALTGAAN).count()
                fine_count = qs.aggregate(Sum('fine')).get('fine__sum')
                if not fine_count:
                    fine_count = 0

                hotsorson_times = qs.filter(hotsorson_time__isnull=False)
                for hotsorson in hotsorson_times:
                    total_hotsorson_seconds += (datetime.datetime.strptime(hotsorson.hotsorson_time, '%H:%M:%S') - datetime.datetime(1900, 1, 1)).total_seconds() if hotsorson.hotsorson_time else 0

                k = int(total_hotsorson_seconds)
                hours = k // 3600
                k = k - (hours * 3600)
                minutes = k // 60
                seconds = k - (minutes * 60)
                hotsorson_time_value = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                kind_working_day_count = kind_working_count + kind_tas_count + kind_ajiltai_shaltgaan_count
                kind_vacation_day_count = kind_amralt_count + kind_amralt_shaltgaan_count

                hotsorson_time = hotsorson_time_value

                for for_key in for_keys:
                    save_dict[for_key] = eval(for_key)

                all_data_seven.append(save_dict)


        # Search-ээр буюу бичиж хайлт хийсэн үед
        if request.data['type'] == 'search':

            # Эхлэх он сарыг барьж авна
            start_year = request.data['start_day'][0:4]
            start_month = request.data['start_day'][5:7]

            # Дуусах хугацааг бөглөсөн бол эхлэхээс дуусах хүртэлхээр шүүнэ
            if (request.data['end_day']):
                end_year = request.data['end_day'][0:4]
                end_month = request.data['end_day'][5:7]

                # XY
                filters_by_xy = {
                    'employee__org': org.id,
                    'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('xy_days'),
                    'date__year__gte': start_year,
                    'date__month__gte': start_month,
                    'date__year__lte': end_year,
                    'date__month__lte': end_month,
                }

                # Seven
                filters_by_seven = {
                    'employee__org': org.id,
                    'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('seven_days'),
                    'date__year__gte': start_year,
                    'date__month__gte': start_month,
                    'date__year__lte': end_year,
                    'date__month__lte': end_month,
                }


            # Дуусах хугацаа байхгүй бол тэр сарын үйл явдлыг л шүүнэ
            else:
                # XY
                filters_by_xy = {
                    'employee__org': org.id,
                    'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('xy_days'),
                    'date__year': start_year,
                    'date__month': start_month,
                }

                # Seven
                filters_by_seven = {
                    'employee__org': org.id,
                    'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('seven_days'),
                    'date__year': start_year,
                    'date__month': start_month,
                }

            datas_xy = TimeScheduleRegister.objects.filter(**filters_by_xy)
            datas_seven = TimeScheduleRegister.objects.filter(**filters_by_seven)

            employees_xy = TimeScheduleRegister.objects.filter(**filters_by_xy).values('employee').distinct()
            employees_seven = TimeScheduleRegister.objects.filter(**filters_by_seven).values('employee').distinct()

            all_values = get_value(datas_xy, employees_xy, datas_seven, employees_seven)

        # Энэ сарынхаар шүүнэ
        elif request.data['type'] == 'thisMonth':

            # XY
            filters_by_xy = {
                'employee__org': org.id,
                'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('xy_days'),
                'date__year': this_year,
                'date__month': this_month,
            }

            # Seven
            filters_by_seven = {
                'employee__org': org.id,
                'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('seven_days'),
                'date__year': this_year,
                'date__month': this_month,
            }

            datas_xy = TimeScheduleRegister.objects.filter(**filters_by_xy)
            datas_seven = TimeScheduleRegister.objects.filter(**filters_by_seven)

            employees_xy = TimeScheduleRegister.objects.filter(**filters_by_xy).values('employee').distinct()
            employees_seven = TimeScheduleRegister.objects.filter(**filters_by_seven).values('employee').distinct()

            all_values = get_value(datas_xy, employees_xy, datas_seven, employees_seven)

        # Өмнөх сарынхаар шүүнэ
        elif request.data['type'] == 'beforeMonth':
            # XY
            filters_by_xy = {
                'employee__org': org.id,
                'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('xy_days'),
                'date__year': before_year,
                'date__month': before_month,
            }

            # Seven
            filters_by_seven = {
                'employee__org': org.id,
                'employee__workingtimeschedule__type': WorkingTimeScheduleType.TYPE_CODE.get('seven_days'),
                'date__year': before_year,
                'date__month': before_month,
            }

            datas_xy = TimeScheduleRegister.objects.filter(**filters_by_xy)
            datas_seven = TimeScheduleRegister.objects.filter(**filters_by_seven)

            employees_xy = TimeScheduleRegister.objects.filter(**filters_by_xy).values('employee').distinct()
            employees_seven = TimeScheduleRegister.objects.filter(**filters_by_seven).values('employee').distinct()

            all_values = get_value(datas_xy, employees_xy, datas_seven, employees_seven)

        all_values = { 'all_data_seven': all_data_seven, 'all_data_xy': all_data_xy }

        return request.send_data(all_values)


class SpecialLeaveAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """ Тусгай баярын өдрүүд
    """

    serializer_class = HolidayDayInYearSerializer
    queryset = HolidayDayInYear.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/special-leave/index.html'

    @login_required()
    # @has_permission(allowed_permissions=['create-vacation-type-read'])
    def get(self, request, pk=None):

        return Response({
            'serializer': self.serializer_class
        })


class SpecialLeaveEveryYearJson(APIView):
    def get(self, request):
        ''' Жил болгоны амралтын өдөрүүдийн datatable-ийн утгыг авна
        '''

        org_id = request.org_filter.get('org').id

        qs = HolidayDayInYear.objects.filter(every_year=True, org__id=org_id).order_by('-date')
        paginated = data_table(qs, request)
        paginated['data'] = HolidayDayInYearSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class SpecialLeaveEveryYearAjaxAPIView(APIView):
    ''' Жил болгоны өдөрүүд ajax
    '''

    def get_object(self, pk, request):
        try:
            return HolidayDayInYear.objects.get(pk=pk)
        except HolidayDayInYear.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = HolidayDayInYearSerializer(snippet)
        return request.send_data(serializer.data)

    def post(self, request, pk=None):

        org_id = request.org_filter.get('org').id

        datas = {}

        for key in request.data:
            datas[key] = request.data[key]
        datas['org'] = org_id
        datas['every_year'] = True

        qs_coincidence = HolidayDayInYear.objects.filter(date__year=1900, date__month=datas["month"], date__day=datas["date"])

        if qs_coincidence:
            raise request.send_error("ERR_002", "он сар")

        datas['date'] = f'1900-{datas["month"]}-{datas["date"]}'
        datas.pop('month')

        serializer = HolidayDayInYearSerializer(data=datas)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        return request.send_info('INF_015')

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-create-and-edit'])
    def put(self, request, pk=None):

        datas = request.data

        qs_coincidence = HolidayDayInYear.objects.filter(date__year=1900, date__month=datas["month"], date__day=datas["date"])

        if qs_coincidence:
            raise request.send_error("ERR_002", "он сар")

        datas['date'] = f'1900-{datas["month"]}-{datas["date"]}'
        datas.pop('month')

        snippet = HolidayDayInYear.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")


class SpecialLeaveChosedYearJsonAPIView(APIView):
    def get(self, request):
        ''' Жил болгоны амралтын өдөрүүдийн datatable-ийн утгыг авна
        '''
        year = request.GET['year']
        searchYear = request.GET.get('searchYear')

        if searchYear:
            year = searchYear

        qs = HolidayDayInYear.objects.filter(every_year=False, year=year)

        paginated = data_table(qs, request)
        paginated['data'] = HolidayDayInYearSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class SpecialLeaveChosedYearAjaxAPIView(APIView):
    ''' Жил болгоны өдөрүүд ajax
    '''

    def get_object(self, pk, request):
        try:
            return HolidayDayInYear.objects.get(pk=pk)
        except HolidayDayInYear.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = HolidayDayInYearSerializer(snippet)
        return request.send_data(serializer.data)

    def post(self, request, pk=None):

        org_id = request.org_filter.get('org').id

        datas = {}

        for key in request.data:
            datas[key] = request.data[key]
        datas['org'] = org_id
        datas['every_year'] = False

        qs_coincidence = HolidayDayInYear.objects.filter(date__year=datas["year"], date__month=datas["month"], date__day=datas["date"])
        if qs_coincidence:
            raise request.send_error("ERR_002", "он сар")

        datas['date'] = f'{datas["year"]}-{datas["month"]}-{datas["date"]}'
        datas.pop('month')
        datas['name'] = datas['chosedName']
        datas.pop('chosedDate')

        serializer = HolidayDayInYearSerializer(data=datas)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        return request.send_info('INF_015')

    @login_required()
    @has_permission(allowed_permissions=['create-vacation-type-create-and-edit'])
    def put(self, request, pk=None):

        datas = request.data

        qs_coincidence = HolidayDayInYear.objects.filter(date__year=datas["year"], date__month=datas["month"], date__day=datas["date"])
        if qs_coincidence:
            raise request.send_error("ERR_002", "он сар")

        datas['date'] = f'{datas["year"]}-{datas["month"]}-{datas["date"]}'
        datas.pop('month')
        datas['name'] = datas['chosedName']
        datas.pop('chosedDate')
        datas.pop('chosedName')
        datas.pop('chosedId')

        snippet = HolidayDayInYear.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")


class TimeRegisterRequestPrintAPIView(
    generics.GenericAPIView
):
    ''' Чөлөөний хуудас хэвлэх
    '''
    serializer_class = RequestTimeVacationRegisterGetSerializer
    queryset = RequestTimeVacationRegister.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/time-register-request-solve/print/index.html'

    def get_object(self, pk, request):
        try:
            return RequestTimeVacationRegister.objects.get(pk=pk)
        except RequestTimeVacationRegister.DoesNotExist:
            raise request.send_error("ERR_003")

    def get(self, request, pk=None):

        snippet = self.get_object(pk, request)
        serializer = self.serializer_class(snippet, many=False)

        return Response(serializer.data)


class TimeRegisterRequestOrgPosAPIView(APIView):

    def get(self, request, pk, req_id):

        org_vac_type_qs = OrgVacationTypesBranchTypes.objects.filter(vacation_id=pk)
        data = OrgVacationTypesDetailSerializer(org_vac_type_qs, context={ "req_id": req_id }, many=True).data

        return request.send_data(data)


class TimeRegisterRequestOrgPosAgreeAPIView(APIView):
    ''' Хүсэлтийг зөвшөөрөх
    '''

    @login_required()
    def put(self, request, pk=None):

        vacation_id = request.GET.get("vacation")
        employeeId = request.employee.id
        org_position_id = request.employee.org_position_id

        vacation_branch_types_count = OrgVacationTypesBranchTypes.objects.filter(vacation_id=vacation_id).count()

        Correspond_Answer.objects.create(
            request_id=pk,
            org_position_id=org_position_id,
            date=datetime.datetime.now().date(),
            is_confirm=True,
            employee_id=employeeId,
        )

        answer_count = Correspond_Answer.objects.filter(request__vacation_type_id=vacation_id).count()

        if answer_count == vacation_branch_types_count:
            qs = RequestTimeVacationRegister.objects.filter(pk=pk)
            qs.update(
                status=RequestTimeVacationRegister.AGREE,
            )

        return request.send_info("INF_015")


class TimeRegisterRequestOrgPosDeclineAPIView(APIView):
    ''' Хүсэлтийг татгалзах
    '''

    @login_required()
    def put(self, request, pk=None):

        detail = request.data.get('reason_for_rejection')

        employeeId = request.employee.id
        org_position_id = request.employee.org_position_id

        Correspond_Answer.objects.create(
            request_id=pk,
            org_position_id=org_position_id,
            date=datetime.datetime.now().date(),
            is_confirm=False,
            message=detail,
            employee_id=employeeId,
        )

        qs = RequestTimeVacationRegister.objects.filter(pk=pk)
        qs.update(
            status=RequestTimeVacationRegister.DECLINE,
        )

        return request.send_info("INF_002")


class Vacation(
    generics.GenericAPIView

):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/vacation/index.html'

    def get(self, request):

        return Response()


class YearVacationAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = VacationEmployeeSerializer
    queryset = VacationEmployee.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/year-vacation/index.html'

    @login_required()
    def get(self, request, pk=None):

        check_request = VacationEmployee.objects.filter(
            employee=request.employee,
            start_date__year=datetime.datetime.today().year,
            state__in=[VacationEmployee.APPROVED, VacationEmployee.WAITING]
        ).exists()


        return Response({
            'check_request': check_request
        })

    @login_required()
    def post(self, request, pk=None):
        """ Шинээр үүсгэх
        """

        request.data._mutable = True
        request.data['employee'] = request.employee.id
        request.data._mutable = False

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('year-vacation')


class YearVacationJson(APIView):
    def get(self, request):
        ''' Жилээсээ шалтгаалж ээлжийн амралтын дататаблэ
        '''

        year = request.GET.get('year')

        qs = VacationEmployee.objects.filter(start_date__year=year, employee=request.employee)
        paginated = data_table(qs, request)
        paginated['data'] = VacationEmployeeSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class YearVacationCancelAPIView(
    generics.GenericAPIView,
):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/year-vacation/index.html'

    @login_required()
    def post(self, request):
        """ Шинээр үүсгэх
        """
        id = request.data.get('cancel_input')

        VacationEmployee.objects.filter(id=id).update(state=VacationEmployee.CANCEL)
        request.send_message('success', 'INF_007')
        return redirect('year-vacation')


class YearVacationDecidingAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = VacationEmployeeSerializer
    queryset = VacationEmployee.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/year-vacation-deciding/index.html'

    @login_required()
    def get(self, request, pk=None):

        return Response({})


class YearVacationDecidingJson(APIView):
    def get(self, request):
        ''' Жилээсээ шалтгаалж ээлжийн амралтын дататаблэ
        '''

        year = request.GET.get('year')

        qs = VacationEmployee.objects.filter(
            start_date__year=year,
            state__in=[VacationEmployee.APPROVED,VacationEmployee.DECLINED, VacationEmployee.WAITING],
            employee__user__userinfo__action_status=UserInfo.APPROVED,
            employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
        ).annotate(
            full_name=Concat(Upper(Substr("employee__user__userinfo__last_name", 1, 1)), Value(". "), "employee__user__userinfo__first_name")
        )

        paginated = data_table(qs, request)
        paginated['data'] = VacationEmployeeDecidingSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class YearVacationDeclineAPIView(
    generics.GenericAPIView,
):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/year-vacation-deciding/index.html'

    @login_required()
    def post(self, request):
        """ Ээлжийн амралт цуцлах
        """

        id = request.data.get('cancel_input')

        VacationEmployee.objects.filter(id=id).update(state=VacationEmployee.DECLINED)
        request.send_message('success', 'INF_007')
        return redirect('year-vacation-deciding')


class YearVacationApproveAPIView(
    generics.GenericAPIView,
):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/schedule/year-vacation-deciding/index.html'

    @login_required()
    def post(self, request):
        """ Ээлжийн амралт зөвшөөрөх
        """

        id = request.data.get('approve_input')

        VacationEmployee.objects.filter(id=id).update(
            state=VacationEmployee.APPROVED,
            start_date=request.data['start_date'],
            days=request.data['days'],
        )
        request.send_message('success', 'INF_007')
        return redirect('year-vacation-deciding')
