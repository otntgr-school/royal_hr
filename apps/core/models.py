import os

from datetime import datetime as dt

from django.db.models.functions import Concat
from django.db import models
from django.db.models import Value, Func
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

from .managers import Unit2Manager
from .managers import Unit3Manager
from .managers import UserManager
from .managers import SalbarManager
from .managers import NotifManager
from .managers import EmployeeManager

from .signals import delete_progress_signal

from main.utils.consts import (
    init_feedback_kinds,
    init_work_calendar_kinds,
    init_forTomilolt,
    init_shagnal,
)

from main.utils.user_percent import CalcUserPercent


class PropertyType(models.Model):
    """ Өмчийн хэлбэр
    """

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Өмчийн төрөлийн нэр")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EducationalInstitutionCategory(models.Model):
    """ Сургалтын байгууллагын ангилал
    """

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Сургалтын байгууллагын ангилалын нэр")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Create your models here.
class Orgs(models.Model):
    """
        Хамгийн том Байгууллага
    """

    name = models.CharField(max_length=250, null=False)
    name_eng = models.CharField(max_length=250, null=True)

    register = models.CharField(max_length=250, verbose_name='Байгууллагын регистр:', null=True, blank=True)
    address = models.CharField(max_length=250, verbose_name='Байгууллагын хаяг:', null=True, blank=True)
    web = models.CharField(max_length=250, verbose_name='Байгууллагын веб:', null=True, blank=True)
    social = models.CharField(max_length=250, verbose_name='Байгууллагын сошиал холбоос:', null=True, blank=True)
    logo = models.ImageField(upload_to="orgs/logo", null=True, blank=True, verbose_name='лого')

    email = models.EmailField(max_length=254, unique=True, blank=False, null=True, verbose_name="И-мэйл", error_messages={ "unique": "И-мэйл давхцсан байна" })
    phone_number = models.IntegerField(null=True, blank=True, verbose_name="Утасны дугаар")
    home_phone = models.IntegerField(null=True, blank=True, verbose_name="Факс")

    sign_zahiral = models.CharField(max_length=255, blank=True, null=True, verbose_name="Гарын үсэг зурах захиралын нэр")

    todorkhoilolt_approved = models.CharField(max_length=250, null=True)
    todorkhoilolt_rank = models.CharField(max_length=250, null=True)
    todorkhoilolt_signature = models.ImageField(upload_to="orgs/logo", null=True, blank=True, verbose_name='лого')
    todorkhoilolt_tamga = models.ImageField(upload_to="orgs/logo", null=True, blank=True, verbose_name='лого')

    email_host_user = models.EmailField(max_length=255, unique=False, blank=False, null=True, verbose_name="Системийн и-мэйл")
    email_use_tls = models.BooleanField(default=False, verbose_name="USE TLS")
    email_host_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="HOST NAME")
    email_host = models.CharField(max_length=255, null=True, blank=True, verbose_name="EMAIL HOST")
    email_port = models.IntegerField(null=True, blank=True, verbose_name="EMAIL PORT")
    email_password = models.CharField(max_length=255, null=True, blank=True, verbose_name="EMAIL PASSWORD")

    property_type = models.ForeignKey(PropertyType, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Өмчийн хэлбэр")
    educational_institution_category = models.ForeignKey(EducationalInstitutionCategory, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Сургалтын байгууллагын ангилал")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        is_create = not self.pk

        super(Orgs, self).save(*args, **kwargs)

        if is_create:
            #  Шинээр үүсэж байгаа үед

            _FeedbackKind = apps.get_model("core", 'FeedbackKind')
            for kind in init_feedback_kinds:
                _FeedbackKind.objects.create(**kind, org_id=self.pk)

            _ForTomilolt = apps.get_model("core", 'ForTomilolt')
            for tomiloltType in init_forTomilolt:
                _ForTomilolt.objects.create(**tomiloltType, org_id=self.pk)

            _WorkCalendarKindd = apps.get_model("core", 'WorkCalendarKind')
            for kind in init_work_calendar_kinds:
                _WorkCalendarKindd.objects.create(**kind, org_id=self.pk)

            _Shagnal = apps.get_model("core", 'Shagnal')
            for kind in init_shagnal:
                _Shagnal.objects.create(**kind, org_id=self.pk)


class Permissions(models.Model):
    """ Эрхүүд нь """

    name = models.CharField(max_length=250, null=False)
    description = models.CharField(max_length=1000, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.name}"


class Roles(models.Model):
    """ Системийн нийт role ууд """

    name = models.CharField(max_length=250, null=False)
    description = models.CharField(max_length=1000, null=True)
    permissions = models.ManyToManyField(Permissions)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MainPosition(models.Model):
    """ Үндсэн төрөлүүд
    """

    name = models.CharField(max_length=250, null=False, verbose_name="Нэр")
    code = models.CharField(max_length=255, null=True, blank=True, verbose_name="Код")


class OrgPosition(models.Model):
    """ Тухайн байгууллагын албан тушаал
    """

    org = models.ForeignKey(Orgs, on_delete=models.CASCADE)
    description = models.CharField(max_length=5000, null=True, blank=True, verbose_name="Тайлбар")
    name = models.CharField(max_length=250, null=False)
    permissions = models.ManyToManyField(Permissions)
    roles = models.ManyToManyField(Roles)
    is_hr = models.BooleanField(default=False, verbose_name="Хүний нөөцийн ажилтан эсэх")
    is_director =  models.BooleanField(default=False, verbose_name="Удирдах албан тушаалтан эсэх")
    is_teacher =  models.BooleanField(default=False, verbose_name="Багш эсэх")
    removed_perms = models.ManyToManyField(Permissions, related_name="remove", blank=True)
    main_position = models.ForeignKey(MainPosition, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Үндсэн албан тушаалын төрөлүүд")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Unit1(models.Model):
    name = models.CharField(unique=True, max_length=50)
    code = models.CharField(default=None, null=True, max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit2(models.Model):
    unit1 = models.ForeignKey(Unit1, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    code = models.CharField(default=None, null=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = Unit2Manager()

    @property
    def full_name(self):
        full = self.unit1.name + "," + self.name
        return full

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit3(models.Model):
    unit2 = models.ForeignKey(Unit2, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    code = models.CharField(default=None, null=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = Unit3Manager()

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.name


class SubOrgs(models.Model):
    """ Байгууллагын охин байгууллага эсвэл дэд байгууллага
    """

    org = models.ForeignKey(Orgs, on_delete=models.CASCADE, verbose_name='Байгууллага сонгох')

    name = models.CharField(max_length=250, verbose_name='Байгууллага нэр:', null=False)
    name_eng = models.CharField(max_length=500, null=True, blank=True, verbose_name="Байгууллага нэр англи")
    name_uig = models.CharField(max_length=500, null=True, blank=True, verbose_name="Байгууллага нэр уйгаржин")

    zahiral_name = models.CharField(max_length=250, verbose_name='Захирал нэр', null=True, blank=True)
    zahiral_name_eng = models.CharField(max_length=500, null=True, blank=True, verbose_name="Захирал нэр англи")
    zahiral_name_uig = models.CharField(max_length=500, null=True, blank=True, verbose_name="Захирал нэр уйгаржин")

    tsol_name = models.CharField(max_length=250, verbose_name='Цол нэр', null=True, blank=True)
    tsol_name_eng = models.CharField(max_length=500, null=True, blank=True, verbose_name="Цол нэр англи")
    tsol_name_uig = models.CharField(max_length=500, null=True, blank=True, verbose_name="Цол нэр уйгаржин")

    address = models.CharField(max_length=250, verbose_name='Байгууллагын хаяг:', null=True, blank=True)
    web = models.CharField(max_length=250, verbose_name='Байгууллагын веб:', null=True, blank=True)
    social = models.CharField(max_length=250, verbose_name='Байгууллагын сошиал холбоос:', null=True, blank=True)
    logo = models.ImageField(upload_to="suborgs/logo", null=True, blank=True, verbose_name='лого')
    is_school = models.BooleanField(default=False, null=True, verbose_name="Сургууль эсэх")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        is_create = not self.pk

        super(SubOrgs, self).save(*args, **kwargs)

        if is_create:
            #  Шинээр үүсэж байгаа үед

            _FeedbackKind = apps.get_model("core", 'FeedbackKind')
            for kind in init_feedback_kinds:
                _FeedbackKind.objects.create(**kind, org=self.org, sub_org_id=self.pk)

            _ForTomilolt = apps.get_model("core", 'ForTomilolt')
            for tomiloltType in init_forTomilolt:
                _ForTomilolt.objects.create(**tomiloltType, sub_org_id=self.pk)

            _WorkCalendarKindd = apps.get_model("core", 'WorkCalendarKind')
            for kind in init_work_calendar_kinds:
                _WorkCalendarKindd.objects.create(**kind, org=self.org, sub_org_id=self.pk)


class User(AbstractUser):

    LOGIN_TYPE_MAIN = 1
    LOGIN_TYPE_SIMPLE = 2
    LOGIN_TYPE_STUDENT = 3

    LOGIN_TYPE = (
        (LOGIN_TYPE_MAIN, 'Үндсэн'),
        (LOGIN_TYPE_SIMPLE, 'Энгийн хүн'),
        (LOGIN_TYPE_STUDENT, 'Оюутан'),
    )

    real_photo = models.ImageField(upload_to="user/profile",max_length=255, null=True, blank=True, verbose_name='Хэрэглэгчийн profile зураг')
    phone_number = models.IntegerField(null=True, blank=True, verbose_name="Утасны дугаар", unique=True, error_messages={'unique': 'Бүртгэлтэй дугаар байна.'})
    email = models.EmailField(max_length=254, unique=True, blank=False, null=True, verbose_name="И-мэйл", error_messages={ "unique": "И-мэйл давхцсан байна" })
    password = models.CharField(max_length=256, null=True)
    username = models.CharField(max_length=30, unique=True, null=True)
    home_phone = models.IntegerField(null=True, blank=True, verbose_name="Гэрийн утасны дугаар")
    mail_verified = models.BooleanField(null=True, blank=True, default=False, verbose_name="Гэрийн утасны дугаар")
    login_type = models.PositiveIntegerField(choices=LOGIN_TYPE, db_index=True, null=False, default=LOGIN_TYPE_MAIN, verbose_name="Хэрэглэгчийн төлөв")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def info(self):
        """ userinfo дундаас яг зөвшөөрөгдсөн userinfo хайж олно """
        return self.userinfo_set.filter(action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL).first()

    @property
    def full_name(self):
        return self.info.full_name()

    @property
    def employee(self):
        return self.employee_set.filter(state=Employee.STATE_WORKING).first()

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(User, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.id,
            model_name="User"
        ).calc()



class Salbars(models.Model):
    """
        Тухайн дэд байгууллагын салбар
    """

    leader = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Хөтөлбөрийн багийн ахлагч")

    org = models.ForeignKey(Orgs, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_orgs = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, verbose_name="Дэд байгууллага")
    name = models.CharField(max_length=250, null=False, verbose_name="Нэр", help_text="Энэ бол тайлбар")

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    branch_pos = models.IntegerField(default=0)

    address = models.CharField(max_length=250, verbose_name='Байгууллагын хаяг:', null=True, blank=True)
    web = models.CharField(max_length=250, verbose_name='Байгууллагын веб:', null=True, blank=True)
    social = models.CharField(max_length=250, verbose_name='Байгууллагын сошиал холбоос:', null=True, blank=True)
    logo = models.ImageField(upload_to="salbars/logo", null=True, blank=True, verbose_name='лого')
    is_hotolboriin_bag = models.BooleanField(default=False, null=True, verbose_name="Хөтөлбөрийн баг эсэх")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SalbarManager()

    @staticmethod
    def get_tree(request):
        from worker.serializer import SubOrgWithSalbarSerializer
        from worker.serializer import SalbarSerializer
        from suborg.serializer import SubOrgsSerializer

        sub_org_filters = SubOrgsSerializer.get_filters(request)
        salbar_filter = SalbarManager.get_filters(request)

        #  хэрвээ дэд байгууллагын ажилтан байвал
        # тухайн дэд байгууллагын салбарын жагсаалтыг өгнө
        if "id" in sub_org_filters and "id" not in salbar_filter:
            instance = SubOrgs.objects.filter(id=sub_org_filters.get("id"))
            return SubOrgWithSalbarSerializer(instance=instance, many=True).data, 'suborg'

        #  хэрвээ салбарын ажилтан байвал доод салбарын жагсаалтыг буцаана
        elif "id" in salbar_filter:
            instance = Salbars.objects.filter(id=salbar_filter['id'])
            return SalbarSerializer(instance=instance, many=True).data, 'salbar'

        #  хэрвээ хамгийн том байгууллагын хүн байвал
        #  дэд байгууллагыг салбаруудын хамт буцаана
        elif "org" in request.org_filter:
            instance = SubOrgs.objects.filter(org=request.org_filter.get("org"))
            return SubOrgWithSalbarSerializer(instance=instance, many=True).data, 'org'

        return [], None

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        is_create = not self.pk

        if self.parent:
            self.branch_pos = self.parent.branch_pos + 1
        else:
            self.branch_pos = 0
        super(Salbars, self).save(*args, **kwargs)

        if is_create:

            #  Шинээр үүсэж байгаа үед

            _FeedbackKind = apps.get_model("core", 'FeedbackKind')
            for kind in init_feedback_kinds:
                _FeedbackKind.objects.create(**kind, org=self.org, sub_org=self.sub_orgs, salbar_id=self.pk)

            _ForTomilolt = apps.get_model("core", 'ForTomilolt')
            for tomiloltType in init_forTomilolt:
                _ForTomilolt.objects.create(**tomiloltType, salbar_id=self.pk)

            _WorkCalendarKindd = apps.get_model("core", 'WorkCalendarKind')
            for kind in init_work_calendar_kinds:
                _WorkCalendarKindd.objects.create(**kind, org=self.org, sub_org=self.sub_orgs, salbar_id=self.pk)


class CountNumber(models.Model):
    ''' Ямар нэгэн юм тоолох
    '''

    name = models.CharField(max_length=500, verbose_name="Тушаалын дугаар")
    count = models.IntegerField(unique=True, verbose_name='Хэрэглэгчийн цагаа бүртгүүлэх ID')


# class EmployeeZeregTsol(models.Model):
#     ''' Ажилчны зэрэг
#     '''

#     name = models.CharField(max_length=500, null=True, blank=True, verbose_name="Зэрэгийн нэр")
#     level = models.IntegerField(blank=True, null=True, unique=True, verbose_name='Түвшин')

#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Шинэчилсэн огноо")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")


class Employee(models.Model):
    """ Хэрэглэгчийн тухайн байгуулг дахь бүртгэл """

    STATE_WORKING = 1
    STATE_FIRED = 2
    STATE_LEFT = 3

    STATE = (
        (STATE_WORKING, 'Ажиллаж байгаа'),
        (STATE_FIRED, 'Халагдсан'),
        (STATE_LEFT, 'Гарсан'),
    )

    WORKER_TYPE_CONTRACT = 1
    WORKER_TYPE_EMPLOYEE = 2
    WORKER_TYPE_PARTTIME = 3

    WORKER_TYPE = (
        (WORKER_TYPE_CONTRACT, 'Гэрээт ажилтан.'),
        (WORKER_TYPE_EMPLOYEE, 'Үндсэн ажилтан.'),
        (WORKER_TYPE_PARTTIME, 'Түр ажилтан.'),
    )

    TEACHER_RANK_TYPE_TRAINEE = 1
    TEACHER_RANK_TYPE_TEACHER = 2
    TEACHER_RANK_TYPE_SENIOR = 3
    TEACHER_RANK_TYPE_ASSOCIATE_PRO = 4
    TEACHER_RANK_TYPE_PRO = 5

    TEACHER_RANK_TYPE = (
        (TEACHER_RANK_TYPE_TRAINEE, 'Дадлагажигч багш'),
        (TEACHER_RANK_TYPE_TEACHER, 'Багш'),
        (TEACHER_RANK_TYPE_SENIOR, 'Ахлах багш'),
        (TEACHER_RANK_TYPE_ASSOCIATE_PRO, 'Дэд профессор'),
        (TEACHER_RANK_TYPE_PRO, 'Профессор'),
    )

    EDUCATION_LEVEL_TRAINEE = 1
    EDUCATION_LEVEL_TEACHER = 2
    EDUCATION_LEVEL_SENIOR = 3
    EDUCATION_LEVEL_ASSOCIATE_PRO = 4

    EDUCATION_LEVEL = (
        (EDUCATION_LEVEL_TRAINEE, 'Дипломын'),
        (EDUCATION_LEVEL_TEACHER, 'Бакалавр'),
        (EDUCATION_LEVEL_SENIOR, 'Магистр'),
        (EDUCATION_LEVEL_ASSOCIATE_PRO, 'Доктор'),
    )

    DEGREE_TYPE_ASSOCIATE_PRO = 1
    DEGREE_TYPE_PRO = 2
    DEGREE_TYPE_ACADEMICIAN = 3

    DEGREE_TYPE = (
        (DEGREE_TYPE_ASSOCIATE_PRO, 'Дэд профессор'),
        (DEGREE_TYPE_PRO, 'Профессор'),
        (DEGREE_TYPE_ACADEMICIAN, 'Академич'),
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Хэрэглэгч")
    org_position = models.ForeignKey(OrgPosition, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Албан тушаал")
    state = models.PositiveIntegerField(choices=STATE, db_index=True, null=False, default=STATE_WORKING, verbose_name="Ажилтны төлөв(Ажиллаж байгаа, Халагдсан эсэг)")
    worker_type = models.PositiveIntegerField(choices=WORKER_TYPE, db_index=True, null=False, default=WORKER_TYPE_EMPLOYEE, verbose_name="Ажилтны төлөв(Ажиллаж байгаа, Халагдсан эсэг)")

    time_user = models.CharField(null=True, max_length=500, blank=True, verbose_name="Цаг өгөх төхөөрөмжөөс таних ID")
    time_register_employee = models.CharField(max_length=500, blank=True, null=True, unique=True, verbose_name='Хэрэглэгчийн цагаа бүртгүүлэх ID')
    register_code = models.CharField(null=True, max_length=500, blank=True, unique=True, verbose_name="Ажилтны код")

    basic_salary_information = models.IntegerField(blank=True, null=True, default=0, verbose_name='Үндсэн цалингийн мэдээлэл')
    work_for_hire = models.BooleanField(null=True, blank=True, default=False, verbose_name="Хөлсөөр ажиллах эсэх")
    hourly_wage_information = models.IntegerField(blank=True, null=True, default=0, verbose_name='Нэг цагийн цалингийн мэдээлэл')
    hire_wage_information = models.IntegerField(blank=True, null=True, default=0, verbose_name='Хөлсөөр ажиллах цалингийн мэдээлэл')

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Ажилд орсон хугацаа")
    date_left = models.DateTimeField(blank=True, null=True, verbose_name="Ажлаас гарсан хугацаа")

    teacher_rank_type = models.PositiveIntegerField(choices=TEACHER_RANK_TYPE, db_index=True, null=True, blank=True, default=None, verbose_name="Албан тушаал")
    education_level = models.PositiveIntegerField(choices=EDUCATION_LEVEL, db_index=True, null=True, blank=True, default=None, verbose_name="Боловсролын түвшин")
    degree_type = models.PositiveIntegerField(choices=DEGREE_TYPE, db_index=True, null=True, blank=True, default=None, verbose_name="Эрдмийн зэрэг")
    updated_at = models.DateTimeField(auto_now=True)

    # zereg = models.ForeignKey(EmployeeZeregTsol, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Эрдмийн зэрэг цол")

    objects = EmployeeManager()

    @property
    def is_hr(self):
        return self.user.is_superuser or (self.org_position.is_hr if self.org_position else False)

    @property
    def real_photo(self):
        return self.user.real_photo

    @property
    def full_name(self):
        return self.user.full_name

    @staticmethod
    def exactly_our_employees(request):
        return Employee.objects.filter(**request.exactly_org_filter, state=Employee.STATE_WORKING)

    @staticmethod
    def get_filter(request):
        filters = {
            "org": request.org_filter.get("org")
        }

        if "sub_org" in request.org_filter:
            filters['sub_org'] = request.org_filter.get("sub_org").id

        if "salbar" in request.org_filter:
            filters['salbar'] = request.org_filter.get("salbar").id

        return filters


class Attachments(models.Model):
    file = models.FileField(upload_to="attachements/%Y/%m/%d")
    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def save_attach_get_ids(request, reqfiles, files=[]):
        from command.serializer import AttachmentSerializer
        attachment_ids = list()

        for _file in reqfiles:
            attachemnt = AttachmentSerializer(data={ "file": _file, "org": request.exactly_org_filter.get("org").id }, many=False)
            attachemnt.is_valid()
            attachemnt.save()
            files.append(attachemnt.data)
            attachment_ids.append(str(attachemnt.data.get("id")))

        return attachment_ids, files

    @staticmethod
    def remove_files(files):
        from main.utils.file import remove_file
        for _file in files:
            zam = str(settings.BASE_DIR) + _file.get('file')
            remove_file(zam)

    @staticmethod
    def remove_obj(remove_att_qs):
        from main.utils.file import remove_file
        for obj in remove_att_qs:
            remove_file(obj.file.path)
            obj.delete()


class Command(models.Model):
    """ Тушаал """
    UNIT_ALL = 'all'
    UNIT_SELF = 'self_org'
    UNIT_EMPLOYEE = 'selected_employees'

    UNIT_CHOICES = (
        (UNIT_ALL, "Нийт байгууллага"),
        (UNIT_SELF, "Зөвхөн өөрийн байгууллага"),
        (UNIT_EMPLOYEE, "Оноогдсон ажилтанд"),
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    unit = models.CharField(choices=UNIT_CHOICES, max_length=100, default=UNIT_SELF, verbose_name="Тушаалын хамрах хүрээ")
    command_number = models.CharField(null=False, unique=True, max_length=500, verbose_name="Тушаалын дугаар", error_messages={ "unique": "Тушаалын дугаар давхцсан байна" })
    name = models.CharField(max_length=250, null=False, blank=False, verbose_name="Гарчиг")
    description = models.CharField(max_length=5000, null=True, blank=True, verbose_name="Тайлбар")
    attachments = models.ManyToManyField(Attachments, blank=True, verbose_name="Хавсралт")

    employees = models.ManyToManyField(Employee, blank=True, verbose_name="Ажилчид")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="command_created_by")
    commander = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="command_commander")

    date = models.DateField(null=False, verbose_name="Тушаалын огноо")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmployeeMigrations(models.Model):
    """ Тухайн ажилтны ажил албан тушаалын түүх"""

    ACTION_TYPE_ORG = 1
    ACTION_TYPE_SUB_ORG = 2
    ACTION_TYPE_SALBAR = 3

    ACTION_TYPE = (
        (ACTION_TYPE_ORG, 'Байгуулга хооронд'),
        (ACTION_TYPE_SUB_ORG, 'Харьяалагдах алба нэгж хооронд'),
        (ACTION_TYPE_SALBAR, 'Салбар хооронд'),
    )

    ACTION_CAUSE_ERROR = 1
    ACTION_CAUSE_COMMAND = 2
    ACTION_CAUSE_SELF = 3

    ACTION_CAUSE = (
        (ACTION_CAUSE_ERROR, 'Системийн алдаатай бүртгэсэн'),
        (ACTION_CAUSE_COMMAND, 'Тушаалаар'),
        (ACTION_CAUSE_SELF, 'Өөрийн хүсэлтээр'),
    )

    EMPLOYEE_MOOD_JOINED = 1
    EMPLOYEE_MOOD_LEFT = 2
    EMPLOYEE_MOOD_MIGRATION = 3

    EMPLOYEE_MOOD = (
        (EMPLOYEE_MOOD_JOINED, 'Ажилд орсон'),
        (EMPLOYEE_MOOD_LEFT, 'Ажлаас гарсан'),
        (EMPLOYEE_MOOD_MIGRATION, 'Шилжилт хөдөлгөөн хийсэн'),
    )

    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, db_index=True , verbose_name="Ажилтан")

    org_old = models.ForeignKey(Orgs, related_name='org_old', blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org_old = models.ForeignKey(SubOrgs, related_name='sub_org_old',on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar_old = models.ForeignKey(Salbars, related_name='salbar_old',on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    org_position_old = models.ForeignKey(OrgPosition, related_name='org_position_old',blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Албан тушаал")

    org_new = models.ForeignKey(Orgs, related_name='org_new', blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org_new = models.ForeignKey(SubOrgs, related_name='sub_org_new',on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar_new = models.ForeignKey(Salbars, related_name='salbar_new',on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    org_position_new = models.ForeignKey(OrgPosition, related_name='org_position_new',blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Албан тушаал")
    command = models.ForeignKey(Command, on_delete=models.CASCADE, db_index=True, verbose_name="Тушаал", null=True)

    action_type = models.PositiveIntegerField(choices=ACTION_TYPE, db_index=True, null=False, default=ACTION_TYPE_SALBAR, verbose_name="Үйлдлийн төрөл")
    action_cause = models.PositiveIntegerField(choices=ACTION_CAUSE, db_index=True, null=False, default=ACTION_CAUSE_SELF, verbose_name="Үйлдлийн шалтгаан")
    employee_mood = models.PositiveIntegerField(choices=EMPLOYEE_MOOD, db_index=True, null=False, default=EMPLOYEE_MOOD_JOINED, verbose_name="Ажилтны төлөв")

    date_joined = models.DateTimeField(blank=True, null=True, verbose_name="Ажилд орсон хугацаа")
    date_left = models.DateTimeField(blank=True, null=True, verbose_name="Ажлаас гарсан хугацаа")

    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_filter(request):
        filters = {
            "org": request.org_filter.get("org")
        }

        if "sub_org" in request.org_filter:
            filters['sub_org'] = request.org_filter.get("sub_org").id

        if "salbar" in request.org_filter:
            filters['salbar'] = request.org_filter.get("salbar").id

        return filters


class UserContactInfoRequests(models.Model):
    """
        Холбоо барих мэдээлэл солих хүсэлт
    """

    PENDING = 1
    APPROVED = 2
    DECLINED = 3

    ACTION_STATUS = (
        (PENDING, 'Хүлээгдэж буй'),
        (APPROVED, 'Зөвшөөрсөн'),
        (DECLINED, 'Цуцалсан'),
    )
    # employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, verbose_name="Ажилтан")
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, verbose_name="Хэрэглэгч")
    phone_number = models.IntegerField(null=True, verbose_name="Утасны дугаар", default=0)
    email = models.EmailField(max_length=254, unique=True, blank=False, null=False, verbose_name="И-мэйл", error_messages={ "unique": "И-мейл давхцсан байна" })
    home_phone = models.IntegerField(null=True, blank=True, verbose_name="Гэрийн утасны дугаар")
    action_status =  models.PositiveIntegerField(choices=ACTION_STATUS, db_index=True, null=False, default=PENDING, verbose_name="Өөрчлөх, үүсгэх төлөв")

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")


class UserInfo(models.Model):

    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_OTHER = 3

    GENDER_TYPE = (
        (GENDER_MALE, 'эрэгтэй'),
        (GENDER_FEMALE, 'эмэгтэй'),
        (GENDER_OTHER, 'бусад'),
    )

    BLOOD_O = 1
    BLOOD_A = 2
    BLOOD_B = 3
    BLOOD_AB = 4

    BLOOD_TYPE = (
        (BLOOD_O, 'O/I/'),
        (BLOOD_A, 'A/II/'),
        (BLOOD_B, 'B/III/'),
        (BLOOD_AB, 'AB/IV/'),
    )

    PENDING = 1
    APPROVED = 2
    DECLINED = 3

    ACTION_STATUS = (
        (PENDING, 'Хүлээгдэж буй'),
        (APPROVED, 'Зөвшөөрсөн'),
        (DECLINED, 'Цуцалсан'),
    )

    ACTION_TYPE_GENERAL = 1
    ACTION_TYPE_EXTRA = 2
    ACTION_TYPE_ALL = 3

    ACTION_TYPE = (
        (ACTION_TYPE_GENERAL, 'ерөнхий мэдээлэл'),
        (ACTION_TYPE_EXTRA, 'нэмэлт мэдээлэл'),
        (ACTION_TYPE_ALL, 'бүх мэдээлэл'),
    )

    SUUTS_TYPE_GER = 1
    SUUTS_TYPE_BAISHIN = 2
    SUUTS_TYPE_ORON_SUUTS = 3

    SUUTS_TYPE = (
        (SUUTS_TYPE_GER, 'гэр'),
        (SUUTS_TYPE_BAISHIN, 'байшин'),
        (SUUTS_TYPE_ORON_SUUTS, 'орон сууц'),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="Хэрэглэгч")
    urgiin_ovog = models.CharField(default='', null=True , max_length=100, verbose_name="Ургийн овог", blank=True)
    last_name = models.CharField(default='', null=True , max_length=50, verbose_name="Эцэг эхийн нэр")
    first_name = models.CharField(default='', null=True , max_length=50, verbose_name="Хэрэглэгчийн нэр")
    register = models.CharField(null=True, blank=False , max_length=10, unique=False, verbose_name="Регистерийн дугаар")
    gender = models.PositiveIntegerField(choices=GENDER_TYPE, db_index=True, null=False, default=GENDER_OTHER, verbose_name="Хүйс")
    ys_undes = models.CharField(default='', null=True , max_length=150, verbose_name="Яс үндэс", blank=True)
    action_status =  models.PositiveIntegerField(choices=ACTION_STATUS, db_index=True, null=False, default=PENDING, verbose_name="Өөрчлөх, үүсгэх төлөв")
    action_status_type =  models.PositiveIntegerField(choices=ACTION_TYPE, db_index=True, null=False, default=ACTION_TYPE_ALL, verbose_name="Өөрчлөх, үүсгэх төлөв төрөл")
    blood_type =  models.PositiveIntegerField(choices=BLOOD_TYPE, db_index=True, null=True, blank=True, default=None, verbose_name="Цусны бүлэг")
    address = models.CharField(default='', null=True , max_length=500, verbose_name="Оршин суугаа хаяг", blank=True)

    unit1 = models.ForeignKey(Unit1, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Төрсөн газар /аймаг,хот/')
    unit2 = models.ForeignKey(Unit2, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Төрсөн газар /сум, дүүрэг/')
    emdd_number = models.CharField(default='', null=True, max_length=256, verbose_name="ЭМДД-ийн дугаар", blank=True)
    ndd_number = models.CharField(default='', null=True, max_length=256, verbose_name="НДД-ийн дугаар", blank=True)
    body_height = models.FloatField(default=0, verbose_name="Биеийн өндөр")
    body_weight = models.FloatField(default=0, verbose_name="Биеийн жин")

    # MYNC
    suutsnii_torol = models.PositiveIntegerField(choices=SUUTS_TYPE, db_index=True, null=True, blank=True, default=None, verbose_name="Сууцны төрөл")
    is_pension = models.BooleanField(default=False, null=True, verbose_name="Тэтгэвэрт гарсан эсэх")
    is_disabled = models.BooleanField(default=False, null=True, verbose_name="Хөгжлийн бэрхшээлтэй эсэх")
    experience_year = models.CharField(default='', null=True, max_length=50, verbose_name="Нийт ажилласан жил", blank=True)
    experience_mnun_year = models.CharField(default='', null=True, max_length=50, verbose_name="МҮИС-д ажилласан жил", blank=True)
    is_training_licence = models.BooleanField(default=False, null=True, verbose_name="Багшлах эрхийн сургалтанд суусан эсэх")

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    birthday = models.DateField(null=True, verbose_name="Төрсөн өдөр")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")

    def full_name(self):

        ovog = f"{self.last_name[0].upper()}." if self.last_name else ""
        name = self.first_name.capitalize()

        if ovog and name:
            return f"{ovog}{name}"

        if name:
            return name

        return self.user.email

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserInfo, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name="UserInfo"
        ).calc()
delete_progress_signal(UserInfo)


class UserEducation(models.Model):
    """
        Хэрэглэгчийн  Боловсролын талаархи мэдээлэл
    """
    EDUCATION_SOB = 1
    EDUCATION_BAGA = 2
    EDUCATION_BUREN = 3
    EDUCATION_MERGEJLIIN = 4
    EDUCATION_DEED = 5

    EDUCATION_GRADE = (
        (EDUCATION_SOB, 'СӨБ'),
        (EDUCATION_BAGA, 'Бага, суурь'),
        (EDUCATION_BUREN, 'Бүрэн дунд'),
        (EDUCATION_MERGEJLIIN, 'Мэргэжлийн боловсрол'),
        (EDUCATION_DEED, 'Дээд боловсрол'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Хэрэглэгч", null=True, blank=True)
    level = models.PositiveIntegerField(choices=EDUCATION_GRADE, db_index=True, default=EDUCATION_BUREN, verbose_name="Боловсролын зэрэг", null=True, blank=True)

    bachelor_sedew = models.CharField(max_length=255, null=True, blank=True)
    dr_sedew = models.CharField(max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserEducation, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserEducation'
        ).calc()
delete_progress_signal(UserEducation)


class UserEducationInfo(models.Model):
    """
        Боловсрол /ерөнхий, тусгай дунд, дээд боловсрол, дипломын, бакалаврын болон магистрийн зэргийг оролцуулан/
    """
    user_education = models.ForeignKey(UserEducation, on_delete=models.CASCADE, null=True, blank=True)
    school = models.CharField(max_length=256, verbose_name="Төгссөн сургууль", null=True, blank=True)
    mergejil = models.CharField(max_length=255, verbose_name="Мэргэжил", null=True, blank=True)
    ezemshsen_bolowsrol = models.CharField(max_length=255, verbose_name="Эзэмшсэн боловсрол", null=True, blank=True)
    start_date = models.DateField(verbose_name="Элссэн он сар", null=True, blank=True)
    end_date = models.DateField(verbose_name="Төгссөн он сар", null=True, blank=True)

    diplom_number = models.CharField(max_length=256, verbose_name="Дипломын гэрчилгээний дугаар", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо", null=True, blank=True)

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserEducationInfo, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_education.user_id,
            model_name='UserEducationInfo'
        ).calc()
delete_progress_signal(UserEducationInfo)


class UserEducationDoctor(models.Model):
    """
        Боловсролын докторын болон шинжлэх ухааны докторын зэрэг
    """
    user_education = models.ForeignKey(UserEducation, on_delete=models.CASCADE, null=True, blank=True)
    level = models.CharField(max_length=255, null=True, blank=True)
    school = models.CharField(null=True, blank=True, max_length=256, verbose_name="Төгссөн сургууль")
    end_date = models.DateField(verbose_name="Төгссөн он сар")

    diplom_number = models.CharField(null=True, blank=True, max_length=256, verbose_name="Дипломын гэрчилгээний дугаар")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserEducationDoctor, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_education.user_id,
            model_name='UserEducationDoctor'
        ).calc()
delete_progress_signal(UserEducationDoctor)


class UserProfessionInfo(models.Model):
    """
        Хэрэглэгчийн мэргэжил дээшлүүлсэн байдал 3.1. Мэргэшлийн бэлтгэл
    """

    WHERE_COUNTRY_DOTOOD = 1
    WHERE_COUNTRY_GADAAD = 2

    WHERE_COUNTRY_TYPE = (
        (WHERE_COUNTRY_DOTOOD, 'Дотоодод'),
        (WHERE_COUNTRY_GADAAD, 'Гадаадад'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    where = models.CharField(max_length=256, verbose_name='ХААНА, ЯМАР БАЙГУУЛЛАГАД', null=True, blank=True)

    start_date = models.DateField(verbose_name="Элссэн он сар", null=True, blank=True)
    end_date = models.DateField(verbose_name="Төгссөн он сар", null=True, blank=True)
    learned_days = models.IntegerField(verbose_name="Хугацаа хоногоор", default=0, null=True, blank=True)

    profession = models.CharField(max_length=256, verbose_name="эзэмссэн мэргэжил", null=True, blank=True)
    license_number = models.CharField(max_length=256, verbose_name="Үнэмлэх, гэрчилгээний дугаар", null=True, blank=True)

    where_country = models.PositiveBigIntegerField(choices=WHERE_COUNTRY_TYPE, db_index=True, default=WHERE_COUNTRY_DOTOOD, verbose_name="Мэргэжил дээшлүүлсэн байдал", null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserProfessionInfo, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserProfessionInfo'
        ).calc()
delete_progress_signal(UserProfessionInfo)


class UserWorkExperience(models.Model):
    """ 3.2. Албан тушаалын зэрэг дэв, цол """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    alban_tushaal = models.CharField(max_length=255, null=True, blank=True)
    zereg = models.CharField(max_length=255, null=True, blank=True)
    zarlig = models.CharField(max_length=500, null=True, blank=True)

    license_number = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserWorkExperience, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserWorkExperience'
        ).calc()
delete_progress_signal(UserWorkExperience)


class UserErdmiinTsol(models.Model):
    """ 3.3. Эрдмийн цол /дэд профессор, профессор, академийн гишүүнийг оролцуулан/ """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tsol = models.CharField(max_length=255, null=True, blank=True)
    tsol_olgoson_org = models.CharField(max_length=255, null=True, blank=True)
    give_date = models.DateField(null=True, blank=True)

    license_number = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserErdmiinTsol, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserErdmiinTsol'
        ).calc()
delete_progress_signal(UserErdmiinTsol)


class UserLanguage(models.Model):
    """
        4.2. Гадаад хэлний мэдлэг
    """
    GRADE_DUND = 1
    GRADE_SAIN = 2
    GRADE_ONTS = 3

    GRADE_TYPE = (
        (GRADE_DUND, 'Дунд'),
        (GRADE_SAIN, 'Сайн'),
        (GRADE_ONTS, 'Онц'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    langage = models.CharField(max_length=128, verbose_name="гадаад хэл", null=True, blank=True)

    talk = models.PositiveBigIntegerField(choices=GRADE_TYPE, db_index=True, default=GRADE_DUND, verbose_name="Ярих", null=True, blank=True)
    read = models.PositiveBigIntegerField(choices=GRADE_TYPE, db_index=True, default=GRADE_DUND, verbose_name="Унших", null=True, blank=True)
    listen = models.PositiveBigIntegerField(choices=GRADE_TYPE, db_index=True, default=GRADE_DUND, verbose_name="Сонсох", null=True, blank=True)
    write = models.PositiveBigIntegerField(choices=GRADE_TYPE, db_index=True, default=GRADE_DUND, verbose_name="Бичих", null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserLanguage, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserLanguage'
        ).calc()
delete_progress_signal(UserLanguage)


class UserOfficeKnowledge(models.Model):
    """
        4.3.2 ЭЗЭМШСЭН ОФФИСИЙН ТОНОГ ТӨХӨӨРӨМЖ, ТЕХНОЛОГИЙН НЭР
    """
    GRADE_DUND = 1
    GRADE_SAIN = 2
    GRADE_ONTS = 3

    GRADE_TYPE = (
        (GRADE_DUND, 'Дунд'),
        (GRADE_SAIN, 'Сайн'),
        (GRADE_ONTS, 'Онц'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    internet_usage = models.PositiveBigIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Интернэт ашиглалт")
    local_network = models.PositiveBigIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Дотоод сүлжээ ашиглах")

    scaner = models.PositiveSmallIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Скайнер")
    printer = models.PositiveSmallIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Принтр")
    copier = models.PositiveSmallIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Хувилагч")
    fax = models.PositiveSmallIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Факс")
    media = models.PositiveSmallIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Гэрэл зургийн болон видео бичлэгийн аппарат г.м")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserOfficeKnowledge, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserOfficeKnowledge'
        ).calc()
delete_progress_signal(UserOfficeKnowledge)


class UserProgrammKnowledge(models.Model):
    """
        4.3.1 ЭЗЭМШСЭН ПРОГРАММЫН НЭР
    """
    GRADE_DUND = 1
    GRADE_SAIN = 2
    GRADE_ONTS = 3

    GRADE_TYPE = (
        (GRADE_DUND, 'Дунд'),
        (GRADE_SAIN, 'Сайн'),
        (GRADE_ONTS, 'Онц'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, null=True, blank=True)
    level = models.PositiveSmallIntegerField(choices=GRADE_TYPE, db_index=True, null=True, blank=True, default=GRADE_DUND, verbose_name="Түвшин")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserProgrammKnowledge, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserProgrammKnowledge'
        ).calc()
delete_progress_signal(UserProgrammKnowledge)


class UserTalent(models.Model):
    """
        Хэрэглэгчийн урлаг, спортын авъяас
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, verbose_name="Хэрэглэгч")

    type = models.CharField(null=False, max_length=128, verbose_name="Урлаг/Спортын төрөл")
    studied_date = models.FloatField(default=0, verbose_name="Хичээллэсэн хугацаа")
    rank = models.CharField(null=False, max_length=128, verbose_name="Зэрэг/Шагналын нэр")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserTalent, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserTalent'
        ).calc()
delete_progress_signal(UserTalent)


class UserReward(models.Model):
    """
        шагнал
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, verbose_name="Хэрэглэгч")
    reward_name = models.CharField(null=False, max_length=128, verbose_name="Шагналын нэр ")
    got_date = models.DateField(verbose_name="Шагнагдсан он ")
    company_name = models.CharField(null=False, max_length=256, verbose_name="Хаана ажиллах хугацаанд шагнагдсан")
    explanation = models.CharField(blank=True, null=True, default='', max_length=500, verbose_name="Тайлбар")

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")


class UserFamilyMember(models.Model):
    """
        1.7. Гэр бүлийн байдал
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_who = models.CharField(default='', max_length=30, verbose_name="Таны хэн болох", null=True, blank=True)
    full_name = models.CharField(default='', max_length=30, verbose_name="Овог нэр", null=True, blank=True)

    birthday = models.DateField(verbose_name="Төрсөн өдөр", null=True, blank=True)
    birthplace = models.CharField(max_length=500, null=True, blank=True)

    phone_number = models.IntegerField(null=True, blank=True, unique=False, verbose_name="Утасны дугаар")
    register = models.CharField(null=True, blank=True , max_length=10, unique=False, verbose_name="Регистерийн дугаар")

    job = models.CharField(null=True, blank=True, max_length=256, verbose_name="Ямар ажил хийдэг")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserFamilyMember, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserFamilyMember'
        ).calc()

    def delete(self, *args, **kwargs):
        deleted = super(UserFamilyMember, self).delete(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserFamilyMember'
        ).calc()
        return deleted


class UserHamaatan(models.Model):
    """
        1.8. Садан төрлийн байдал
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_who = models.CharField(default='', max_length=30, verbose_name="Таны хэн болох", null=True, blank=True)
    full_name = models.CharField(default='', max_length=30, verbose_name="Овог нэр", null=True, blank=True)

    birthday = models.DateField(verbose_name="Төрсөн өдөр", null=True, blank=True)
    birthplace = models.CharField(max_length=500, null=True, blank=True)

    job = models.CharField(null=True, blank=True, max_length=256, verbose_name="Ямар ажил хийдэг")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserHamaatan, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserHamaatan'
        ).calc()

    def delete(self, *args, **kwargs):
        deleted = super(UserHamaatan, self).delete(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserHamaatan'
        ).calc()
        return deleted


class UserEmergencyCall(models.Model):
    """
        1.11. Онцгой шаардлага гарвал харилцах хүмүүс
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(default='', max_length=30, verbose_name="Овог нэр", null=True, blank=True)
    number = models.CharField(max_length=100, verbose_name="Дугаар", null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserEmergencyCall, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserEmergencyCall'
        ).calc()

    def delete(self, *args, **kwargs):
        deleted = super(UserEmergencyCall, self).delete(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserEmergencyCall'
        ).calc()
        return deleted


class StaticGroupSkills(models.Model):
    """ ур чадварын багц """

    name = models.CharField(max_length=255, null=False, blank=False)


class StaticSkills(models.Model):

    group = models.ForeignKey(StaticGroupSkills, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class StaticSkillsDefinations(models.Model):

    skill = models.ForeignKey(StaticSkills, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class SkillDefWithUser(models.Model):

    LEVEL_LOW = 1
    LEVEL_MED = 2
    LEVEL_HIGH = 3

    LEVEL_CHOICES = (
        (LEVEL_LOW, "1"),
        (LEVEL_MED, "2"),
        (LEVEL_HIGH, "3"),
    )

    skill_def = models.ForeignKey(StaticSkillsDefinations, on_delete=models.CASCADE)
    level = models.SmallIntegerField(choices=LEVEL_CHOICES, default=LEVEL_LOW)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(SkillDefWithUser, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='SkillDefWithUser'
        ).calc()

    def delete(self, *args, **kwargs):
        deleted = super(SkillDefWithUser, self).delete(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='SkillDefWithUser'
        ).calc()
        return deleted


class ExtraSkillsDefinations(models.Model):

    LEVEL_LOW = 1
    LEVEL_MED = 2
    LEVEL_HIGH = 3

    LEVEL_CHOICES = (
        (LEVEL_LOW, "1"),
        (LEVEL_MED, "2"),
        (LEVEL_HIGH, "3"),
    )

    name = models.CharField(max_length=255, null=True, blank=True)
    level = models.SmallIntegerField(choices=LEVEL_CHOICES, default=LEVEL_LOW, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(ExtraSkillsDefinations, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='ExtraSkillsDefinations'
        ).calc()

    def delete(self, *args, **kwargs):
        deleted = super(ExtraSkillsDefinations, self).delete(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='ExtraSkillsDefinations'
        ).calc()
        return deleted


class UserExperience(models.Model):
    """
        5.1. Хөдөлмөр эрхлэлтийн байдал
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    worked_place = models.CharField(max_length=500, null=True, blank=True)
    pos = models.CharField(max_length=255, null=True, blank=True)

    joined_date = models.DateField(verbose_name="Ажилд орсон", null=True, blank=True)
    left_date = models.DateField(verbose_name="Ажлаас гарсан", null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Системд өгөгдөл шинээр оруулсан огноо")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(UserExperience, self).save(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserExperience'
        ).calc()

    def delete(self, *args, **kwargs):
        deleted = super(UserExperience, self).delete(*args, **kwargs)
        CalcUserPercent(
            user_id=self.user_id,
            model_name='UserExperience'
        ).calc()
        return deleted


class OrgVacationTypes(models.Model):
    """ Байгууллагын чөлөөний төрөл
    """
    org = models.ForeignKey(Orgs, on_delete=models.CASCADE, verbose_name='Байгууллага')
    times = models.IntegerField(default=0, verbose_name='Сард хэдэн удаа авч болох эрхийн тоо')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Нэр')
    one_day_vacation = models.BooleanField(default=True, null=True, verbose_name="Нэг өдрийн чөлөө")
    many_days_vacation = models.BooleanField(default=True, null=True, verbose_name="Олон өдрийн чөлөө")


class OrgVacationTypesBranchTypes(models.Model):
    """ Гарын үсэг зурах албан тушаалтнууд
    """
    vacation = models.ForeignKey(OrgVacationTypes, on_delete=models.CASCADE, verbose_name='Байгууллагын чөлөөнөөс салаалах утга')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Хүсэлтийн хуудасан дээрх өмнө нь юу гэж бичигдэхийг заана')
    order = models.IntegerField(default=0, null=False, blank=False, verbose_name="Зэрэглэл")
    org_position = models.ForeignKey(OrgPosition, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Гарын үсэг зурах албан тушаал")


class RequestTimeVacationRegister(models.Model):
    """ Чөлөө авах хүсэлт
    """

    WAITING = 1
    DECLINE = 2
    AGREE = 3

    STATUS_CHOICES = (
        (WAITING, 'Хүлээгдэж буй'),
        (DECLINE, 'Татгалзсан'),
        (AGREE, 'Зөвшөөрсөн'),
    )

    vacation_type = models.ForeignKey(OrgVacationTypes, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Чөлөөний төрөл')
    # special_reason = models.ForeignKey(OrgVacationTypesBranchTypes, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Чөлөөний төрөлийн шалтгаан')

    description = models.TextField(verbose_name="Тайлбар", null=True, blank=True)
    start_day = models.DateField(null=True, verbose_name="Эхлэх өдөр")
    end_day = models.DateField(null=True, verbose_name="Дуусах өдөр")
    start_time = models.TimeField(null=True, verbose_name="Эхлэх цаг")
    end_time = models.TimeField(null=True, verbose_name="Дуусах цаг")
    during_the_day = models.BooleanField(default=False, null=True, verbose_name="Өдрөөр")
    during_the_hours = models.BooleanField(default=False, null=True, verbose_name="Цагаар")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee_request")

    status = models.CharField(choices=STATUS_CHOICES, max_length=100, default=WAITING)
    # agreed = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="agreed_request", null=True)
    # resolved_date = models.DateTimeField(null=True, blank=True, verbose_name='Шийдвэрлэгдсэн хугацаа')
    # reason_for_rejection = models.CharField(max_length=500, null=True, blank=True, verbose_name='Татгалзсан шалтгаан')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Correspond_Answer(models.Model):
    """ Дүйцүүлэлтэнд хариу илгээсэн бүртгэл
    """

    request = models.ForeignKey(RequestTimeVacationRegister, on_delete=models.PROTECT, verbose_name='Чөлөөний хүсэлт')
    org_position = models.ForeignKey(OrgPosition, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Хариулсан албан тушаалтан")
    date = models.DateField(verbose_name="Хариулсан огноо")
    is_confirm = models.BooleanField(default=False, verbose_name="Зөвшөөрсөн эсэх")
    message = models.CharField(max_length=500, null=True, verbose_name="Тайлбар")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Хэн баталсан")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TimeScheduleRegister(models.Model):
    """ Ажилтаны цаг бүртгэл
    """

    KIND_WORKING = 1
    KIND_TAS = 2
    KIND_AJILTAI_SHALTGAAN = 3
    KIND_AMRALT = 4
    KIND_AMRALT_SHALTGAAN = 5
    KIND_SHALTGAAN = 6
    KIND_AMRALT_AJLIIN = 7

    KIND_CHOICES = (
        (KIND_WORKING, 'Ажилласан'),
        (KIND_TAS, 'Тасалсан'),
        (KIND_AJILTAI_SHALTGAAN, 'Ажлын өдөр шалтгаантай'),

        (KIND_AMRALT, 'Амралт'),
        (KIND_AMRALT_SHALTGAAN, 'Шалтгаантай мөртлөө амралтын өдөр'),

        (KIND_SHALTGAAN, 'Шалтгаантай өдөр ажлын амралтын гэдэг нь мэдэгдээгүй'),

        (KIND_AMRALT_AJLIIN, 'Ажлын өдөр тусгай амралт таарсан өдөр')
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    date = models.DateField(verbose_name='Хэдний өдрийн цаг бүртгэл гэдгийг илтгэх')
    in_dt = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, verbose_name="Ирсэн цаг")
    lunch_in_dt = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, verbose_name="Цайны цагтаа орсон цаг")
    worked_time = models.CharField(max_length=30, null=True, blank=True, verbose_name="Ажилласан цаг")
    out_dt = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, verbose_name="Явсан цаг")
    lunch_out_dt = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, verbose_name="Цайны цагаасаа ирсэн цаг")
    kind = models.IntegerField(choices=KIND_CHOICES, null=False, blank=False, verbose_name='Цаг бүртгэлийн төрөл')
    for_shaltgaan = models.ForeignKey(RequestTimeVacationRegister, null=True, blank=True, on_delete=models.CASCADE)
    fine = models.IntegerField(default=0, verbose_name="Торгуултай бол торгуулийн дүн")

    hotsorson_time = models.CharField(max_length=30, null=True, blank=True, verbose_name="Хоцорсон цаг")

    @staticmethod
    def get_filter(request):
        filters = {
            "org": request.org_filter.get("org")
        }

        if "sub_org" in request.org_filter:
            filters['sub_org'] = request.org_filter.get("sub_org").id

        if "salbar" in request.org_filter:
            filters['salbar'] = request.org_filter.get("salbar").id

        return filters


class TimeScheduleType(models.Model):
    ''' Ажлын цагийн төрөл
    '''
    name = models.CharField(default='', max_length=30, verbose_name="Ажлын цагийн төрөлийн нэр")
    uyn_khatan = models.BooleanField(default=False, verbose_name="Уян хатан хуваарь")
    start_time = models.TimeField(null=True, verbose_name="Эхлэх цаг")
    end_time = models.TimeField(null=True, verbose_name="Дуусах цаг")
    lunch_time_start_time = models.TimeField(null=True, verbose_name="Цайны цаг эхлэх")
    lunch_time_end_time = models.TimeField(null=True, verbose_name="Цайны цаг дуусах")
    registration_start_time = models.TimeField(null=True, blank=True, verbose_name='Ирсэн цаг бүртгэж эхлэх хугацаа')
    registration_end_time = models.TimeField(null=True, blank=True,verbose_name='Явсан цаг бүртгэж дуусах хугацаа')
    time_range = models.IntegerField(default=0, null=True, verbose_name='Ирэх, явах цагийн хязгаар')
    org = models.ForeignKey(Orgs, on_delete=models.CASCADE, verbose_name='Байгууллага')

    # V2
    hotorch_boloh_limit = models.TimeField(null=True, blank=True, verbose_name='Хоцорч болох лимит')


class WorkingTimeScheduleType(models.Model):
    ''' Ажиллах цагийн хуваарийн төрөл
    '''

    TYPE_CODE = {
        'seven_days': 1,                      # 7 хоногийн өдрүүдээр
        'xy_days': 2,                         # Ажлын X хоног, амралтын Y хоног
        'independent_days': 3                 # Үл хамаарагдах цаг (зүгээр ирсэн явсан цагийг бүртгэнэ)
    }

    name = models.CharField(max_length=250, verbose_name='Ажиллах цагийн хуваарийн төрөл', null=False)
    code = models.CharField(max_length=250, default=0, verbose_name='Ажиллах цагийн хуваарийг илэрхийлэх код', null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WorkingTimeSchedule(models.Model):
    ''' Ажиллах цагийн хуваарь
    '''
    name = models.CharField(default='', max_length=250, verbose_name="Ажлын цагийн хуваарийн нэр")
    type = models.ForeignKey(WorkingTimeScheduleType, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн хуваарийн төрөл")
    vacation = models.BooleanField(default=False, verbose_name="Амралтын өдрүүдэд ажиллана")
    holiday = models.BooleanField(default=False, verbose_name="Баярын өдрүүдэд ажиллана")
    description = models.CharField(default='', max_length=250, verbose_name="Тайлбар")
    start_time_penalty = models.IntegerField(default=0, null=True, verbose_name='Ирэх, явах цагийн хязгаар')
    end_time_penalty = models.IntegerField(default=0, null=True, verbose_name='Ирэх, явах цагийн хязгаар')

    # XY ажлын төрөлийн утгууд
    ajillah_time = models.IntegerField(null=True, verbose_name='Ажиллах цаг')
    amrah_time = models.IntegerField(null=True, verbose_name='Амрах цаг')
    lunch_time = models.TimeField(null=True, blank=True, verbose_name="Цайны цагийн хугацаа")
    registration_start_time = models.TimeField(null=True, blank=True, verbose_name="Ирсэн цаг бүртгэж эхлэх хугацаа")
    registration_end_time = models.TimeField(null=True, blank=True, verbose_name="Явсан цаг бүртгэж эхлэх хугацаа")
    hotorch_boloh_limit = models.TimeField(null=True, blank=True, verbose_name='Хоцорч болох лимит')

    # 7 хоногийн ажлын төрөлийн утгууд
    mon_work = models.BooleanField(default=False, verbose_name="Ажиллана")
    tue_work = models.BooleanField(default=False, verbose_name="Ажиллана")
    wed_work = models.BooleanField(default=False, verbose_name="Ажиллана")
    thu_work = models.BooleanField(default=False, verbose_name="Ажиллана")
    fri_work = models.BooleanField(default=False, verbose_name="Ажиллана")
    sat_work = models.BooleanField(default=False, verbose_name="Ажиллана")
    sun_work = models.BooleanField(default=False, verbose_name="Ажиллана")

    mon_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="mon_time_schedule")
    tue_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="tue_time_schedule")
    wed_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="wed_time_schedule")
    thu_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="thu_time_schedule")
    fri_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="fri_time_schedule")
    sat_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="sat_time_schedule")
    sun_time_schedule = models.ForeignKey(TimeScheduleType, null=True, on_delete=models.CASCADE, verbose_name="Ажиллах цагийн төрөл", related_name="sun_time_schedule")

    org = models.ForeignKey(Orgs, on_delete=models.CASCADE, verbose_name='Байгууллага')
    employees = models.ManyToManyField(Employee, blank=True)


class OtherImages(models.Model):
    image = models.ImageField(upload_to="other/chigluuleh", null=True, blank=True, verbose_name='Контентийн зураг')

    @staticmethod
    def delete_images(image_paths=[]):
        for image_path in image_paths:
            qs = OtherImages.objects.filter(image=image_path)
            for row in qs:
                row.image.delete()
                row.delete()


class XyTimeScheduleValues(models.Model):
    ''' Xy ажлын цагийн утгууд
    '''
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, null=False, blank=False)
    start_date = models.DateTimeField(auto_now_add=False, blank=True, null=True, verbose_name="Ажилын эхний өдрийн он сар")
    start_next_job_date = models.DateTimeField(auto_now_add=False, blank=True, null=True, verbose_name="Дараачийн ажлын эхлэх цаг")
    start_next_vacation_date = models.DateTimeField(auto_now_add=False, blank=True, null=True, verbose_name="Дараачийн амралтын эхлэх цаг")

    created_at = models.DateTimeField(auto_now_add=True)


class ChigluulehHutulbur(models.Model):
    """ Шинэ ажилтны чиглүүлэх хөтөлбөр """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    name = models.CharField(max_length=500, null=False, blank=False, verbose_name="Нэр")
    description = models.TextField(verbose_name="Тайлбар", null=True, blank=True)
    pdfs = models.ManyToManyField(Attachments, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Surgalt(models.Model):
    """ Сургалт, сургалтын төлөвлөгөө """

    FOR_WHOLE = 'whole'
    FOR_USERS = 'users'

    FOR_TYPE_CHOICES = (
        (FOR_WHOLE, 'Байгууллагын хүмүүсд'),
        (FOR_USERS, 'Оноогдсон хүмүүсд')
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    name = models.CharField(max_length=500, null=False, blank=False, verbose_name="Нэр")
    purpose = models.CharField(max_length=1500, null=False, blank=False, verbose_name="Зориулалт")
    for_type = models.CharField(choices=FOR_TYPE_CHOICES, max_length=100, null=False, blank=False)
    for_count = models.IntegerField(default=0, verbose_name="Суралцагчдын тоо")

    #  зөвхөн is_all false  байхад л бөглөнө
    employees = models.ManyToManyField(Employee, blank=True, verbose_name="Хэрэглэгчид")

    start_date = models.DateField(verbose_name="Сургалт эхлэх огноо")
    end_date = models.DateField(verbose_name="Сургалт дуусах огноо")

    start_time = models.TimeField(verbose_name="Сургалт эхлэх цаг")
    end_time = models.TimeField(verbose_name="Сургалт дуусах цаг")

    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="created_user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WorkCalendarKind(models.Model):
    """ Тухайн байгууллагын Ажлын календарийн төрөл """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    title = models.CharField(max_length=250, null=False, blank=False)
    textColor = models.CharField(max_length=250, null=True, blank=True, default="#ccc")
    color = models.CharField(max_length=250, null=True, blank=True, default="#3788D8")

    @staticmethod
    def get_tomilolt():
        return {
            "id": "tomilolt",
            "title": "Томилолт",
            "textColor": "white",
            "color": '#B6CA69',
            'is_extra': True
        }

    @staticmethod
    def get_surgalt():
        return {
            "id": "surgalt",
            "title": "Сургалт",
            "textColor": "black",
            "color": '#33E9FF',
            'is_extra': True
        }

    @staticmethod
    def get_extra_kinds():
        extra_kinds = [
            WorkCalendarKind.get_tomilolt(),
            WorkCalendarKind.get_surgalt()
        ]
        return extra_kinds


class WorkCalendar(models.Model):
    """ Ажлын календарь """

    FOR_WHOLE = 'whole'
    FOR_USERS = 'users'

    FOR_TYPE_CHOICES = (
        (FOR_WHOLE, 'Байгууллагын хүмүүсд'),
        (FOR_USERS, 'Оноогдсон хүмүүсд')
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    title = models.CharField(max_length=255, verbose_name="Гарчиг", null=False, blank=False)
    kind = models.ForeignKey(WorkCalendarKind, on_delete=models.CASCADE, verbose_name="Төрөл")

    start_date = models.DateTimeField(verbose_name="Эхлэх огноо")
    end_date = models.DateTimeField(verbose_name="Дуусах огноо")

    is_all_day = models.BooleanField(default=False, verbose_name="Бүх өдөр")
    url = models.URLField(null=True, blank=True, max_length=200,)
    for_type = models.CharField(choices=FOR_TYPE_CHOICES, max_length=100, null=False, blank=False)

    location = models.CharField(max_length=1000, verbose_name="Байршил", null=True, blank=True)
    description = models.CharField(max_length=2500, verbose_name="Тайлбар")

    employees = models.ManyToManyField(Employee, verbose_name="Хэрэглэгчид")

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_tomilolt(request, employee_ids, extra_filter={}):
        for_type = WorkCalendar.FOR_USERS
        return list(
            Tomilolt
                .objects
                .filter(**request.exactly_org_filter, employees__in=employee_ids, **extra_filter)
                .annotate(
                    textColor=Value(WorkCalendarKind.get_tomilolt()['textColor'], models.CharField()),
                    color=Value(WorkCalendarKind.get_tomilolt()['color'], models.CharField()),
                    title=Value(WorkCalendarKind.get_tomilolt()['title'], models.CharField()),
                    work_title=models.F('for_tomilolt__name'),
                    start=models.F('start_date'),
                    end=models.F('end_date'),
                    for_type=Value(for_type, models.CharField()),
                    editable=Value(False, models.BooleanField()),
                    kind=Value(WorkCalendarKind.get_tomilolt()['id'], models.CharField()),
                    url=Concat(Value('/worker/designation/?id='), models.F('id'), output_field=models.CharField()),
                )
                .values(
                    "textColor",
                    "color",
                    "title",
                    "work_title",
                    "start",
                    "end",
                    "editable",
                    'kind',
                    'url',
                    'for_type',
                )
                .annotate(
                    id=Concat(Value("tomilolt_"), models.F("id"), output_field=models.CharField())
                )
        )

    @staticmethod
    def get_surgalt(request, employee_ids, is_all, extra_filter={}):
        filters = {**request.exactly_org_filter}
        if employee_ids:
            filters['employees__in'] = employee_ids

        if is_all:
            filters['for_type'] = Surgalt.FOR_WHOLE

        return list(
            Surgalt
                .objects
                .filter(**filters, **extra_filter)
                .annotate(
                    textColor=Value(WorkCalendarKind.get_surgalt()['textColor'], models.CharField()),
                    color=Value(WorkCalendarKind.get_surgalt()['color'], models.CharField()),
                    title=Value(WorkCalendarKind.get_surgalt()['title'], models.CharField()),
                    work_title=models.F('name'),
                    start=Concat(models.F('start_date'), Value(" "), models.F('start_time'), output_field=models.DateTimeField()),
                    end=Concat(models.F('end_date'), Value(" "), models.F('end_time'), output_field=models.DateTimeField()),
                    editable=Value(False, models.BooleanField()),
                    kind=Value(WorkCalendarKind.get_surgalt()['id'], models.CharField()),
                    url=Concat(Value('/surgalt/surgalt-list/?id='), models.F('id'), output_field=models.CharField()),
                    today_time=Concat(
                        Func(
                            models.F('start_time'),
                            Value('HH24:MM'),
                            function='to_char',
                            output_field=models.CharField()
                        ),
                        Value(" "),
                        Func(
                            models.F('end_time'),
                            Value('HH24:MM'),
                            function='to_char',
                            output_field=models.CharField()
                        ),
                        output_field=models.CharField()
                    )
                )
                .values(
                    "textColor",
                    "color",
                    "title",
                    "work_title",
                    "start",
                    "end",
                    "editable",
                    'kind',
                    'url',
                    'for_type',
                    'today_time'
                )
                .annotate(
                    id=Concat(Value("surgalt_"), models.F("id"), output_field=models.CharField())
                )
        )

    @staticmethod
    def get_extra_kind_datas(request, employee_ids=[], for_type=''):
        parsed_ids = employee_ids if isinstance(employee_ids, list) else [employee_ids]
        return WorkCalendar.get_tomilolt(request, parsed_ids) + WorkCalendar.get_surgalt(request, parsed_ids, for_type)


class FeedbackKind(models.Model):
    """ Санал хүсэлтийн төрөл """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    title = models.CharField(max_length=250, null=False, blank=False, verbose_name="Гарчиг")
    rank = models.IntegerField(default=0, verbose_name="Эрэмбэ")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rank']


class Feedback(models.Model):
    """ Санал хүсэлтийн төрөл """

    FROM_KIND_EMPLOYEE = 1
    FROM_KIND_CUSTOMER = 2
    FROM_KIND_PARTNER = 3

    FROM_KIND = (
        (FROM_KIND_EMPLOYEE, "Ажилтнаас"),
        (FROM_KIND_CUSTOMER, "Үйлчлүүлэгч"),
        (FROM_KIND_PARTNER, "Хамтран ажиллагч"),
    )

    STATE_NEW = 1
    STATE_GRANTED = 2
    STATE_CANCELED = 3

    STATE_CHOICES = (
        (STATE_NEW, "Илгээсэн"),
        (STATE_GRANTED, "Зөвшөөрсөн"),
        (STATE_CANCELED, "Цуцлагдсан"),
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    title = models.CharField(max_length=250)
    kind = models.ForeignKey(FeedbackKind, on_delete=models.CASCADE)
    to_employees = models.ForeignKey(Employee, related_name="to_employees", on_delete=models.CASCADE, null=True, blank=True)
    main_content = models.TextField()

    from_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="from_employee", null=True, blank=True)
    from_employee_kind = models.IntegerField(choices=FROM_KIND, default=FROM_KIND_EMPLOYEE)

    from_user_name = models.CharField(max_length=250, null=True, blank=True)
    from_user_email = models.EmailField(null=True, blank=True)

    decided_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="decided_employee", null=True, blank=True)
    decided_content = models.TextField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    comment = models.TextField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachments)
    commands = models.ManyToManyField(Attachments, related_name="commands", blank=True)

    is_meeting = models.BooleanField(default=False)

    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NEW)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ForTomilolt(models.Model):
    """ Томилолт ямар ажлаар """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    name = models.CharField(max_length=250, null=False, blank=False, verbose_name="Гарчиг")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tomilolt(models.Model):
    """ Томилолт """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    unit1 = models.ForeignKey(Unit1, on_delete=models.CASCADE, null=True, blank=True)
    unit2 = models.ForeignKey(Unit2, on_delete=models.CASCADE, null=True, blank=True)
    unit3 = models.ForeignKey(Unit3, on_delete=models.CASCADE, null=True, blank=True)

    isForeign = models.BooleanField(default=False, verbose_name="Гадаадруу томилолтод явах эсэх")
    foreignCountry = models.CharField(max_length=250, null=True, blank=True, verbose_name="Гадаад явах улс or хаяг")

    employees = models.ManyToManyField(Employee)
    attachments = models.ManyToManyField(Attachments)

    for_tomilolt = models.ForeignKey(ForTomilolt, on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    days = models.IntegerField(default=0)

    deleted_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="deleted_by", null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="created_by")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def get_image_path(instance, filename):
    """ Асуултын файлын замыг зааж байна """
    return os.path.join('survery', 'questions', "asuult_%s" % str(instance.id), filename)


class QuestionChoices(models.Model):
    """ Асуултын сонолттой асуултын сонголтууд """
    choices = models.CharField(verbose_name="Сонголт", max_length=250, null=False, blank=False)

    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SurveyQuestions(models.Model):
    """ Судалгааны асуултууд """

    KIND_ONE_CHOICE = 1
    KIND_MULTI_CHOICE = 2
    KIND_BOOLEAN = 3
    KIND_RATING = 4
    KIND_TEXT = 5

    KIND_CHOICES = (
        (KIND_ONE_CHOICE, 'Нэг сонголт'),
        (KIND_MULTI_CHOICE, 'Олон сонголт'),
        (KIND_BOOLEAN, 'Тийм, Үгүй сонголт'),
        (KIND_RATING, 'Үнэлгээ'),
        (KIND_TEXT, 'Бичвэр'),
    )

    kind = models.IntegerField(choices=KIND_CHOICES, null=False, blank=False, verbose_name='Асуултын төрөл')
    question = models.CharField(max_length=1000, null=False, blank=False, verbose_name="Асуулт")

    is_required = models.BooleanField(default=False, verbose_name="Заавал санал өгөх эсэх")
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True, verbose_name='зураг')

    #  KIND_RATING үед
    rating_max_count = models.IntegerField(default=0, verbose_name="Үнэлгээний дээд тоо", null=True, blank=True)
    low_rating_word = models.CharField(max_length=100, verbose_name="Доод үнэлгээг илэрхийлэх үг")
    high_rating_word = models.CharField(max_length=100, verbose_name="Дээд үнэлгээг илэрхийлэх үг")

    #  KIND_MULTI_CHOICE үед
    max_choice_count = models.IntegerField(default=0, verbose_name="Сонголтын хязгаар", null=True, blank=True)

    # KIND_ONE_CHOICE болон KIND_MULTI_CHOICE үед
    choices = models.ManyToManyField(QuestionChoices)

    is_rate_teacher = models.BooleanField(default=False, verbose_name='Багшийн үнэлэх асуулт эсэх')

    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Survey(models.Model):
    """ Судалгааны ажил """

    KIND_ALL = 1
    KIND_ORG = 2
    KIND_SUB_ORG = 3
    KIND_SALBAR = 4
    KIND_POSITIONS = 5
    KIND_EMPLOYEES = 6

    KIND_CHOICES = (
        (KIND_ALL, 'Нийт'),
        (KIND_ORG, 'Байгууллагын хүрээнд'),
        (KIND_SUB_ORG, 'Дэд байгууллагын хүрээнд'),
        (KIND_SALBAR, 'Нэгжийн хүрээнд'),
        (KIND_POSITIONS, 'Албан тушаалын хүрээнд'),
        (KIND_EMPLOYEES, 'Алба хаагчдын хүрээнд'),
    )

    #  Хамрах хүрээ нь
    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ManyToManyField(SubOrgs, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ManyToManyField(Salbars, blank=True, verbose_name="Салбар")
    org_positions = models.ManyToManyField(OrgPosition, blank=True, verbose_name="Албан тушаал")
    employees = models.ManyToManyField(Employee, blank=True, verbose_name="Албан хаагч")
    is_all = models.BooleanField(default=True, verbose_name="Системийн хүрээнд")

    kind = models.IntegerField(choices=KIND_CHOICES, null=False, blank=False)

    title = models.CharField(max_length=250, null=False, blank=False, verbose_name="Гарчиг")
    description = models.TextField(null=False, blank=False, verbose_name="Тайлбар")
    image = models.ImageField(upload_to="survery", null=True, blank=True, verbose_name='зураг')

    questions = models.ManyToManyField(SurveyQuestions)

    start_date = models.DateTimeField(null=False, blank=False, verbose_name="Эхлэх хугацаа")
    end_date = models.DateTimeField(null=False, blank=False, verbose_name="Дуусах хугацаа")

    has_shuffle = models.BooleanField(default=False, verbose_name="Холих эсэх")
    is_required = models.BooleanField(default=False, verbose_name="Заавал бөглөх эсэх")
    is_hide_employees = models.BooleanField(default=False, verbose_name="Бөглөсөн албан хаагчдыг нуух эсэх")

    created_org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага", related_name="created_org")
    created_sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж", related_name="created_sub_org")
    created_salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар", related_name="created_salbar")

    deleted_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="deleted", null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_filter(request):
        filters = {}
        org_filter = request.exactly_org_filter
        filters['created_org'] = org_filter.get("org") if org_filter.get("org") else None
        filters['created_sub_org'] = org_filter.get("sub_org") if org_filter.get("sub_org") else None
        filters['created_salbar'] = org_filter.get("salbar") if org_filter.get("salbar") else None
        return filters

    @staticmethod
    def get_state_filter(state_name):
        dn = dt.now()
        return {
            "all": {},
            "waiting": {
                "start_date__gt": dn
            },
            "progressing": {
                "start_date__lte": dn,
                "end_date__gt": dn,
            },
            "finish": {
                "end_date__lte": dn,
            },
        }.get(state_name)


class Pollee(models.Model):
    """ Судалгаанд оролцогчид """

    question = models.ForeignKey(SurveyQuestions, on_delete=models.CASCADE, verbose_name="Асуулт")
    answer = models.TextField(verbose_name="Хариулт", null=True)

    # KIND_ONE_CHOICE болон KIND_MULTI_CHOICE үед
    choosed_choices = models.ManyToManyField(QuestionChoices, verbose_name="Сонгосон сонголтууд", blank=True)

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmployeeDonation(models.Model):
    ALLOWANCE = 1
    HELP_HAND = 2

    DONATE_TYPE = (
        (ALLOWANCE, 'Тэтгэмж'),
        (HELP_HAND, 'Буцалтгүй тусламж'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_index=True , verbose_name="Ажилтан")

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    type = models.IntegerField(choices=DONATE_TYPE, null=False, blank=False, verbose_name='Тэтгэмжийг төрөл')
    description = models.TextField(null=False, blank=False, verbose_name="Тайлбар")
    total_cost = models.IntegerField(null=True, default=0, verbose_name="Нийт үнийн дүн")

    donate_date = models.DateField(verbose_name="Төгссөн он сар", default='2022-01-01')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StaticShagnal(models.Model):
    """ Байгууллага бүр болон ажилчин болгон авах боломжтой шагналууд """

    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Нэр")
    order = models.IntegerField(default=0, null=False, blank=False, verbose_name="Зэрэглэл")

    def save(self, *args, **kwargs):
        is_create = not self.pk
        if is_create:
            self.order = StaticShagnal.objects.aggregate(most_min=models.Min('order'))['most_min'] - 1
        super(StaticShagnal, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(StaticShagnal, self).delete(*args, **kwargs)
        #  TODO: шаардлагатай гэж үзвэл тоонуудыг reset хийх нь


class Shagnal(models.Model):
    """ Тухайн байгууллагад л байдаг шагнал урамшуулал """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")

    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Нэр")
    order = models.IntegerField(default=0, null=False, blank=False, verbose_name="Зэрэглэл")

    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_filter(request):
        return {
            "org": request.exactly_org_filter.get("org")
        }

    def save(self, *args, **kwargs):
        is_create = not self.pk
        if is_create:
            if Shagnal.objects.count() > 0:
                self.order = Shagnal.objects.aggregate(most_max=models.Max('order'))['most_max'] + 1
        super(Shagnal, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Shagnal, self).delete(*args, **kwargs)
        #  TODO: шаардлагатай гэж үзвэл тоонуудыг reset хийх нь


class ShagnalEmployee(models.Model):
    """ Шагнал авсан ажилчид """

    KIND_STATIC = 1
    KIND_DYNAMIC = 2

    KIND_CHOICES = (
        (KIND_STATIC, 'static'),
        (KIND_DYNAMIC, 'dynamic'),
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    kind = models.IntegerField(choices=KIND_CHOICES)
    what_year = models.DateTimeField()
    desc = models.TextField(verbose_name="Тайлбар", null=True, blank=True)
    shagnal = models.ForeignKey(Shagnal, on_delete=models.CASCADE, null=True, blank=True)
    static_shagnal = models.ForeignKey(StaticShagnal, on_delete=models.CASCADE, null=True, blank=True)

    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Sahilga(models.Model):
    """ Сахилга шийтгэл """

    STATE_ACTIVE = 1
    STATE_REFUSED = 2
    STATE_FINISHED = 3

    STATE_CHOICES = (
        (STATE_ACTIVE, "Идэвхтэй"),
        (STATE_REFUSED, "Цуцлагдсан"),
        (STATE_FINISHED, "Дууссан"),
    )

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachments, blank=False)

    during_month = models.IntegerField(default=0, null=True, blank=True)
    percent = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )

    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_ACTIVE)

    start_date = models.DateField(verbose_name="Эхлэх он сар")
    end_date = models.DateField(verbose_name="Дуусах он сар")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Цуцласан", related_name="++")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AlbanTushaaliinTodGeneral(models.Model):
    turiin_albanii_huulitai_holbootoi = models.BooleanField(default=False, verbose_name="Төрийн албаны тухай хууль хэрэгжиж эхэлсэнтэй холбогдуулан шинэчлэн боловсруулсан")
    huuli_togtoomjtoi_holbootoi_chiglel_vvrgiin_oorchlolt = models.BooleanField(default=False, verbose_name="Хууль тогтоомжоор байгууллагын чиг үүрэгт өөрчлөлт орсон")

    chig_vvreg_oorchlogdson_ner = models.CharField(max_length=250, verbose_name='Холбогдох хууль тогтоомжийн нэр', null=True, blank=True)
    chig_vvreg_oorchlogdson_ognoo = models.DateField(verbose_name="Холбогдох хууль тогтоомжийн огноо")
    dagaj_murduh_ognoo = models.DateField(verbose_name="Дагаж мөрдөх огноо")
    alban_tushaal_batalsan_ognoo = models.DateField(verbose_name="Албан тушаалын тодорхололтыг баталсан огноо")

    negj = models.CharField(max_length=250, verbose_name='Нэгжийн нэр', null=True, blank=True)
    alban_tushaal_angilal = models.CharField(max_length=250, verbose_name='Албан тушаалын ангилал', null=True, blank=True)
    ajliin_tsag = models.CharField(max_length=250, verbose_name='Ажлын цаг', null=True, blank=True)
    ajliin_bairnii_bairshil = models.CharField(max_length=250, verbose_name='Ажлын байрны албан ёсны байршил', null=True, blank=True)
    hudulmuriin_nuhtsul = models.CharField(max_length=250, verbose_name='Хөдөлмөрийн нөхцөл', null=True, blank=True)
    ontsgoi_nuhtsul = models.CharField(max_length=250, verbose_name='Онцгой нөхцөл', null=True, blank=True)


class AlbanTushaaliinTodZorilgo(models.Model):
    alban_tushaaliin_zorilgo = models.TextField(verbose_name='Албан тушаалын зорилго', null=True, blank=True)


class AlbanTushaaliinZorilt(models.Model):
    zorilgo = models.ForeignKey(AlbanTushaaliinTodZorilgo, on_delete=models.CASCADE, null=False, blank=False)
    desicription = models.CharField(max_length=250, verbose_name='Албан тушаалын тодорхойлолтын албан тушаалых нь зорилт')


class AlbanTushaaliinZoriltiinVvreg(models.Model):
    TUSLAH = 1
    GVITSETGEH = 2
    HYNAH = 3
    SHIIDWERLEH = 4

    OROLTSOONII_TURUL = (
        (TUSLAH, 'Туслах'),
        (GVITSETGEH, 'Хариуцан гүйцэтгэх'),
        (HYNAH, 'Хянах'),
        (SHIIDWERLEH, 'Шийдвэрлэх'),
    )

    zorilt = models.ForeignKey(AlbanTushaaliinZorilt, on_delete=models.CASCADE, null=False, blank=False)
    vvreg = models.CharField(max_length=500, verbose_name="", null=True, blank=True)
    shalguur = models.CharField(max_length=500, verbose_name="", null=True, blank=True)
    oroltsoonii_turul = ArrayField(
        models.PositiveIntegerField(choices=OROLTSOONII_TURUL, blank=True),
    )


class AlbanTushaalSubject(models.Model):
    hariyalan_udirdah_alban_tushaaliin_ner = models.CharField(max_length=250, verbose_name="Албан тушаалыг шууд харьялан удирдах албан тушаалын нэр")
    # Албан тушаалд шууд харьялан удирдуулах албан тушаалын нэр, тоо
    ahlah_mergejilten = models.CharField(max_length=250, verbose_name="Ахлах мэргэжилтэн")
    mergejilten = models.CharField(max_length=250, verbose_name="Mэргэжилтэн")
    turiin_vilchilgeenii_alban_haagch = models.CharField(max_length=250, verbose_name="Төрийн үйлчилгээний албан хаагч")
    niit = models.IntegerField(verbose_name="Нийт", default=0)
    busad_hariltsah_subject = ArrayField(
        models.CharField(max_length=250, verbose_name='Бусад харилцах субъект')
    )


class AlbanTushaalShaardlaga(models.Model):
    bolowsor = models.CharField(max_length=250, verbose_name='Албан тушаалд тавигдах тусгай шаардлага боловсрол')
    mergejil = ArrayField(
        models.CharField(max_length=250, verbose_name='Албан тушаалд тавигдах тусгай шаардлага мэргэжил')
    )
    mergeshil = models.CharField(max_length=250, verbose_name='Мэргэшил', null=True, blank=True)
    turshlaga = models.CharField(max_length=250, verbose_name='Туршлага', null=True, blank=True)

    udirdan_zohion_baiguulah = ArrayField(
        models.CharField(max_length=250, verbose_name='Удирдан зохион байгуулах ур чадвар')
    )
    dvn_shinjilgee_hiih = ArrayField(
        models.CharField(max_length=250, verbose_name='Дүн шинжилгээ хийх ур чадвар')
    )
    asuudal_shiidwerleh = ArrayField(
        models.CharField(max_length=250, verbose_name='Асуудал шийдвэрлэх')
    )
    manlailah = ArrayField(
        models.CharField(max_length=250, verbose_name='Манлайлах')
    )
    busad = ArrayField(
        models.CharField(max_length=250, verbose_name='Бусад')
    )


class AlbanTushaalBatalgaajuulalt(models.Model):
    todorhoiloltiig_bolowsruulsan = models.CharField(max_length=250, verbose_name='Албан тушаалын тодорхойлолтыг боловсруулсан')
    todorhoiloltiig_batlah_zowshoorol = models.CharField(max_length=250, verbose_name='Албан тушаалын тодорхойлолтыг хянаж, батлах зөвшөөрөл олгосон байгууллагын шийдвэр')

    alban_tushaal = models.CharField(max_length=250, verbose_name='Албан тушаал')

    baiguullagiin_ner = models.CharField(max_length=250, verbose_name='Байгууллагын нэр')
    shiidweriin_ognoo_batalgaajuulalt = models.DateField(verbose_name='Шийдвэрийн огноо', null=True, blank=True)
    dugaar_batalgaajuulalt = models.IntegerField(verbose_name='Шийдвэрийн дугаар')


class AlbanTushaaliinTodorhoilolt(models.Model):
    """ Албан тушаалын тодорхойлолт """

    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    org_position = models.OneToOneField(OrgPosition, on_delete=models.CASCADE, null=False, blank=False, default='')

    # I Ерөнхий мэдээлэл
    general = models.OneToOneField(AlbanTushaaliinTodGeneral, on_delete=models.CASCADE, null=False, blank=False, default='')
    # II Албан тушаалын зорилго, зорилт, чиг үүрэг
    zorilgo_zorilt = models.OneToOneField(AlbanTushaaliinTodZorilgo, on_delete=models.CASCADE, null=False, blank=False, default='')
    # III Албан тушаалд тавигдах тусгай шаардлага
    shaardlaga = models.OneToOneField(AlbanTushaalShaardlaga, on_delete=models.CASCADE, null=False, blank=False, default='')
    # IV Албан тушаалтны харилцах субъект
    subject = models.OneToOneField(AlbanTushaalSubject, on_delete=models.CASCADE, null=False, blank=False, default='')
    # V Албан тушаалын тодорхойлолт баталгаажуулах
    batalgaajuulalt = models.OneToOneField(AlbanTushaalBatalgaajuulalt, on_delete=models.CASCADE, null=False, blank=False, default='')

    org_name = models.CharField(max_length=250, null=True, blank=True)
    shiidweriin_ognoo = models.DateField(null=True, blank=True)
    dugaar = models.CharField(max_length=250, null=True, blank=True)
    darga = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationType(models.Model):
    """ notif ийн төрөл """
    name = models.CharField(max_length=255, null=False, blank=False)
    color = models.CharField(max_length=255, null=False, blank=False)
    code = models.CharField(max_length=255, null=True, blank=True, unique=True)
    level = models.IntegerField(default=0)


class Notification(models.Model):
    """ Үндсэн notif """

    SCOPE_KIND_ORG = 1
    SCOPE_KIND_SUBORG = 2
    SCOPE_KIND_SALBAR = 3
    SCOPE_KIND_POS = 4
    SCOPE_KIND_EMPLOYEE = 5
    SCOPE_KIND_USER = 6
    SCOPE_KIND_ALL = 7
    SCOPE_KIND_OYUTAN = 8
    SCOPE_KIND_PROFESSION = 9
    SCOPE_KIND_KURS = 10
    SCOPE_KIND_GROUP = 11

    SCOPE_KIND_CHOICES = (
        (SCOPE_KIND_ORG, 'Байгууллага'),
        (SCOPE_KIND_SUBORG, 'Дэд байгууллага'),
        (SCOPE_KIND_SALBAR, 'Салбар'),
        (SCOPE_KIND_POS, 'Албан тушаал'),
        (SCOPE_KIND_EMPLOYEE, 'Алба хаагч'),
        (SCOPE_KIND_USER, 'Хэрэглэгч'),
        (SCOPE_KIND_ALL, 'Бүгд'),
        (SCOPE_KIND_OYUTAN, 'Оюутан'),
        (SCOPE_KIND_PROFESSION, 'Мэргэжил'),
        (SCOPE_KIND_KURS, 'Курс'),
        (SCOPE_KIND_GROUP, 'Анги'),
    )

    FROM_KIND_ORG = 1
    FROM_KIND_SUBORG = 2
    FROM_KIND_SALBAR = 3
    FROM_KIND_POS = 4
    FROM_KIND_EMPLOYEE = 5
    FROM_KIND_USER = 6
    FROM_KIND_OYUTAN = 7

    FROM_KIND_CHOICES = (
        (FROM_KIND_ORG, 'Байгууллага'),
        (FROM_KIND_SUBORG, 'Дэд байгууллага'),
        (FROM_KIND_SALBAR, 'Салбар'),
        (FROM_KIND_POS, 'Албан тушаал'),
        (FROM_KIND_EMPLOYEE, 'Алба хаагч'),
        (FROM_KIND_USER, 'Хэрэглэгч'),
        (FROM_KIND_OYUTAN, 'Оюутан'),
    )

    #  notif хамрах хүрнээ
    org = models.ManyToManyField(Orgs, blank=True, verbose_name="Байгууллага")
    sub_org = models.ManyToManyField(SubOrgs, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ManyToManyField(Salbars, blank=True, verbose_name="Салбар")
    org_position = models.ManyToManyField(OrgPosition, blank=True)
    employees = models.ManyToManyField(Employee, blank=True)
    users = models.ManyToManyField(User, blank=True)
    kurs = ArrayField(
        models.IntegerField(null=True),
        blank=True,
        null=True,
    )
    profs = ArrayField(
        models.IntegerField(null=True),
        blank=True,
        null=True,
    )
    groups = ArrayField(
        models.IntegerField(null=True),
        blank=True,
        null=True,
    )
    oyutans = ArrayField(
        models.IntegerField(null=True),
        blank=True,
        null=True,
    )
    is_all = models.BooleanField(default=False)
    scope_kind = models.IntegerField(choices=SCOPE_KIND_CHOICES, null=False, blank=False)
    #  notif хамрах хүрнээ

    from_org = models.ForeignKey(Orgs, on_delete=models.CASCADE, null=True, blank=True, related_name="from_org")
    from_sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж", related_name="from_sub_org")
    from_salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар", related_name="from_salbar")
    from_org_position = models.ForeignKey(OrgPosition, on_delete=models.CASCADE, null=True, blank=True, related_name="from_pos")
    from_employees = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name="from_employees")
    from_users = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="from_user")
    from_kind = models.IntegerField(choices=FROM_KIND_CHOICES, null=False, blank=False)

    tree_org = models.ForeignKey(Orgs, on_delete=models.CASCADE, null=True, blank=True, related_name="tree_org")
    tree_sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж", related_name="tree_sub_org")
    tree_salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар", related_name="tree_salbar")
    tree_org_position = models.ForeignKey(OrgPosition, on_delete=models.CASCADE, null=True, blank=True, related_name="tree_pos")
    tree_kind = models.BooleanField(default=False)

    title = models.CharField(max_length=255, null=False, blank=False)
    ntype = models.ForeignKey(NotificationType, on_delete=models.CASCADE, null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Үүсгэсэн", related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotifManager()

    @staticmethod
    def get_filters(request):
        filters = models.Q()
        if request.org_filter.get("org"):
            filters.add(models.Q(org=request.org_filter.get("org")), models.Q.OR)
        if request.org_filter.get("sub_org"):
            filters.add(models.Q(sub_org=request.org_filter.get("sub_org")), models.Q.OR)
        if request.org_filter.get("salbar"):
            filters.add(models.Q(salbar=request.org_filter.get("salbar")), models.Q.OR)
        if request.employee:
            filters.add(models.Q(employees=request.employee), models.Q.OR)
            filters.add(models.Q(org_position=request.employee.org_position), models.Q.OR)

        filters.add(models.Q(is_all=True), models.Q.OR)
        filters.add(models.Q(users=request.user), models.Q.OR)
        filters.add(models.Q(created_at__gte=request.user.date_joined), models.Q.AND)

        return filters


class NotificationState(models.Model):
    """ Тухайн notification ийг уншсан хүмүүс """

    notif = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class RoutingSlip(models.Model):
    """ Тойрох хуудас """
    PENDING = 1
    APPROVED = 2
    DECLINED = 3

    STATE_STATUS = (
        (PENDING, 'Хүлээгдэж буй'),
        (APPROVED, 'Зөвшөөрсөн'),
        (DECLINED, 'Цуцалсан'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Ажилтан")
    org = models.ForeignKey(Orgs, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    state =  models.PositiveIntegerField(choices=STATE_STATUS, db_index=True, null=False, default=PENDING, verbose_name="Өөрчлөх, үүсгэх төлөв")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн", related_name="routing_slip_created_by")
    command = models.ForeignKey(Command, on_delete=models.CASCADE, db_index=True, verbose_name="Тушаал", null=True)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RoutingSlipCommanders(models.Model):
    """ Тойрох хуудастай хамааралтай албан тушаалтануудтай холбоотой"""
    PENDING = 1
    APPROVED = 2
    DECLINED = 3

    STATE_STATUS = (
        (PENDING, 'Хүлээгдэж буй'),
        (APPROVED, 'Зөвшөөрсөн'),
        (DECLINED, 'Цуцалсан'),
    )

    routing_slip = models.ForeignKey(RoutingSlip, on_delete=models.SET_NULL, null=True, verbose_name="Тойрох хуудас")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Хариуцагч")
    state =  models.PositiveIntegerField(choices=STATE_STATUS, db_index=True, null=False, default=PENDING, verbose_name="Өөрчлөх, үүсгэх төлөв")
    org_position = models.ForeignKey(OrgPosition, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Албан тушаал")
    description = models.CharField(max_length=5000, null=True, blank=True, verbose_name="Тайлбар")

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WorkAdsense(models.Model):
    """ Ажлын зар"""
    ACTIVE = 1
    INACTIVE = 2
    ENDED = 3

    STATE_STATUS = (
        (ACTIVE, 'Идэвхтэй'),
        (INACTIVE, 'Идэвхгүй'),
    )

    org = models.ForeignKey(Orgs, blank=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    state =  models.PositiveIntegerField(choices=STATE_STATUS, db_index=True, null=False, default=ACTIVE, verbose_name="Зарын төлөв")

    org_position = models.ForeignKey(OrgPosition, on_delete=models.CASCADE, blank=False)
    description = models.TextField(null=False, blank=False)
    end_at = models.DateTimeField(verbose_name="Зар дуусах хугацаа")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WorkJoinRequests(models.Model):
    PENDING = 1
    APPROVED = 2
    DECLINED = 3
    DECLINED_BY_MYSELF = 4

    STATE_STATUS = (
        (PENDING, 'Хүлээгдэж буй'),
        (APPROVED, 'Зөвшөөрсөн'),
        (DECLINED, 'Байгууллагаас цуцалсан'),
        (DECLINED_BY_MYSELF, 'Өөрөө цуцалсан'),
    )
    org = models.ForeignKey(Orgs, blank=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")

    org_position = models.ForeignKey(OrgPosition, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    is_send_uureg = models.BooleanField(default=False, verbose_name="Шинэ ажилтны чиг үүрэг илгээсэн эсэх")

    state =  models.PositiveIntegerField(choices=STATE_STATUS, db_index=True, null=False, default=PENDING, verbose_name="Хүсэлтийн төлөв")

    work_adsense = models.ForeignKey(WorkAdsense, on_delete=models.CASCADE, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)


class UserToken(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, verbose_name="Хэрэглэгч" )

    token = models.CharField(max_length=500, null=False, blank=False, verbose_name="Токен")
    expire_date = models.DateTimeField(verbose_name="Токен дуусах хугацаа")

    created_at = models.DateTimeField(auto_now_add=True)


class FAQGroup(models.Model):
    WORKER = 1
    NOT_WORKER = 2

    TYPE = (
        (WORKER, 'Ажилтан'),
        (NOT_WORKER, 'Ажилтан биш'),
    )

    name = models.CharField(max_length=250, null=False, blank=False, verbose_name="Бүлэг асуултын нэр")
    icon = models.CharField(max_length=250, null=False, blank=False, verbose_name="Бүлэг асуултын icon")

    type =  models.PositiveIntegerField(choices=TYPE, db_index=True, null=False, default=WORKER, verbose_name="Асуулт хариултын харагдах төpөл")

    created_at = models.DateTimeField(auto_now_add=True)


class FAQ(models.Model):
    question = models.CharField(max_length=250, null=False, blank=False, verbose_name="Асуулт")
    answer = models.CharField(max_length=1000, null=False, blank=False, verbose_name="Хариулт")

    group = models.ForeignKey(FAQGroup, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class AccessHistory(models.Model):
    LOGIN = 1
    LOGOUT = 2
    STATE_TYPE = (
        (LOGIN, 'Системд нэвтэрсэн'),
        (LOGOUT, 'Системээс гарсан'),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="Хэрэглэгч")
    device = models.CharField(max_length=250, null=True, blank=True, verbose_name="Нэвтэрсэн төхөөрөмж")
    state = models.PositiveIntegerField(choices=STATE_TYPE, db_index=True, null=False, default=LOGOUT, verbose_name="Асуулт хариултын харагдах төpөл")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Нэвтэрсэн газрын мэдээлэл")
    is_mobile = models.BooleanField(default=False, verbose_name='Утсаар нэвтэрсэн эсэх')

    created_at = models.DateTimeField(auto_now_add=True)


class BankInfo(models.Model):
    """ Банкны мэдээлэл"""
    name = models.CharField(max_length=250, null=False)
    image = models.ImageField(upload_to="logo", null=True, blank=True, verbose_name='Банк лого зураг')
    order = models.IntegerField(default=0, null=False, blank=False, verbose_name="Зэрэглэл")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def delete_images(image_paths=[]):
        for image_path in image_paths:
            qs = OtherImages.objects.filter(image=image_path)
            for row in qs:
                row.image.delete()
                row.delete()

    def save(self, *args, **kwargs):
        is_create = not self.pk
        if is_create:
            most_min = BankInfo.objects.aggregate(most_min=models.Min('order'))['most_min']
            self.order = (most_min if most_min else 0) - 1
        super(BankInfo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(BankInfo, self).delete(*args, **kwargs)
        #  TODO: шаардлагатай гэж үзвэл тоонуудыг reset хийх нь


class BankAccountInfo(models.Model):
    """ Дансны мэдээлэл"""
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="Хэрэглэгч")
    bank = models.ForeignKey(BankInfo,on_delete=models.CASCADE, verbose_name="Банк")
    number = models.CharField(max_length=250, null=False, unique=True, verbose_name="Дансны дугаар")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BankAccountRequest(models.Model):
    """ Дансны мэдээлэл өөрлөх хүсэлт"""
    DELETE = 1
    UPDATE = 2
    APPROVED = 3
    DECLINED = 4
    CREATE = 5

    STATE_TYPE = (
        (DELETE, 'Устгах хүсэлт'),
        (UPDATE, 'Өөрчлөх хүсэлт'),
        (CREATE, 'Бүртгэх хүсэлт'),
        (APPROVED, 'Шийдвэрлэгдсэн'),
        (DECLINED, 'Цуцлагдсан'),
    )

    org = models.ForeignKey(Orgs, blank=True, on_delete=models.CASCADE, verbose_name="Байгууллага")
    sub_org = models.ForeignKey(SubOrgs, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Харьяалагдах алба нэгж")
    salbar = models.ForeignKey(Salbars, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Салбар")
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, db_index=True , verbose_name="Ажилтан")

    bank = models.ForeignKey(BankInfo,on_delete=models.CASCADE, verbose_name="Банк")
    number = models.CharField(max_length=250, null=False, verbose_name="Дансны дугаар")
    state = models.PositiveIntegerField(choices=STATE_TYPE, db_index=True, null=False, default=UPDATE, verbose_name="Хүсэлтийн төpөл")
    bank_account = models.ForeignKey(BankAccountInfo,on_delete=models.CASCADE, null=True, blank=True,db_index=True , verbose_name="Дансны мэдээлэл")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserProgress(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    progressing = models.JSONField()


class MainMedicalExamination(models.Model):
    ''' Бие бялдарын ерөнхий үзүүлэлт
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Хэрэглэгч")

    a_date = models.DateField(null=True, blank=True, verbose_name="Огноо")
    weight = models.CharField(max_length=255, null=True, blank=True, verbose_name="Жин")
    height = models.CharField(max_length=255, null=True, blank=True, verbose_name="Өндөр")
    weight_index = models.CharField(max_length=255, null=True, blank=True, verbose_name="Жингийн индекс")
    blood_pressure_left = models.CharField(max_length=255, null=True, blank=True, verbose_name='Зүүн цусны даралт')
    blood_pressure_right = models.CharField(max_length=255, null=True, blank=True, verbose_name='Баруун цусны даралт')
    pulse = models.CharField(max_length=255, null=True, blank=True, verbose_name='Судасны цохилт')
    eye_left = models.CharField(max_length=255, null=True, blank=True, verbose_name='Зүүн хараа')
    eye_right = models.CharField(max_length=255, null=True, blank=True, verbose_name='Баруун хараа')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AdditiveMedicalExamination(models.Model):
    ''' Бие бялдарын нэмэлт үзүүлэлт
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Хэрэглэгч")

    b_date = models.DateField(null=True, blank=True, verbose_name="Огноо")
    speed = models.CharField(max_length=255, null=True, blank=True, verbose_name='Хурд')
    power = models.CharField(max_length=255, null=True, blank=True, verbose_name='Хүч')
    flexible = models.CharField(max_length=255, null=True, blank=True, verbose_name='Уян хатан')
    endurance = models.CharField(max_length=255, null=True, blank=True, verbose_name='Тэсвэр')
    patience = models.CharField(max_length=255, null=True, blank=True, verbose_name='Тэвчээр')
    total = models.CharField(max_length=255, null=True, blank=True, verbose_name='Нийт')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InspectionType(models.Model):
    ''' Эрүүл мэндийн үзлэгийн хуудас төрөлүүд
    '''
    name = models.CharField(max_length=250, null=False)
    code = models.CharField(default=None, null=True, max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InspectionMedicalExamination(models.Model):
    ''' Эрүүл мэндийн үзлэгийн хуудас
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Хэрэглэгч")

    inspectionType = models.ForeignKey(InspectionType, on_delete=models.CASCADE, verbose_name="Эрүүл мэндийн үзлэгийн хуудас төрөл")
    inspectionText = models.TextField(null=False, blank=False, verbose_name="Утга")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Config(models.Model):

    name = models.CharField(max_length=255, null=False, unique=True)
    value = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)


class UserBookMarkPages(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)

    pages = ArrayField(
        models.CharField(max_length=500, null=False),
        blank=True,
        max_length=5,
        size=5,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Error500(models.Model):
    """ error 500 хадгалах
    """
    url = models.CharField(null=False, db_index=True, max_length=254, verbose_name='URL')
    method = models.CharField(max_length=20, null=False, db_index=True, verbose_name='Method')
    description = models.TextField(null=True, verbose_name='Алдааны мэдэгдэл')
    headers = models.TextField(null=True, verbose_name='Request headers')
    scheme = models.TextField(null=True, verbose_name='Request scheme')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Хүсэлт илгээсэн огноо')
    data = models.TextField(null=True, verbose_name='Request data')


class RequestLogGet(models.Model):
    """ Request-ийн GET method-үүдийн түүхийг хадгалах
    """
    url = models.CharField(null=False, db_index=True, max_length=254, verbose_name='URL')
    query_string = models.TextField(null=True, verbose_name='Query string')
    remote_ip = models.CharField(max_length=50, null=True, db_index=True, verbose_name='Remote IP')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Хүсэлт илгээсэн огноо')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, db_constraint=False,
                                verbose_name='Хэрэглэгчийн ID')
    status_code = models.SmallIntegerField(null=True, verbose_name='request status code')


class RequestLogPost(models.Model):
    """ Request-ийн POST method-үүдийн түүхийг хадгалах
    """
    url = models.CharField(null=False, db_index=True, max_length=254, verbose_name='URL')
    query_string = models.TextField(null=True, verbose_name='Query string')
    remote_ip = models.CharField(max_length=50, null=True, db_index=True, verbose_name='Remote IP')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Хүсэлт илгээсэн огноо')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, db_constraint=False,
                                verbose_name='Хэрэглэгчийн ID')
    data = models.TextField(null=False, verbose_name='Post data буюу body')
    status_code = models.SmallIntegerField(null=True, verbose_name='request status code')


class RequestLogPut(models.Model):
    """ Request-ийн PUT method-үүдийн түүхийг хадгалах
    """
    url = models.CharField(null=False, db_index=True, max_length=254, verbose_name='URL')
    query_string = models.TextField(null=True, verbose_name='Query string')
    remote_ip = models.CharField(max_length=50, null=True, db_index=True, verbose_name='Remote IP')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Хүсэлт илгээсэн огноо')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, db_constraint=False,
                                verbose_name='Хэрэглэгчийн ID')
    data = models.TextField(null=False, verbose_name='Put data буюу body')
    status_code = models.SmallIntegerField(null=True, verbose_name='request status code')


class RequestLogDelete(models.Model):
    """ Request-ийн DELETE method-үүдийн түүхийг хадгалах
    """
    url = models.CharField(null=False, db_index=True, max_length=254, verbose_name='URL')
    query_string = models.TextField(null=True, verbose_name='Query string')
    remote_ip = models.CharField(max_length=50, null=True, db_index=True, verbose_name='Remote IP')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Хүсэлт илгээсэн огноо')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, db_constraint=False,
                                verbose_name='Хэрэглэгчийн ID')
    status_code = models.SmallIntegerField(null=True, verbose_name='request status code')


class Errors(models.Model):
    """ error хадгалах
    """
    url = models.CharField(null=False, db_index=True, max_length=254, verbose_name='URL')
    method = models.CharField(max_length=20, null=False, db_index=True, verbose_name='Method')
    code = models.CharField(max_length=50, null=False, db_index=True, verbose_name='Алдааны дугаар')
    description = models.TextField(null=True, verbose_name='Алдааны мэдэгдэл')
    headers = models.TextField(null=True, verbose_name='Request headers')
    scheme = models.TextField(null=True, verbose_name='Request scheme')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Хүсэлт илгээсэн огноо')
    data = models.TextField(null=True, verbose_name='Request data')


class KpiIndicator(models.Model):
    """ KPI албан тушаал болгоны үзүүлэлтүүд
    """

    TOOGOOR_TYPE = 1
    HUVIAR_TYPE = 2

    INDICATOR_TYPE =(
        (TOOGOOR_TYPE, 'Тоогоор'),
        (HUVIAR_TYPE, 'Хувиар')
    )

    org_position = models.ForeignKey(OrgPosition, on_delete=models.SET_NULL, null=True, verbose_name="Албан тушаал")

    name = models.CharField(max_length=255, null=False, verbose_name='Үзүүлэлтийн нэр')
    ogogdliin_torol = models.PositiveIntegerField(choices=INDICATOR_TYPE, db_index=True, null=False, verbose_name="Хүсэлтийн төpөл")
    tolovlogoo = models.IntegerField(default=0)
    tailbar = models.TextField(null=True, verbose_name='Request data')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class KpiIndicatorAssessment(models.Model):
    """ KPI Ажилчны үнэлгээ
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, verbose_name="Ажилчин")
    onoo = models.IntegerField(default=0, null=False)
    tailbar = models.TextField(null=True, verbose_name='Тайлбар')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class KhodolmoriinGeree(models.Model):
    """ Хөдөлмөрийн гэрээ
    """

    name = models.CharField(max_length=255, null=False, verbose_name='Нэр')
    for_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилчин", related_name='for_employee')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилчин", related_name='employee')
    attachments = models.ForeignKey(Attachments, on_delete=models.CASCADE, verbose_name="Файл")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Student(models.Model):
    """ Оюутан """

    class Meta:
        db_table = 'lms_student'
        managed = False

    code = models.CharField(unique=True, max_length=50, verbose_name='Оюутны код')


class StudentLogin(models.Model):
    """ Оюутны нэвтрэх """

    class Meta:
        db_table = 'lms_studentlogin'
        managed = False

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Оюутан')

    username = models.CharField(max_length=100, verbose_name='Нэвтрэх нэр', unique=True)
    password = models.CharField(max_length=256, verbose_name='Нууц үг')


class HolidayDayInYear(models.Model):
    """ Жилийн амралтын өдрүүд
    """

    org = models.ForeignKey(Orgs, blank=True, on_delete=models.CASCADE, verbose_name="Байгууллага")

    date = models.DateField(null=True, blank=True, verbose_name="Огноо")
    every_year = models.BooleanField(default=False, verbose_name="Жил болгон давхцдаг эсэх")
    year = models.CharField(default='', null=True, max_length=50, verbose_name="Аль он", blank=True)
    name = models.CharField(max_length=256, verbose_name='Амралтын өдрийн нэр')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VacationEmployee(models.Model):
    """ Ээлжийн амралт
    """

    WAITING = 1
    DECLINED = 2
    APPROVED = 3
    CANCEL = 4

    STATE_TYPE = (
        (WAITING, 'Хүсэлт илгээгдсэн'),
        (DECLINED, 'Татгалзсан'),
        (APPROVED, 'Зөвшөөрсөн'),
        (CANCEL, 'Цуцалсан')
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилтан")
    start_date = models.DateField(null=True, blank=True, verbose_name="Төгссөн он сар")
    days = models.IntegerField(null=True, blank=True, verbose_name="Хэд хоног амрах өдөр")
    state = models.PositiveIntegerField(choices=STATE_TYPE, db_index=True, null=False, default=WAITING, verbose_name="Хүсэлтийн төpөл")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class HrOrderFormEmployee(models.Model):
    ''' Хүний нөөцийн захиалгын хуудас
    '''

    WAITING = 1
    DECLINED = 2
    APPROVED = 3
    CANCEL = 4

    STATE_TYPE = (
        (WAITING, 'Хүсэлт илгээгдсэн'),
        (DECLINED, 'Татгалзсан'),
        (APPROVED, 'Зөвшөөрсөн'),
        (CANCEL, 'Цуцалсан')
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилтан")
    file = models.FileField(upload_to="hr-order-form/%Y/%m/%d")

    state = models.PositiveIntegerField(choices=STATE_TYPE, db_index=True, null=False, default=WAITING, verbose_name="Хүсэлтийн төpөл")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ViolationRegistrationPage(models.Model):
    ''' Зөрчил бүртгэх хуудас бүртгэлүүд
    '''

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилтан")
    file = models.FileField(upload_to="violation_registration_page/%Y/%m/%d")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AnketEmployee(models.Model):
    ''' Ажилтны анкет
    '''
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилтан")
    file = models.FileField(upload_to="anket-employee/%Y/%m/%d")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NewEmployeeRegistrationForm(models.Model):
    ''' Ажилтны анкет
    '''
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Ажилтан")
    file = models.FileField(upload_to="new-employee-registration-form/%Y/%m/%d")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
