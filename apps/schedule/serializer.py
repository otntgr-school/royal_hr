
from rest_framework import serializers

from django.db.models import Q

from core.models import TimeScheduleType
from core.models import WorkingTimeSchedule
from core.models import WorkingTimeScheduleType
from core.models import TimeScheduleRegister
from core.models import Orgs
from core.models import User
from core.models import UserInfo
from core.models import Employee
from core.models import RequestTimeVacationRegister
from core.models import SubOrgs
from core.models import Salbars
from core.models import OrgPosition
from core.models import OrgVacationTypes
from core.models import OrgVacationTypesBranchTypes
from core.models import HolidayDayInYear
from core.models import Correspond_Answer
from core.models import VacationEmployee


class OrgVacationTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrgVacationTypes
        fields = '__all__'


class OrgVacationTypesBranchTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrgVacationTypesBranchTypes
        fields = '__all__'


class TimeScheduleTypeAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeScheduleType
        fields = '__all__'


class WorkingTimeScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingTimeSchedule
        fields = '__all__'


class OrgsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orgs
        fields = '__all__'


class TimeScheduleRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeScheduleRegister
        fields = '__all__'


class EmployeeTimeScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'


class UserInfoRegisterEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInfo
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = 'username', 'id'


class WorkingTimeScheduleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingTimeScheduleType
        fields = 'code', 'name'


class SubOrgsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubOrgs
        fields = 'id', 'name'


class SalbarsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Salbars
        fields = 'id', 'name'


class OrgPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrgPosition
        fields = 'id', 'name'


class WorkingTimeScheduleJsonSerializer(serializers.ModelSerializer):

    type = WorkingTimeScheduleTypeSerializer(many=False)

    class Meta:
        model = WorkingTimeSchedule
        fields = '__all__'


class WorkingTimeScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingTimeSchedule
        fields = '__all__'


class OrgVacationTypesAndReasonSerializer(serializers.ModelSerializer):

    reason = OrgVacationTypesBranchTypesSerializer(source="orgvacationtypesbranchtypes_set", many=True)

    class Meta:
        model = OrgVacationTypes
        fields = 'id', 'times', 'name', 'one_day_vacation', 'many_days_vacation', 'reason'


class WorkingTimeScheduleTypeCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingTimeSchedule
        fields = 'id', 'type'


class TimeScheduleTypeSerializer(serializers.ModelSerializer):

    name = serializers.CharField(style={ "placeholder": "Ажлын цагийн төрлийн нэр" }, label="Ажлын цагийн төрлийн нэр")
    # uyn_khatan = serializers.BooleanField(style={"template": "form/checkbox.html"}, label="Уян хатан хуваарь")
    start_time = serializers.TimeField(style={"template": "form/time.html"}, label="Эхлэх цаг")
    hotorch_boloh_limit = serializers.TimeField(style={"template": "form/time.html"}, label="Хэд хүртэл хоцорч болох")
    end_time = serializers.TimeField(style={"template": "form/time.html"}, label="Дуусах цаг")
    lunch_time_start_time = serializers.TimeField(style={"template": "form/time.html"}, label="Цайны цаг")
    # lunch_time_end_time = serializers.TimeField(style={"template": "form/time.html"}, label="Цайны цаг дуусах")
    # registration_start_time = serializers.TimeField(style={"template": "form/time.html"}, label="Ирсэн цаг бүртгэж эхлэх хугацаа")
    # registration_end_time = serializers.TimeField(style={"template": "form/time.html"}, label="Явсан цаг бүртгэж дуусах хугацаа")
    time_range = serializers.IntegerField(label="Ажиллах цаг", style={ "placeholder": "Ажиллах цаг" })

    class Meta:
        model = TimeScheduleType
        exclude = ['org', 'registration_start_time', 'registration_end_time', 'uyn_khatan', 'lunch_time_end_time']


