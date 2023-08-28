import datetime
import os

from rest_framework import serializers

from core.models import StaticGroupSkills
from core.models import StaticSkills
from core.models import StaticSkillsDefinations
from core.models import EmployeeDonation
from core.models import Orgs
from core.models import Salbars
from core.models import SubOrgs
from core.models import Tomilolt
from core.models import Employee
from core.models import Attachments
from core.models import ForTomilolt
from core.models import OtherImages
from core.models import ChigluulehHutulbur
from core.models import EmployeeMigrations
from core.models import Command
from core.models import RoutingSlip
from core.models import RoutingSlipCommanders
from core.models import UserExperience
from core.models import KhodolmoriinGeree
from core.models import AnketEmployee
from core.models import NewEmployeeRegistrationForm

from main.utils.file import get_extension, get_file_field_exists
from main.utils.file import get_name_from_path
from main.utils.file import calc_size
from main.utils.file import get_content_type
from main.utils.file import get_attachment_url


class OrgsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orgs
        fields = '__all__'


class AnketEmployeeSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M"), read_only=True)

    class Meta:
        model = AnketEmployee
        fields = '__all__'

    def get_file_name(self, obj):

        return os.path.basename(obj.file.name)


class NewEmployeeRegistrationFormSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M"), read_only=True)

    class Meta:
        model = NewEmployeeRegistrationForm
        fields = '__all__'

    def get_file_name(self, obj):

        return os.path.basename(obj.file.name)


class AttachmentsDisplaySerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    ext = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    pure_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    has_file = serializers.SerializerMethodField()

    class Meta:
        model = Attachments
        exclude = "file",

    def get_url(self, obj):
        is_pub = self.context.get("public")
        return get_attachment_url(obj.id) if is_pub == False else obj.file.url

    def get_name(self, obj):
        name = obj.file.name
        return get_name_from_path(name)

    def get_ext(self, obj):
        path = obj.file.path
        return "".join(get_extension(path))

    def get_size(self, obj):
        size = obj.file.size if get_file_field_exists(obj.file) else ""
        return calc_size(size) if size else 0

    def get_pure_size(self, obj):
        return obj.file.size if get_file_field_exists(obj.file) else 0

    def get_mime_type(self, obj):
        data = get_content_type(obj.file.path)
        return data[0]

    def get_has_file(self, obj):
        return get_file_field_exists(obj.file)


