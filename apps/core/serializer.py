from rest_framework import serializers

from core.models import Orgs
from core.models import TimeScheduleRegister
from core.models import SubOrgs
from core.models import Salbars
from core.models import OrgPosition
from core.models import Employee

from main.utils.file import get_file_field_exists


def get_query(context):
    request = context.get("request")
    query = request.GET.get("choices")
    return query


def need_children(context):
    """ children ийг авах хэрэгтэй эсэх """
    query = get_query(context)
    if query == 'songolt-sub-org':
        return False, query
    if query == 'songolt-position':
        return False, query

    return True, query


class EmployeeJsonSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source="user.real_photo", default="")
    pos_name = serializers.CharField(source="org_position.name", default="")

    class Meta:
        model = Employee
        fields = "__all__"

    def get_name(self, obj):
        first_name = obj.user.info.first_name
        last_name = obj.user.info.last_name
        return f"{last_name} {first_name}"


class OrgPositionJsonSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    top_name = serializers.CharField(source="org.name")

    class Meta:
        model = OrgPosition
        fields = "__all__"

    def get_children(self, obj):
        need, query = need_children(self.context)
        if not need:
            return []
        return EmployeeJsonSerializer(obj.employee_set.filter(state=Employee.STATE_WORKING), many=True).data


class SalbarJsonSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source="logo")
    top_name = serializers.SerializerMethodField()

    class Meta:
        model = Salbars
        fields = "__all__"

    def get_top_name(self, obj):
        if obj.parent:
            return obj.parent.name
        else:
            return obj.sub_orgs.name

    def get_children(self, obj):
        query = get_query(self.context)
        if query != 'songolt-employee':
            return []

        request = self.context.get("request")

        #  alban tushaalaar tsegtselsen ajilchidiin jagsaaal awah ni
        position_ids = list(obj.employee_set.filter(state=Employee.STATE_WORKING).values_list("org_position_id", flat=True))
        position_qs = OrgPosition.objects.filter(id__in=position_ids)
        data = OrgPositionJsonSerializer(position_qs, many=True, context={ "request": request }).data
        return data


class SubOrgJsonSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source="logo")
    top_name = serializers.CharField(source="org.name")

    class Meta:
        model = SubOrgs
        fields = "__all__"

    def get_children(self, obj):
        request = self.context.get("request")
        need, query = need_children(self.context)
        if not need:
            return []

        qs = obj.salbars_set
        return SalbarJsonSerializer(qs, many=True, context={ "request": request }).data


class OrgJsonSerializer(serializers.ModelSerializer):

    org_positions = OrgPositionJsonSerializer(source="orgposition_set", many=True)
    sub_orgs = SubOrgJsonSerializer(source="suborgs_set", many=True)

    class Meta:
        model = Orgs
        fields = "__all__"


class AllEmployeeSeriliazer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    avatar = serializers.FileField(source="user.real_photo", default="")

    class Meta:
        model = Employee
        fields = "__all__"

    def get_name(self, obj):
        first_name = obj.user.info.first_name
        last_name = obj.user.info.last_name
        return f"{last_name} {first_name}"


## -----------

class OrgToEmployeeEmployeeJsonSerializer(serializers.ModelSerializer):

    type = serializers.IntegerField(source="id")
    text = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "text", 'type', 'id'

    def get_text(self, obj):
        first_name = obj.user.info.first_name
        last_name = obj.user.info.last_name
        return f"{last_name} {first_name}"

    def get_id(self, obj):
        return f"emp_{obj.id}"


class OrgToEmployeeOrgPositionJsonSerializer(serializers.ModelSerializer):

    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")
    children = serializers.SerializerMethodField()

    class Meta:
        model = OrgPosition
        fields = "type", 'text', "children"

    def get_children(self, obj):
        employee_ids = self.context.get("employee_ids")
        return OrgToEmployeeEmployeeJsonSerializer(
            obj.employee_set.filter(state=Employee.STATE_WORKING, id__in=employee_ids),
            many=True
        ).data


def get_employees(filters):
    positions = list(Employee.objects.filter(**filters).distinct("org_position_id").values_list("org_position_id", flat=True))
    employee_ids = list(Employee.objects.filter(**filters).values_list("id", flat=True))
    employees = OrgToEmployeeOrgPositionJsonSerializer(
        OrgPosition.objects.filter(id__in=positions),
        many=True,
        context={
            "employee_ids": employee_ids
        }
    ).data
    extra = {
        "text": "Ажилчид",
        "icon": "fa fa-user",
        "children": employees,
        "state": {
            "disabled": len(employees) == 0,
        }
    }
    return extra


class OrgToEmployeeSalbarSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")

    class Meta:
        model = Salbars
        fields = "type", 'text', "children"

    def get_children(self, obj):
        extra = get_employees({
            "org": obj.org,
            "sub_org": obj.sub_orgs,
            "salbar_id": obj.id,
        })

        children = OrgToEmployeeSalbarSerializer(
            Salbars.objects.filter(
                parent_id=obj.id
            ),
            many=True,
        ).data

        children.append(extra)
        return children


class OrgToEmployeeSubOrgSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")

    class Meta:
        model = SubOrgs
        fields = "type", 'text', 'children'

    def get_children(self, obj):
        extra = get_employees({
            "org": obj.org,
            "sub_org_id": obj.id,
            "salbar": None,
        })

        children = OrgToEmployeeSalbarSerializer(
            obj.salbars_set.filter(branch_pos=0),
            many=True
        ).data
        children.append(extra)
        return children


class OrgToEmployeeSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")

    class Meta:
        model = Orgs
        fields = "type", 'text', 'children'

    def get_children(self, obj):
        extra = get_employees({
            "org_id": obj.id,
            "sub_org": None,
            "salbar": None
        })

        children = OrgToEmployeeSubOrgSerializer(
            obj.suborgs_set,
            many=True
        ).data
        children.append(extra)
        return children


class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orgs
        fields = "__all__"


class HomeTimeRegisterSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    pos_name = serializers.SerializerMethodField()
    f_in_dt = serializers.SerializerMethodField()
    f_out_dt = serializers.SerializerMethodField()

    profile_img = serializers.SerializerMethodField()
    has_img = serializers.SerializerMethodField()

    class Meta:
        model = TimeScheduleRegister
        fields = "full_name", 'f_in_dt', 'f_out_dt', 'pos_name', 'profile_img', 'has_img'

    def get_full_name(self, obj):
        return obj.full_name

    def get_pos_name(self, obj):
        return obj.pos_name

    def get_f_in_dt(self, obj):
        return obj.f_in_dt

    def get_f_out_dt(self, obj):
        return obj.f_out_dt

    def get_profile_img(self, obj):
        return obj.employee.real_photo.url if obj.employee.real_photo else ""

    def get_has_img(self, obj):
        return get_file_field_exists(obj.employee.real_photo)