class TimeScheduleTypeFormSerializer(serializers.ModelSerializer):

    name = serializers.CharField(style={ "placeholder": "Ажлын цагийн төрлийн нэр" }, label="Ажлын цагийн төрлийн нэр")
    start_time = serializers.TimeField(style={"template": "form/time.html"}, label="Эхлэх цаг")
    end_time = serializers.TimeField(style={"template": "form/time.html"}, label="Дуусах цаг")
    time_range = serializers.IntegerField(label="Ажиллах цаг", style={ "placeholder": "Ажиллах цаг" })

    class Meta:
        model = TimeScheduleType
        exclude = ['org', 'registration_start_time', 'registration_end_time', 'uyn_khatan', 'lunch_time_end_time', 'lunch_time_start_time', 'hotorch_boloh_limit']


class WorkingTimeScheduleSerializerAjax(serializers.ModelSerializer):

    type = WorkingTimeScheduleTypeSerializer(many=False)
    mon_time_schedule = TimeScheduleTypeSerializer(many=False)
    tue_time_schedule = TimeScheduleTypeSerializer(many=False)
    wed_time_schedule = TimeScheduleTypeSerializer(many=False)
    thu_time_schedule = TimeScheduleTypeSerializer(many=False)
    fri_time_schedule = TimeScheduleTypeSerializer(many=False)
    sat_time_schedule = TimeScheduleTypeSerializer(many=False)
    sun_time_schedule = TimeScheduleTypeSerializer(many=False)
    org = OrgsSerializer(many=False)

    class Meta:
        model = WorkingTimeSchedule
        fields = '__all__'


class UserRegisterEmployeeSerializer(serializers.ModelSerializer):

    user_info = UserInfoRegisterEmployeeSerializer(source="userinfo_set.first", many=False)

    class Meta:
        model = User
        fields = 'user_info', 'id', 'phone_number', 'email'


class EmployeeTimeScheduleByRequestSerializer(serializers.ModelSerializer):

    user = UserRegisterEmployeeSerializer(many=False)
    org = OrgsSerializer(many=False)
    sub_org = SubOrgsSerializer(many=False)
    salbar = SalbarsSerializer(many=False)
    org_position = OrgPositionSerializer(many=False)

    class Meta:
        model = Employee
        fields = '__all__'



class RequestTimeVacationRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestTimeVacationRegister
        fields = '__all__'


class RequestTimeVacationRegisterJsonSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    employee = EmployeeTimeScheduleByRequestSerializer(many=False)

    class Meta:
        model = RequestTimeVacationRegister
        fields = '__all__'


class RequestTimeVacationRegisterFirstNameJsonSerializer(serializers.ModelSerializer):

    is_need_answer = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    employee = EmployeeTimeScheduleByRequestSerializer(many=False)
    first_name = serializers.SerializerMethodField()

    class Meta:
        model = RequestTimeVacationRegister
        fields = '__all__'

    def get_first_name(self, obj):
        return obj.first_name

    def get_is_need_answer(self, obj):

        answer = False

        request = self.context['request']
        my_org_pos = request.employee.org_position_id
        vacation_type = obj.vacation_type

        correspond_answer_qs = Correspond_Answer.objects.filter(request_id=obj.id, is_confirm=False)

        if correspond_answer_qs:
            return answer

        correspond_answer_qs = Correspond_Answer.objects.filter(request_id=obj.id).values_list('org_position', flat=True).distinct()
        types_branch_org_positions = OrgVacationTypesBranchTypes.objects.filter(vacation=vacation_type).values_list('org_position', flat=True).distinct()

        minus_list = list(set(types_branch_org_positions) - set(correspond_answer_qs))

        if my_org_pos in minus_list:
            answer = True

        return answer


class RequestTimeVacationRegisterJsonV2Serializer(serializers.ModelSerializer):

    vacation_type = serializers.SerializerMethodField()

    class Meta:
        model = RequestTimeVacationRegister
        fields = '__all__'

    def get_vacation_type(self, obj):
        if obj.special_reason:
            return f"{obj.special_reason.name}"

        return f"{obj.vacation_type.name}"


class TimeScheduleRegisterDataTableSerializer(serializers.ModelSerializer):

    employee = EmployeeTimeScheduleSerializer(many=False)
    for_shaltgaan = RequestTimeVacationRegisterJsonV2Serializer(many=False)

    in_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    out_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    lunch_in_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    lunch_out_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))

    class Meta:
        model = TimeScheduleRegister
        fields = 'in_dt', 'out_dt', 'date', 'id', 'worked_time', 'employee', 'kind', 'for_shaltgaan', 'fine', 'lunch_out_dt', 'lunch_in_dt'


class EmployeeSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    register = serializers.SerializerMethodField()
    ex_sub_org_id = serializers.SerializerMethodField()
    start_date = serializers.CharField(source="xytimeschedulevalues.start_date", default='')
    type = WorkingTimeScheduleTypeCodeSerializer(source="workingtimeschedule_set.last", many=False)

    class Meta:
        model = Employee
        fields = '__all__'

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_register(self, obj):
        return obj.register

    def get_ex_sub_org_id(self, obj):
        return obj.sub_org.name if obj.sub_org else ''


class RequestTimeVacationRegisterReportJsonSerializer(serializers.ModelSerializer):

    vacation_type = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    resolved_date = serializers.DateTimeField(format=("%Y-%m-%d %H:%M"))

    class Meta:
        model = RequestTimeVacationRegister
        fields = '__all__'

    def get_vacation_type(self, obj):
        if obj.special_reason:
            return f"{obj.special_reason.name}"

        return f"{obj.vacation_type.name}"


class TimeScheduleRegisterReportSerializer(serializers.ModelSerializer):

    kind = serializers.CharField(source="get_kind_display")
    for_shaltgaan = RequestTimeVacationRegisterReportJsonSerializer(many=False)

    in_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    out_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    lunch_in_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    lunch_out_dt = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))

    class Meta:
        model = TimeScheduleRegister
        fields = '__all__'


class HolidayDayInYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = HolidayDayInYear
        fields = '__all__'


class Correspond_AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Correspond_Answer
        fields = '__all__'


class OrgVacationTypesDetailSerializer(serializers.ModelSerializer):

    answers = serializers.SerializerMethodField()
    org_position = OrgPositionSerializer(many=False)

    class Meta:
        model = OrgVacationTypesBranchTypes
        fields = '__all__'

    def get_answers(self, obj):

        req_id = self.context['req_id']
        org_postition_qs = obj.org_position

        corrospond_qs = Correspond_Answer.objects.filter(org_position_id=org_postition_qs.id, request_id=req_id).last()
        corrospond_data = Correspond_AnswerSerializer(corrospond_qs, many=False).data if corrospond_qs else None

        return corrospond_data


class Correspond_AnswerPrintSerializer(serializers.ModelSerializer):

    employee = EmployeeTimeScheduleByRequestSerializer(many=False)

    class Meta:
        model = Correspond_Answer
        fields = '__all__'


class OrgVacationTypesDetailPrintSerializer(serializers.ModelSerializer):

    answers = serializers.SerializerMethodField()
    org_position = OrgPositionSerializer(many=False)

    class Meta:
        model = OrgVacationTypesBranchTypes
        fields = '__all__'

    def get_answers(self, obj):

        req_id = self.context['req_id']

        corrospond_qs = Correspond_Answer.objects.filter(org_position_id=obj.org_position.id, request_id=req_id).last()
        corrospond_data = Correspond_AnswerPrintSerializer(corrospond_qs, many=False).data if corrospond_qs else None

        return corrospond_data


class RequestTimeVacationRegisterGetSerializer(serializers.ModelSerializer):

    branch_types = serializers.SerializerMethodField()
    employee = EmployeeTimeScheduleByRequestSerializer(many=False)

    class Meta:
        model = RequestTimeVacationRegister
        fields = '__all__'

    def get_branch_types(self, obj):

        types_qs = OrgVacationTypesBranchTypes.objects.filter(vacation_id=obj.vacation_type_id).order_by('order')
        types_data = OrgVacationTypesDetailPrintSerializer(types_qs, context={ 'req_id': obj.id },  many=True).data

        return types_data


class VacationEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = VacationEmployee
        fields = '__all__'


class VacationEmployeeDecidingSerializer(serializers.ModelSerializer):

    employee = EmployeeTimeScheduleByRequestSerializer(many=False)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = VacationEmployee
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.full_name