class EmployeePaginationSerializer(serializers.ModelSerializer):

    sub_org__name = serializers.CharField(source="sub_org.name", default="")
    salbar__name = serializers.CharField(source="salbar.name", default="")
    org_position__name = serializers.CharField(source="org_position.name", default="")
    position_id = serializers.IntegerField(source="org_position_id")

    cfirst_name = serializers.SerializerMethodField()
    clast_name = serializers.SerializerMethodField()
    cregister = serializers.SerializerMethodField()
    cemdd_number = serializers.SerializerMethodField()
    cndd_number = serializers.SerializerMethodField()
    caddress = serializers.SerializerMethodField()
    curgiin_ovog = serializers.SerializerMethodField()
    gender_name = serializers.SerializerMethodField()

    unit1_name = serializers.SerializerMethodField()
    unit2_name = serializers.SerializerMethodField()
    cemail = serializers.SerializerMethodField()
    cphone_number = serializers.SerializerMethodField()

    ex_csub_org_id = serializers.SerializerMethodField()

    profile_img = serializers.SerializerMethodField()
    has_img = serializers.SerializerMethodField()

    anket = serializers.SerializerMethodField()
    new_employee_registration_form = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            "sub_org__name",
            'salbar__name',
            'org_position__name',
            'cemail',
            'sub_org_id',
            'salbar_id',
            'id',
            'state',
            'position_id',
            'cfirst_name',
            'clast_name',
            'cregister',
            'cemdd_number',
            'cndd_number',
            'caddress',
            'curgiin_ovog',
            'cphone_number',
            'gender_name',
            "unit1_name",
            "unit2_name",
            'profile_img',
            'has_img',
            'ex_csub_org_id',
            'register_code',
            'anket',
            'new_employee_registration_form',
        )

    def get_cfirst_name(self, obj):
        return obj.cfirst_name

    def get_clast_name(self, obj):
        return obj.clast_name

    def get_cregister(self, obj):
        return obj.cregister

    def get_cemdd_number(self, obj):
        return obj.cemdd_number

    def get_cndd_number(self, obj):
        return obj.cndd_number

    def get_caddress(self, obj):
        return obj.caddress

    def get_curgiin_ovog(self, obj):
        return obj.curgiin_ovog

    def get_unit1_name(self, obj):
        return obj.unit1_name

    def get_unit2_name(self, obj):
        return obj.unit2_name

    def get_gender_name(self, obj):
        return obj.gender_name

    def get_cemail(self, obj):
        return obj.cemail

    def get_cphone_number(self, obj):
        return obj.cphone_number

    def get_profile_img(self, obj):
        return obj.real_photo.url if obj.real_photo else ""

    def get_has_img(self, obj):
        return get_file_field_exists(obj.real_photo)

    def get_ex_csub_org_id(self, obj):
        return obj.sub_org.name if obj.sub_org else ''

    def get_anket(self, obj):

        anket_emp_qs = AnketEmployee.objects.filter(employee=obj)

        file_name = ''
        file_url = ''
        have_file = False

        if anket_emp_qs.exists():

            have_file = True
            file_name = os.path.basename(anket_emp_qs.last().file.name)
            file_url = anket_emp_qs.last().file.url

        data = {
            'file_name': file_name,
            'file_url': file_url,
            'have_file': have_file,
        }

        return data

    def get_new_employee_registration_form(self, obj):

        anket_emp_qs = NewEmployeeRegistrationForm.objects.filter(employee=obj)

        file_name = ''
        file_url = ''
        have_file = False

        if anket_emp_qs.exists():

            have_file = True
            file_name = os.path.basename(anket_emp_qs.last().file.name)
            file_url = anket_emp_qs.last().file.url

        data = {
            'file_name': file_name,
            'file_url': file_url,
            'have_file': have_file,
        }

        return data


class SalbarChoiceTreeSerializer(serializers.ModelSerializer):
    """ Салбарыг сонгоход мод хэлбэр хэрэгтэй түүний дата бэлдэх нь """

    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")
    children = serializers.SerializerMethodField()

    class Meta:
        model = Salbars
        exclude = "name", "id"

    def get_children(self, obj):
        childs = Salbars.objects.filter(parent=obj)
        children = SalbarChoiceTreeSerializer(childs, many=True).data

        return children


class SubOrgsSalbarTreeSerializer(serializers.ModelSerializer):

    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")
    children = serializers.SerializerMethodField()

    class Meta:
        model = SubOrgs
        exclude = "name", "id",

    def get_children(self, obj):
        filters = {}
        branch_pos = 0

        request = self.context.get("request")
        if request.org_filter.get('salbar'):
            filters['id'] = request.org_filter.get('salbar').id
            branch_pos = request.salbar_pos

        childs = obj.salbars_set.filter(**filters, branch_pos=branch_pos)
        children = SalbarChoiceTreeSerializer(childs, many=True).data

        return children


class SalbarSerializer(serializers.ModelSerializer):
    """ Салбарыг мод хэлбэртэйгээр авах нь """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Salbars
        fields = "id", 'name', 'children'

    def get_children(self, obj):
        childs = Salbars.objects.filter(parent=obj)
        children = SalbarSerializer(childs, many=True).data
        return children


class SubOrgWithSalbarSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model = SubOrgs
        fields = "id", 'name', 'children'

    def get_children(self, obj):
        qs = obj.salbars_set.filter(branch_pos=0)
        children = SalbarSerializer(instance=qs, many=True).data
        return children


class OrgWithSub_OrgSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    logo = serializers.ImageField(default="")

    class Meta:
        model = Orgs
        fields = "__all__"

    def get_children(self, obj):
        qs = obj.salbars_set.filter(branch_pos=0)
        children = SalbarSerializer(instance=qs, many=True).data
        return children


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class ChigluulehSerializer(serializers.ModelSerializer):

    pdfs = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ChigluulehHutulbur
        fields = '__all__'
        read_only_fields = ['pdfs']

    def get_pdfs(self, obj):
        data = AttachmentsDisplaySerializer(obj.pdfs.all(), many=True, context=self.context).data
        return data


class ChigluulehImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherImages
        fields = '__all__'


class EmployeeMigrationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMigrations
        fields = '__all__'

    @staticmethod
    def get_action_type(employee_new, old_employee):
        """ Ажилтны шилжилт хөдөлгөөний мэдээллийг үүсгэх нь """

        action_type = EmployeeMigrations.ACTION_TYPE_ORG            # Тухайн ажилтны шилжилт хөдөлгөөний төрөл (org, sub_org_ salbar)
        employee_mood = EmployeeMigrations.EMPLOYEE_MOOD_JOINED     # Ажилтны төлөв (Ажилтд орсон гарсан болон шилжиж буй эсэг)
        date_joined = None                                          # Тухайн албан тушаал дээр хэдэн томилгдсон хугацаа
        date_left = None                                            # Тухайн албан тушаалаас буусан хугацаа

        # Хуучин болно шинэ ажилтны мэдээлэл байх юм бол шилжилт хөдөлгөөн гэж үзнэ
        if employee_new and old_employee:
            if employee_new.salbar !=  old_employee.salbar:
                action_type = EmployeeMigrations.ACTION_TYPE_SALBAR
            if employee_new.sub_org !=  old_employee.sub_org:
                action_type = EmployeeMigrations.ACTION_TYPE_SUB_ORG
            if employee_new.org !=  old_employee.org:
                action_type = EmployeeMigrations.ACTION_TYPE_ORG

            employee_mood = EmployeeMigrations.EMPLOYEE_MOOD_MIGRATION
            date_joined = datetime.datetime.now()
            # Хуучин албан тушаалын төгсөглөг цагийг оноох нь
            old_migrations = EmployeeMigrations.objects.filter(employee=old_employee.id).latest('date_joined')
            old_migrations.date_left = date_joined
            old_migrations.save()

        # Зөвхөн шинэ ажилтны мэдээлэл байвал тухайн ажилтныг шинээр ажилд орж байна гэж үзнэ
        elif employee_new :
            if employee_new.sub_org:
                action_type = EmployeeMigrations.ACTION_TYPE_SUB_ORG
            elif employee_new.salbar:
                action_type = EmployeeMigrations.ACTION_TYPE_SALBAR

            date_joined = employee_new.date_joined

        # Зөвхөн хуучин ажилтны мэдээлэл байвал тухайн ажилтанг ажлаасаа гарж байна гэж үзнэ
        else:
            if old_employee.sub_org:
                action_type = EmployeeMigrations.ACTION_TYPE_SUB_ORG
            if old_employee.salbar:
                action_type = EmployeeMigrations.ACTION_TYPE_SALBAR

            employee_mood = EmployeeMigrations.EMPLOYEE_MOOD_LEFT
            date_left = datetime.datetime.now()
            # Хуучин албан тушаалын төгсөглөг цагийг оноох нь
            old_migrations = EmployeeMigrations.objects.filter(employee=old_employee.id).latest('date_joined')
            old_migrations.date_left = date_left
            old_migrations.save()

            # Тухайн ажилтны мэдээлэл дээр төгсөглөг цагийг оноох нь
            old_employee.date_left = date_left
            old_employee.save()

        return action_type, employee_mood, date_joined, date_left

    @staticmethod
    def create_from_employee(new_employee, old_employee, command_id):
        """ employee утгаас employee_migrations үүсгэх"""
        employee_migration_body = dict()        # Ажилтны шилжилт хөдөлгөөнийг хадгалах хувьсагч
        employee_migration_body_old = dict()    # Ажилтны шилжилт хөдөлгөөнийг хадгалах хувьсагч

        if old_employee:
            employee_migration_body_old = {
                    'employee_id': old_employee.id,
                    'org_old_id': old_employee.org.id,
                    'sub_org_old_id': old_employee.sub_org.id if old_employee.sub_org else None,
                    'salbar_old_id': old_employee.salbar.id if old_employee.salbar else None,
                    'org_position_old_id': old_employee.org_position.id if old_employee.org_position else None,
                }

        if new_employee:
            employee_migration_body = {
                    'employee_id': new_employee.id,
                    'org_new_id': new_employee.org.id,
                    'sub_org_new_id': new_employee.sub_org.id if new_employee.sub_org else None,
                    'salbar_new_id': new_employee.salbar.id if new_employee.salbar else None,
                    'org_position_new_id': new_employee.org_position.id if new_employee.org_position else None,
                }

        employee_migration_body.update(employee_migration_body_old)

        action_type, employee_mood, date_joined, date_left = EmployeeMigrationsSerializer.get_action_type(new_employee, old_employee)

        employee_migration_body.update(
            {
                'action_type': action_type,
                'employee_mood': employee_mood,
                'date_joined': date_joined,
                'date_left': date_left,
                'command_id': command_id
            }
        )

        return EmployeeMigrations.objects.create(**employee_migration_body)


class ForTomiloltSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")

    class Meta:
        model = ForTomilolt
        fields = "__all__"


class ForTomiloltCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForTomilolt
        fields = "__all__"


class TomiloltSerializer(serializers.ModelSerializer):
    attachments = serializers.PrimaryKeyRelatedField(allow_empty=True, many=True, queryset=Attachments.objects.all())
    class Meta:
        model = Tomilolt
        fields = '__all__'


class TomiloltGETSerializer(serializers.ModelSerializer):
    attachments = AttachmentsDisplaySerializer(many=True)
    class Meta:
        model = Tomilolt
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = '__all__'


class TomiloltPaginateSerializer(serializers.ModelSerializer):
    for_tomilolt = serializers.CharField(source="for_tomilolt.name", default='')
    created_by = serializers.CharField(source="created_by.full_name", default='')
    deleted_by = serializers.CharField(source="deleted_by.full_name", default='')
    unit1 = serializers.CharField()
    unit2 = serializers.CharField()
    unit3 = serializers.CharField()

    class Meta:
        model = Tomilolt
        fields = '__all__'


class TomiloltSerializerD(serializers.ModelSerializer):
    class Meta:
        model = Tomilolt
        fields = 'deleted_at', 'deleted_by'


class CommandDisplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Command
        fields = '__all__'


class DonoationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDonation
        fields = '__all__'


class DonoationPaginateSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    ctype = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDonation
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.full_name

    def get_ctype(self, obj):
        return obj.ctype


class EmployeeFilterSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    real_photo = serializers.FileField(source="user.real_photo")

    class Meta:
        model = Employee
        fields = "id", 'first_name', 'last_name', 'real_photo'

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name


class SkillDefsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StaticSkillsDefinations
        fields = "__all__"


class SkillsSerializer(serializers.ModelSerializer):

    defs = SkillDefsSerializer(source="staticskillsdefinations_set", many=True)

    class Meta:
        model = StaticSkills
        fields = "__all__"


class StaticSkillsSerializer(serializers.ModelSerializer):

    skills = SkillsSerializer(source="staticskills_set", many=True)

    class Meta:
        model = StaticGroupSkills
        fields = "__all__"


class RoutringSlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingSlip
        fields = '__all__'


class RoutingSlipPaginationSerializer(serializers.ModelSerializer):

    employee__org_position__name = serializers.SerializerMethodField()
    employee__org__name = serializers.SerializerMethodField()
    state_display_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(source="employee.user.info.full_name", default='')
    created_by_name = serializers.CharField(source="created_by.user.info.full_name", default='')
    state = serializers.SerializerMethodField()

    class Meta:
        model = RoutingSlip
        fields = '__all__'

    def get_employee__org_position__name(self, obj):
        return obj.org_position

    def get_employee__org__name(self, obj):
        return obj.employee_org

    def get_state_display_name(self, obj):
        return obj.state_display

    def get_state(self, obj):
        return obj.state_display


class RoutingSlupCommanderSerializer(serializers.ModelSerializer):

    employee__org__name = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    org_position__name =serializers.SerializerMethodField()
    employee__id =serializers.SerializerMethodField()
    org_position = serializers.CharField(source="employee.org_position")
    full_name = serializers.CharField(source="employee.user.info.full_name")
    routing_slip_state = serializers.CharField(source="routing_slip.state")

    class Meta:
        model = RoutingSlipCommanders
        fields = (
            "employee__id",
            "state",
            "org_position",
            "employee__org__name",
            "org_position__name",
            "full_name",
            "description",
            "routing_slip_state",
        )

    def get_employee__org__name(self, obj):
        return obj.employee_org

    def get_state(self, obj):
        return obj.state_display

    def get_org_position__name(self, obj):
        return obj.org_position_name

    def get_employee__id(self, obj):
        return obj.employee.id if obj.employee else None


class RoutingSlupCommanderAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoutingSlipCommanders
        fields = '__all__'


class TomiloltAttachListSerializer(serializers.ModelSerializer):
    attachments = AttachmentsDisplaySerializer(many=True)
    class Meta:
        model = Tomilolt
        fields = ('attachments',)


class EmployeeMigrationsSerializerFk(serializers.ModelSerializer):
    org_new = serializers.CharField(source="org_new.name",  default="")
    sub_org_new = serializers.CharField(source="sub_org_new.name",  default="")
    salbar_new = serializers.CharField(source="salbar_new.name",  default="")
    employee_mood = serializers.CharField(source="get_employee_mood_display")
    date_joined = serializers.DateTimeField(read_only=True,  format="%Y/%m/%d", default="")
    date_left = serializers.DateTimeField(read_only=True,  format="%Y/%m/%d", default="")
    org_position_new = serializers.CharField(source="org_position_new.name", default="")
    org_position_old = serializers.CharField(source="org_position_old.name", default="")

    class Meta:
        model = EmployeeMigrations
        fields = (
            "id",
            "org_new",
            "sub_org_new",
            "salbar_new",
            "employee_mood",
            "date_joined",
            "date_left",
            "org_position_new",
            "org_position_old",
        )


class EmployeeWithMigrationsSerializer(serializers.ModelSerializer):
    migration = EmployeeMigrationsSerializerFk(source='employeemigrations_set', many=True)
    org = serializers.CharField(source="org.name", default="")
    joined_date = serializers.DateTimeField(source="date_joined", read_only=True, format="%Y-%m-%d", default="")
    date_joined = serializers.DateTimeField(read_only=True,  format="%Y", default="")

    class Meta:
        model = Employee
        fields = (
            "id",
            "migration",
            "org",
            "joined_date",
            "date_joined",
        )


class EmployeeShortDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = 'id', 'org_position', 'full_name'


class RoutingSlipCommandersDataSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source="employee.user.info.full_name")
    employee_id = serializers.CharField(source="employee.id")
    class Meta:
        model = RoutingSlipCommanders
        fields = (
            "id",
            "org_position",
            "employee",
            "full_name",
            "employee_id"
        )


class UserExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserExperience
        fields = '__all__'


class EmployeeMigrationsUsedSerializer(serializers.ModelSerializer):
    employee_mood_display = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    updated_at_info = serializers.DateTimeField(source="updated_at", read_only=True, format="%Y-%m-%d", default="")

    class Meta:
        model = EmployeeMigrations
        fields = (
            "id",
            "employee_mood_display",
            "first_name",
            "last_name",
            "updated_at_info"
        )

    def get_employee_mood_display(self, obj):
        return obj.employee_mood_display

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_updated_at_info(self, obj):
        return obj.updated_at_info


class KhodolmoriinGereeSerializer(serializers.ModelSerializer):

    class Meta:
        model = KhodolmoriinGeree
        fields = "__all__"


class EmployeeDefinitionSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='user.info.first_name', default='')
    last_name = serializers.CharField(source='user.info.last_name', default='')
    register = serializers.CharField(source='user.info.register', default='')
    sub_org = serializers.CharField(source='sub_org.name', default='')
    org_position = serializers.CharField(source='org_position.name', default='')

    class Meta:
        model = Employee
        fields = '__all__'
