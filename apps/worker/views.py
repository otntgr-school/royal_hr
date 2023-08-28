import json
import datetime
import copy
from datetime import datetime as dateitmeGG
from datetime import date, timezone

from django.conf import settings
from django.db.models import F, Count
from django.db.models import Q
from django.db import transaction
from django.db.models import Value, CharField, Func
from django.db.models.functions import Concat
from django.db.models.functions import Substr
from django.db.models.functions import Upper

from rest_framework import mixins
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from account.serializer import Unit1Serializer, UserInfoSerializer, UserRegisterSerializer
from core.models import StaticGroupSkills
from core.fns import WithChoices
from core.models import (
    AlbanTushaaliinTodZorilgo,
    Attachments,
    ChigluulehHutulbur,
    EmployeeMigrations,
    EmployeeDonation,
    ForTomilolt,
    OrgPosition,
    OtherImages,
    Salbars,
    Tomilolt,
    Unit1,
    UserInfo,
    Employee,
    Command,
    RoutingSlip,
    RoutingSlipCommanders,
    Notification,
    UserExperience,
    SubOrgs,
    KhodolmoriinGeree,
    CountNumber,
    Orgs,
    AnketEmployee,
    NewEmployeeRegistrationForm,
)

from .serializer import TomiloltAttachListSerializer, TomiloltSerializer
from .serializer import EmployeeSerializer
from .serializer import TomiloltSerializerD
from .serializer import DonoationSerializer
from .serializer import AttachmentSerializer
from .serializer import ChigluulehSerializer
from .serializer import ForTomiloltSerializer
from .serializer import TomiloltGETSerializer
from .serializer import ChigluulehImageSerializer
from .serializer import ForTomiloltCRUDSerializer
from .serializer import TomiloltPaginateSerializer
from .serializer import DonoationPaginateSerializer
from .serializer import EmployeeMigrationsSerializer
from .serializer import EmployeePaginationSerializer
from .serializer import CommandDisplaySerializer
from .serializer import EmployeeFilterSerializer
from .serializer import RoutringSlipSerializer
from .serializer import RoutingSlipPaginationSerializer
from .serializer import RoutingSlupCommanderSerializer
from .serializer import StaticSkillsSerializer
from .serializer import RoutingSlupCommanderAllSerializer
from .serializer import EmployeeWithMigrationsSerializer
from .serializer import UserExperienceSerializer
from .serializer import EmployeeShortDataSerializer
from .serializer import RoutingSlipCommandersDataSerializer
from .serializer import EmployeeMigrationsUsedSerializer
from .serializer import KhodolmoriinGereeSerializer
from .serializer import OrgsSerializer
from .serializer import EmployeeDefinitionSerializer
from .serializer import AnketEmployeeSerializer
from .serializer import NewEmployeeRegistrationFormSerializer
from apps.command.serializer import CommandPaginationSerializer

from main.decorators import login_required
from main.decorators import has_permission

from main.utils.datatable import data_table
from main.utils.register import calculate_birthday
from main.utils.file import remove_file


class WorkerPaginationApiView(APIView):
    """ Pagination хүсэлт """

    @login_required()
    def get(self, request, state):
        qs = Employee.objects.none()

        if state == 'all':
            qs = Employee.objects\
                .filter(
                    **request.org_salbar_filter,
                    state=Employee.STATE_WORKING,
                    user__userinfo__action_status=UserInfo.APPROVED,
                    user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                ) \
                .annotate(
                    ex_csub_org_id=F("sub_org__id"),
                )
        elif state == 'employee':
            qs = Employee.objects\
                .filter(
                    **request.org_salbar_filter,
                    state=Employee.STATE_WORKING,
                    worker_type=Employee.WORKER_TYPE_EMPLOYEE,
                    user__userinfo__action_status=UserInfo.APPROVED,
                    user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                ) \
                .annotate(
                    ex_csub_org_id=F("sub_org__id"),
                )
        elif state == 'contract':
            qs = Employee.objects\
                .filter(
                    **request.org_salbar_filter,
                    state=Employee.STATE_WORKING,
                    worker_type=Employee.WORKER_TYPE_CONTRACT,
                    user__userinfo__action_status=UserInfo.APPROVED,
                    user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                ) \
                .annotate(
                    ex_csub_org_id=F("sub_org__id"),
                )
        elif state == 'parttime':
            qs = Employee.objects\
                .filter(
                    **request.org_salbar_filter,
                    state=Employee.STATE_WORKING,
                    worker_type=Employee.WORKER_TYPE_PARTTIME,
                    user__userinfo__action_status=UserInfo.APPROVED,
                    user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                ) \
                .annotate(
                    ex_csub_org_id=F("sub_org__id"),
                )
        elif state == 'out':
            qs = Employee.objects\
                .filter(
                    **request.org_salbar_filter,
                    state=Employee.STATE_LEFT,
                    user__userinfo__action_status=UserInfo.APPROVED,
                    user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                ) \
                .annotate(
                    ex_csub_org_id=F("sub_org__id"),
                )

        qs = qs.annotate(
                gender_name=WithChoices(UserInfo.GENDER_TYPE, 'user__userinfo__gender'),
                unit1_name=F("user__userinfo__unit1__name"),
                unit2_name=F("user__userinfo__unit2__name"),
                cfirst_name=F("user__userinfo__first_name"),
                clast_name=F("user__userinfo__last_name"),
                cregister=F("user__userinfo__register"),
                cemdd_number=F("user__userinfo__emdd_number"),
                cndd_number=F("user__userinfo__ndd_number"),
                caddress=F("user__userinfo__address"),
                curgiin_ovog=F("user__userinfo__urgiin_ovog"),
                cemail=F("user__email"),
                cphone_number=F("user__phone_number"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = EmployeePaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class WorkerListAPIView(APIView):
    """ Ажилчидын жагсаалт хуудас """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/user/worker-list.html'

    @login_required()
    @has_permission(must_permissions=['work-list-read'])
    def get(self, request):

        sub_org_show = False
        sub_org_list = list()

        employees = Employee.objects.filter(**request.org_salbar_filter, state=Employee.STATE_WORKING)

        tree_data, pos = Salbars.get_tree(request)
        positions = OrgPosition.objects.filter(org=request.org_filter.get("org")).values("id", "name", "description")
        positions_director = OrgPosition\
                                .objects\
                                .filter(org=request.org_filter.get("org"), is_director=True)\
                                .values("id", "name", "description")

        # сүүлийн долоо хоногт шинээр нэмэгдсэн албан тушаал-н тоо
        week = str(datetime.datetime.now().replace(tzinfo=timezone.utc) - datetime.timedelta(days=7))
        org_position_count = Employee \
                                .objects \
                                .filter(date_joined__gte=week, **request.org_salbar_filter) \
                                .count()

        # байгуулгын бүх албан тушаалтан
        employee_pos = Employee.objects.filter(**request.exactly_org_filter, org_position__is_director=True, state=Employee.STATE_WORKING)
        serializer = EmployeeShortDataSerializer(instance=employee_pos, many=True)

        employee_count = Employee.objects.filter(**request.org_salbar_filter, state=Employee.STATE_WORKING, worker_type=Employee.WORKER_TYPE_EMPLOYEE).count()
        contract_count = Employee.objects.filter(**request.org_salbar_filter, state=Employee.STATE_WORKING, worker_type=Employee.WORKER_TYPE_CONTRACT).count()
        part_time = Employee.objects.filter(**request.org_salbar_filter, state=Employee.STATE_WORKING, worker_type=Employee.WORKER_TYPE_PARTTIME).count()

        # Хэрвээ дэд байгууллага харьяалагддаггүй байгууллагын гар бол дэд байгууллагуудаа сонгодог хэсэг харуулах
        if (request.org_filter.get("org") and not request.org_filter.get("sub_org") and not request.org_filter.get("salbar")):
            sub_org_show = True
            sub_org_list = SubOrgs.objects.filter(org=request.org_filter.get("org"))
        else:
            sub_org_list = SubOrgs.objects.filter(pk=request.org_filter.get("sub_org").id)

        return Response({
            "info": {
                "total": employees.count(),
                "new_employees": org_position_count,
                "employee": employee_count,
                "contract": contract_count,
                "parttime": part_time,
            },
            "choices": {
                "pos": pos,
                "tree_data": json.dumps(list(tree_data)),
                "positions": positions,
                "positions_director": positions_director,
                "positions_director_list": json.dumps(list(positions_director)),
                "employee_pos": json.dumps(list(serializer.data)),
            },
            "sub_org": {
                "show": sub_org_show,
                "sub_org_list": sub_org_list
            }
        })


class CommandAPIView(APIView):
    """ Тухайн pk-тай ажилтантай холбоотой тушаалын list авах нь"""
    def get(self, request, pk):
        # Хэрэглэгдсэн тушаалын id-ны list-ыг авах нь
        used_command_ids = EmployeeMigrations.objects.filter(employee_id=pk).values_list('command_id', flat=True)
        # Тухайн ажилтанд хамааралтай нийт тушаалаас хэрэглэгдсэн тушаалуудыг хассанаар
        # ажилтан нэг тушаал дээр нэг л шилжүүлэг хийх боломжтой болно.
        command = Command.objects.filter( **request.org_filter, employees__in = [str(pk)]).exclude(pk__in=used_command_ids)

        data = CommandDisplaySerializer(command, many=True).data

        return request.send_data(data)


class CommandInfoPaginationViews(APIView):

    @login_required()
    @has_permission(must_permissions=['command-read'])
    def get(self, request, pk):
        used_command_ids = EmployeeMigrations.objects.filter(employee_id=pk, command__isnull=False).values_list('command_id', flat=True)
        command = Command.objects.filter( **request.org_filter, employees__in = [pk])\
            .exclude(pk__in=used_command_ids)\
            .annotate(
                unit_name=WithChoices(Command.UNIT_CHOICES, 'unit'),
                formated_created_at=Func(
                    F('created_at'),
                    Value('YYYY-MM-DD'),
                    function='to_char',
                    output_field=CharField()
                )
            )

        paginated = data_table(command, request)
        paginated['data'] = CommandPaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class WorkerApiView(APIView):
    """ Тухайн ажилтан ямар нэг шилжилт хөдөлгөөн хийхэд log хадгалан үйлдэлийг гүйцэтгэх"""

    def is_oldPosition(self, body, employee):

        is_old_data = False
        sub_org = str(getattr(employee, 'sub_org_id'))
        salbar = str(getattr(employee, 'salbar_id'))
        org_position = str(getattr(employee, 'org_position_id'))

        if body.get("sub_org") == sub_org and body.get("salbar") == salbar and body.get("position") == org_position:
            is_old_data = True

        return is_old_data

    @login_required()
    @has_permission(must_permissions=['work-list-update'])
    def put(self, request, pk):

        if 'command_number' not in request.data:
            return request.send_warning("WRN_003")

        command =  Command.objects.filter(command_number=request.data['command_number']).first()

        if not command:
            return request.send_warning("WRN_003")
        else:
            used_ids = EmployeeMigrations.objects.filter(employee_id=pk, command__command_number=request.data['command_number'])
            if used_ids:
                return request.send_warning("WRN_002")

        request.data['command'] = command.id

        employee = Employee.objects.filter(pk=pk).first()
        if not employee:
            return request.send_error("ERR_013")

        body = request.data

        if self.is_oldPosition(body, employee):
            return request.send_warning("WRN_001")

        employee_migration_body = dict()        # Ажилтны шилжилт хөдөлгөөнийг хадгалах хувьсагч
        old_employee = copy.deepcopy(employee)  # Employee obj clone хийх нь

        if body.get("sub_org"):
            employee.sub_org_id = body.get("sub_org")
            employee_migration_body['sub_org_new'] = body.get("sub_org")
        else:
            employee.sub_org_id = None
            employee_migration_body['sub_org_new'] = None

        #  хэрвээ салбар сольж байвал дэд байгууллагын id ийг олж оноох
        if body.get("salbar"):
            employee.salbar_id = body.get("salbar")
            salbar = Salbars.objects.get(id=body.get("salbar"))
            sub_org_id = salbar.sub_orgs.id
            employee.sub_org_id = sub_org_id
            employee_migration_body['sub_org_new'] = sub_org_id
            employee_migration_body['salbar_new'] = body.get("salbar")
        else:
            employee.salbar_id = None
            employee_migration_body['salbar_new'] = None

        if body.get("position"):
            employee.org_position_id = body.get("position")
            employee_migration_body['org_position_new'] = body.get("position")

        employee.save()

        # Ажилтны албан тушаалын шилжилтийн мэдээллийг хадгалах нь
        EmployeeMigrationsSerializer.create_from_employee(employee, old_employee, request.data['command'])

        ## өөрийн датагаа засаж байвал message ийг явуулах
        if request.employee.pk == pk:
            request.send_message("success", 'INF_002')

        return request.send_info("INF_002")


class WorkerRegisterApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/user-info-register-v2.html'

    queryset = UserInfo.objects

    def get(self, request):

        units = list(Unit1Serializer(instance=Unit1.objects.all(), many=True).data)
        tree_data, pos = Salbars.get_tree(request)
        org_position_list = list(
            OrgPosition
                .objects
                .filter(
                    org=request.employee.org
                )
                .values('id', 'name')
        )

        return Response(
        {
            'units': json.dumps(units),
            'tree_data': json.dumps(list(tree_data)),
            'pos': pos,
            'org_positions': org_position_list,
            "genders": UserInfo.GENDER_TYPE,
            "blood_types": UserInfo.BLOOD_TYPE,
            "worker_type": Employee.WORKER_TYPE,
            "teacher_rank_type": Employee.TEACHER_RANK_TYPE,
            "education_level": Employee.EDUCATION_LEVEL,
            "degree_type": Employee.DEGREE_TYPE,
        })


class WorkerCreateApiView(APIView):

    queryset = UserInfo.objects

    def post(self, request):
        with transaction.atomic():

            sid = transaction.savepoint()
            errors = {}

            if not request.data.get('email'):
                del request.data['email']

            def check_field(field, value):
                if not request.data.get(field):
                    request.data[field] = value

            if request.data.get("sub_org"):
                request.data['sub_org'] = request.data['sub_org'].split("-")[0]
            else:
                request.data['sub_org'] = request.org_filter.get("sub_org").id if request.org_filter.get("sub_org") else None

            if request.data.get("unit1"):
                request.data['unit1'] = request.data['unit1'].split("-")[0]

            check_field('body_height', 0)
            check_field('body_weight', 0)
            check_field('emdd_number', None)
            check_field('hudul_number', None)
            check_field('ndd_number', None)
            check_field("home_phone", 0)
            check_field("phone_number", None)

            # Register ийн сүүлийн 8 оронг нууц үг болгох нь
            request.data['password'] = request.data['register'][-8:]
            request.data['org'] = request.org_filter.get("org").id

            # User моделийн датаг эхлэээд үүсгэнэ
            user_serializer = UserRegisterSerializer(
                data=request.data,
            )

            if not user_serializer.is_valid():
                errors.update(user_serializer.errors)
                return request.send_error_valid(errors)

            #  UserInfo үүсгэхэд хэрэгтэй датануудыг цуглуулах нь
            user = user_serializer.save()
            request.data['user'] = str(user.id)
            request.data['birthday'], request.data['gender'] = calculate_birthday(request.data['register'])
            if not request.data['birthday']:
                transaction.savepoint_rollback(sid)
                return request.send_error_valid({ "register": ["Регистерийн дугаар алдаатай байна."] })

            request.data['action_status'] = UserInfo.APPROVED
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL

            userinfo_serializer = UserInfoSerializer(
                data=request.data,
                context={ "org": request.org_filter['org']}
            )

            if not userinfo_serializer.is_valid():
                errors.update(userinfo_serializer.errors)

            if errors:
                transaction.savepoint_rollback(sid)
                return request.send_error_valid(errors)

            userinfo_serializer.save()

            count_number = CountNumber.objects.filter(name='time_register_employee').last()
            time_register_id_count = count_number.count
            request.data['time_register_employee'] = time_register_id_count


            if 'work_for_hire' in request.data:
                request.data['work_for_hire'] = True

            employee_serializer = EmployeeSerializer(data=request.data)
            if not employee_serializer.is_valid():
                transaction.savepoint_rollback(sid)
                return request.send_error_valid(employee_serializer.errors)

            employee = employee_serializer.save()

            # Ажилтны албан тушаалын шилжилтийн мэдээллийг хадгалах нь
            EmployeeMigrationsSerializer.create_from_employee(employee, None, None)

            # Ажилтнаа нэмсний дараа ажилчны тоог нэмнэ
            time_register_id_count = time_register_id_count + 1
            count_number.count = time_register_id_count
            count_number.save()

        rsp = request.send_info("INF_015")
        request.send_message('success', 'INF_015')
        return rsp


class NewWorkerOrientationApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/new-employee-orientation/index.html'

    @login_required()
    @has_permission(must_permissions=['new-employee-lesson-read'])
    def get(self, request, pk=None):
        return Response({})


class NewWorkerOrientationActionApiView(APIView):

    @login_required()
    @has_permission(must_permissions=['new-employee-lesson-create'])
    def post(self, request):

        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        request.data['created_by'] = request.user.pk

        with transaction.atomic():

            files = []

            try:
                pdfs = request.FILES.getlist("pdfs")
                remove_pdfs = request.data.getlist("remove_commands")
                pdf_ids, files = Attachments.save_attach_get_ids(request, pdfs)

                serializer = ChigluulehSerializer(data=request.data)

                serializer.is_valid(raise_exception=True)
                obj = serializer.save()

                old_att_ids = list(obj.pdfs.values_list("id", flat=True))
                obj.pdfs.set(pdf_ids + old_att_ids)

                qs = Attachments.objects.filter(id__in=remove_pdfs, org=request.org_filter.get("org"))
                Attachments.remove_obj(qs)

                return request.send_info("INF_001")
            except Exception as e:
                Attachments.remove_files(files)
                raise e


class NewWorkerOrientationActionOneApiView(APIView):
    def get(self, request, pk):
        snippet = ChigluulehHutulbur.objects.get(id=pk)
        serializer = ChigluulehSerializer(snippet)
        return request.send_data(serializer.data)

    @login_required()
    @has_permission(must_permissions=['new-employee-lesson-update'])
    def put(self, request, pk):

        with transaction.atomic():
            files = []

            try:
                pdfs = request.FILES.getlist("pdfs")
                remove_pdfs = request.data.getlist("remove_commands")
                pdf_ids, files = Attachments.save_attach_get_ids(request, pdfs)

                snippet = ChigluulehHutulbur.objects.get(id=pk)
                serializer = ChigluulehSerializer(snippet, data=request.data)
                serializer.is_valid(raise_exception=True)
                obj = serializer.save()

                old_att_ids = list(obj.pdfs.values_list("id", flat=True))
                obj.pdfs.set(pdf_ids + old_att_ids)

                qs = Attachments.objects.filter(id__in=remove_pdfs, org=request.org_filter.get("org"))
                Attachments.remove_obj(qs)
                return request.send_info("INF_002")

            except Exception as e:
                Attachments.remove_files(files)
                raise e

    @login_required()
    @has_permission(must_permissions=['new-employee-lesson-delete'])
    def delete(self, request, pk):

        try:
            snippet = ChigluulehHutulbur.objects.get(id=pk)
            Attachments.remove_obj(snippet.pdfs.all())
            snippet.delete()
            return request.send_info("INF_003")
        except Exception as e:
            raise e


class SaveChigluulehImageApiView(APIView):

    def put(self, request):
        """ Editor дээр орсон зургийг устгах """
        OtherImages.delete_images([request.data['image']])

        return Response({})

    def post(self, request):
        """ Editor дээр орсон зургийг хадгалах """
        serializer = ChigluulehImageSerializer(data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            return request.send_data(serializer.data)

        return Response({})


class NewWorkerOrientationPaginateApiView(APIView):
    @login_required()
    @has_permission(must_permissions=['new-employee-lesson-read'])
    def get(self, request, pk=None):
        """ Чиглэл дататаблэ """
        qs = ChigluulehHutulbur.objects.filter(**request.exactly_org_filter)
        paginated = data_table(qs, request)
        paginated['data'] = ChigluulehSerializer(paginated['data'], many = True).data
        return Response(paginated)


class TomiloltAPIView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/tomilolt/index.html'

    def get(self, request):

        for_tomilolt = ForTomilolt.objects.filter(**request.exactly_org_filter)
        employees = Employee.objects.filter(
            **request.exactly_org_filter,
            state=Employee.STATE_WORKING,
            user__userinfo__action_status=UserInfo.APPROVED,
            user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
        ).order_by('user__userinfo__first_name')

        return Response({
            "for_tomilolt": for_tomilolt,
            "employees": employees,
        })


class ForTomiloltAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/tomilolt/forTomlilt.html'

    def get(self, request):
        return Response()


class ForTomiloltCRApiView(APIView):

    model = ForTomilolt
    serializer = ForTomiloltCRUDSerializer

    def get_list(self, request):
        snippets = self.model.objects.filter(**request.exactly_org_filter)
        serializer = ForTomiloltSerializer(snippets, many=True)
        return serializer.data

    @login_required()
    @has_permission(allowed_permissions=['tomilolt-type-read'])
    def get(self, request, pk=None):
        if pk:
            snippet = self.model.objects.get(pk=pk)
            serializer = self.serializer(snippet)
            return request.send_data(serializer.data)

        data = self.get_list(request)
        return request.send_data(data)

    @login_required()
    @has_permission(must_permissions=['tomilolt-type-create'])
    def post(self, request):

        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        serializer = self.serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            data = self.get_list(request)
            return request.send_rsp("INF_001", data)
        return request.send_error_valid(serializer.errors)

    @login_required()
    @has_permission(must_permissions=['tomilolt-type-update'])
    def put(self, request, pk):

        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        snippet = self.model.objects.get(pk=pk)
        serializer = self.serializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = self.get_list(request)
            return request.send_rsp("INF_002", data)
        return Response(serializer.errors)

    @login_required()
    @has_permission(must_permissions=['tomilolt-type-delete'])
    def delete(self, request, pk, format=None):
        snippet = self.model.objects.get(pk=pk)
        snippet.delete()
        data = self.get_list(request)
        return request.send_rsp("INF_003", data)


class TomiloltPaginateAPIView(APIView):

    @login_required()
    @has_permission(must_permissions=['tomilolt-read'])
    def get(self, request, type, state):

        if type == 'dotood':
            if state == 'active':
                qs = Tomilolt.objects.filter(Q(start_date__lte=dateitmeGG.now()), Q(end_date__gte=dateitmeGG.now()), isForeign=False, deleted_by__isnull=True, **request.exactly_org_filter)
            if state == 'pending':
                qs = Tomilolt.objects.filter(Q(start_date__gt=dateitmeGG.now()), isForeign=False, deleted_by__isnull=True, **request.exactly_org_filter)
            if state == 'end':
                qs = Tomilolt.objects.filter(Q(end_date__lt=dateitmeGG.now()), isForeign=False, deleted_by__isnull=True, **request.exactly_org_filter)
            if state == 'deleted':
                qs = Tomilolt.objects.filter(deleted_by__isnull=False, isForeign=False, **request.exactly_org_filter)
        else:
            if state == 'active':
                qs = Tomilolt.objects.filter(Q(start_date__lte=dateitmeGG.now()), Q(end_date__gte=dateitmeGG.now()), isForeign=True, deleted_by__isnull=True, **request.exactly_org_filter)
            if state == 'pending':
                qs = Tomilolt.objects.filter(Q(start_date__gt=dateitmeGG.now()), isForeign=True, deleted_by__isnull=True, **request.exactly_org_filter)
            if state == 'end':
                qs = Tomilolt.objects.filter(Q(end_date__lt=dateitmeGG.now()), isForeign=True ,deleted_by__isnull=True, **request.exactly_org_filter)
            if state == 'deleted':
                qs = Tomilolt.objects.filter(deleted_by__isnull=False, isForeign=True, **request.exactly_org_filter)

        if 'tomilolt-all-read' not in request.permissions:
            qs = qs.filter(employees__in=[request.employee])

        paginated = data_table(qs, request)
        paginated['data'] = TomiloltPaginateSerializer(paginated['data'], many = True).data
        return Response(paginated)


class TomiloltCRUDApiView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Tomilolt.objects
    serializer_class = TomiloltSerializer

    @login_required()
    @has_permission(must_permissions=['tomilolt-read'])
    def get(self, request, pk):
        qs = Tomilolt.objects
        obj = qs.get(pk=pk)
        data = TomiloltGETSerializer(obj, many=False).data
        return request.send_data(data)

    def set_orgs_and_more(self, request):
        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id
        request.data['created_by'] = request.employee.id
        request.data['for_tomilolt'] = request.data['for_tomilolt_id']

    def get_foreigt_or_not(self, request):
        if request.data['isForeign'] == 'true':
            request.data['unit1'] = None
            request.data['unit2'] = None
            request.data['unit3'] = None
        else:
            request.data['unit1'] = request.data['unit1_id']

            if request.data['unit2_id'] == 'null':
                request.data['unit2'] = None
            else:
                request.data['unit2'] = request.data['unit2_id']

            if request.data['unit3_id'] == 'null':
                request.data['unit3'] = None
            else:
                request.data['unit3'] = request.data['unit3_id']


    def get_add_attachments(self, request, files):
        attachment_ids = list()

        for _file in request.FILES.getlist('attachments'):
            attachemnt = AttachmentSerializer(data={ "file": _file, "org": request.exactly_org_filter.get("org").id }, many=False)
            attachemnt.is_valid()
            attachemnt.save()
            files.append(attachemnt.data)
            attachment_ids.append(str(attachemnt.data.get("id")))

        return attachment_ids

    def calculate_between_days(self, request):
        start_date_time_obj = dateitmeGG.strptime(request.data['start_date'], '%Y-%m-%d')
        end_date_time_obj = dateitmeGG.strptime(request.data['end_date'], '%Y-%m-%d')
        delta = end_date_time_obj - start_date_time_obj
        if delta.days < 0:
            return request.send_error_valid({ "end_date": ["Дуусах огноо эхлэх огнооноос хойш байна."] })

        request.data['days'] = delta.days + 1

    @login_required()
    @has_permission(must_permissions=['tomilolt-create'])
    def post(self, request):
        with transaction.atomic():
            request.data._mutable = True
            error_rsp = self.calculate_between_days(request=request)
            if error_rsp:
                return error_rsp

            self.get_foreigt_or_not(request=request)
            files = []
            try:
                attachment_ids = self.get_add_attachments(request, files)
                request.data.setlist('attachments', attachment_ids)

                self.set_orgs_and_more(request=request)

                self.create(request).data
            except Exception as e:
                for _file in files:
                    zam = str(settings.BASE_DIR) + _file.get('file')
                    remove_file(zam)
                raise e
            request.data._mutable = False

        return request.send_info("INF_001")

    @login_required()
    @has_permission(must_permissions=['tomilolt-update'])
    def put(self, request, pk):
        with transaction.atomic():
            if 'isDelete' in request.data:
                if request.data['isDelete'] == True:
                    tomilolt_object = Tomilolt.objects.get(pk=pk)

                    request.data['deleted_at'] = dateitmeGG.now()
                    request.data['deleted_by'] = request.employee.pk

                    serializer = TomiloltSerializerD(instance=tomilolt_object, data=request.data)

                    if serializer.is_valid():
                        serializer.save()
                        return request.send_info("INF_007")

                    return request.send_error_valid(serializer.errors)

            else:
                request.data._mutable = True
                self.calculate_between_days(request=request)
                self.get_foreigt_or_not(request=request)

                files = []

                try:
                    remove_attachment_ids = list(json.loads(request.data.get("removed_attachments")))
                    remove_att_qs = Attachments.objects.filter(id__in=remove_attachment_ids)

                    cart = Tomilolt.objects.get(pk=pk)
                    objects = list(cart.attachments.all().values_list("id", flat=True))

                    attachment_ids = self.get_add_attachments(request, files)
                    request.data.setlist("attachments", [])

                    self.set_orgs_and_more(request=request)

                    self.update(request, pk).data

                    obj = self.queryset.get(pk=pk)
                    obj.attachments.set(attachment_ids + list(objects))

                    for obj in remove_att_qs:
                        remove_file(obj.file.path)
                        obj.delete()

                except Exception as e:
                    for _file in files:
                        zam = str(settings.BASE_DIR) + _file.get('file')
                        remove_file(zam)
                    raise e

                request.data._mutable = False
            return request.send_info("INF_002")


class DonationHTMLAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/donations/index.html'

    def get(self, request):
        employees = Employee.objects.filter(**request.exactly_org_filter)

        return Response({
            "employees": employees,
        })


class DonationList(APIView):
    @login_required()
    @has_permission(must_permissions=['donate-read'])
    def get(self, request):
        qs = EmployeeDonation.objects.filter(
            **request.exactly_org_filter,
            employee__user__userinfo__action_status=UserInfo.APPROVED,
            employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
        ) \
        .annotate(
            full_name=Concat(Upper(Substr("employee__user__userinfo__last_name", 1, 1)), Value(". "), "employee__user__userinfo__first_name"),
            ctype=WithChoices(EmployeeDonation.DONATE_TYPE, 'type')
        )
        paginated = data_table(qs, request)
        paginated['data'] = DonoationPaginateSerializer(paginated['data'], many = True).data
        return Response(paginated)

    @login_required()
    @has_permission(must_permissions=['donate-create'])
    def post(self, request):
        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        serializer = DonoationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_001")
        return request.send_error_valid(serializer.errors)


class DonationDetail(APIView):
    def get_object(self, pk, request):
        try:
            return EmployeeDonation.objects.get(pk=pk)
        except EmployeeDonation.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(must_permissions=['donate-read'])
    def get(self, request, pk):
        snippet = self.get_object(pk, request=request)
        serializer = DonoationSerializer(snippet)
        return request.send_data(serializer.data)

    @login_required()
    @has_permission(must_permissions=['donate-update'])
    def put(self, request, pk):
        snippet = self.get_object(pk, request=request)

        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        serializer = DonoationSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_002")
        return request.send_error_valid(serializer.errors)

    @login_required()
    @has_permission(must_permissions=['donate-delete'])
    def delete(self, request, pk):
        snippet = self.get_object(pk, request=request)
        snippet.delete()
        return request.send_info("INF_003")


class FindWorkerApiView(APIView):

    def get(self, request):
        """ register дугаараар ажилтан хайх """

        register = request.GET.get("register")
        exactly = request.GET.get("exactly") # 1 = яг манай байгууллагых, 0 манай болон манайхаас байгууллагаас доош

        if not exactly:
            exactly = 1

        exactly = int(exactly)

        if not register:
            raise request.send_error("ERR_013")

        filters = request.exactly_org_filter if exactly else request.org_filter

        qs = Employee \
                .objects \
                .filter(
                    Q(**filters) &
                    Q(
                        state__in=[Employee.STATE_WORKING],
                        user__userinfo__action_status=UserInfo.APPROVED,
                        user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
                    ) &
                    Q(
                        user__userinfo__first_name__icontains=register
                    ) |
                    Q(
                        user__userinfo__register__iexact=register
                    )
                ) \
                .annotate(
                    first_name=F("user__userinfo__first_name"),
                    last_name=F("user__userinfo__last_name"),
                    register=F("user__userinfo__register"),
                )

        employees = EmployeeFilterSerializer(instance=qs, many=True).data

        return request.send_data(employees)


class StaticSkillsApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
):

    queryset = StaticGroupSkills.objects
    serializer_class = StaticSkillsSerializer

    def get(self, request):
        data = self.list(request).data
        return request.send_data(data)


class  RoutingSlipApiView(APIView):

    def get(self, request, pk):
        slip = RoutingSlip.objects.filter(employee=pk, state=RoutingSlip.PENDING).first()

        return request.send_data(slip.id if slip else slip)


    def post(self, request):

        with transaction.atomic():
            sid = transaction.savepoint()
            routing_slip = dict()                   # Тойрох хуудасний дата хадгалах хувьсагч
            employee_page_body = dict()             # Тойрох хуудасны хариуцагчид
            notification_body = dict()              # Тойрох хуудастай холбоотой мэдэгдэл

            slip = RoutingSlip.objects.filter(employee=request.data['employee'], state=RoutingSlip.PENDING).first()
            # Тухайн ажилтан дээр ямар нэг тойрох хуудас олдвол тойрох хуудасыг засварлах хүсэлт байна гэж үзнэ
            if slip:
                for position in request.data['postionsList']:
                    slip_commander = RoutingSlipCommanders.objects.filter(routing_slip=slip.id, employee=position['employee']).first()
                    if slip_commander is None:

                        if position['employee'] == None or position['employee'] == '':
                            transaction.savepoint_rollback(sid)
                            return request.send_warning("WRN_004")
                        elif position['org_position'] == None or position['org_position'] == '' :
                            transaction.savepoint_rollback(sid)
                            return request.send_warning("WRN_004")

                        employee_page_body = {
                            "routing_slip": slip.id,
                            "employee": position['employee'],
                            "org_position": position['org_position']
                        }

                        employee_slip_serilaizer = RoutingSlupCommanderAllSerializer(data=employee_page_body)
                        if not employee_slip_serilaizer.is_valid():
                            return request.send_error_valid(employee_slip_serilaizer.errors)

                        employee_slip_serilaizer.save()

                for delete_id in request.data['delete']:
                    RoutingSlipCommanders.objects.filter(id=delete_id).delete()

            else:
                # Тойрох хуудас байхгүй бол шинээр тойрох хуудас үүсгэнэ.
                employee = Employee.objects.filter(id=request.data['employee']).first()

                routing_slip = {
                    "employee": employee.id,
                    "org": employee.org.id,
                    "sub_org": employee.sub_org.id if employee.sub_org else None,
                    "salbar": employee.salbar.id if employee.salbar else None,
                    "created_by": request.employee.id,
                }
                routing_slip_serilaizer = RoutringSlipSerializer(data=routing_slip)

                if not routing_slip_serilaizer.is_valid():
                    return request.send_error_valid(routing_slip_serilaizer.errors)

                routing_slip = routing_slip_serilaizer.save()

                for eachData in request.data['postionsList']:

                    if eachData['employee'] == None or eachData['employee'] == '':
                        transaction.savepoint_rollback(sid)
                        return request.send_warning("WRN_004")
                    elif eachData['org_position'] == None or eachData['org_position'] == '' :
                        transaction.savepoint_rollback(sid)
                        return request.send_warning("WRN_004")

                    employee_page_body = {
                        "routing_slip": routing_slip.id,
                        "employee": eachData['employee'],
                        "org_position": eachData['org_position']
                    }

                    commander = Employee.objects.filter(pk=eachData['employee']).first()

                    employee_slip_serilaizer = RoutingSlupCommanderAllSerializer(data=employee_page_body)

                    if not employee_slip_serilaizer.is_valid():
                        return request.send_error_valid(employee_slip_serilaizer.errors)

                    employee_slip_serilaizer.save()

                    notification_body = {
                            'title': 'Тойрох хуудас шийдвэрлэх хүсэлт ирлээ.',
                            'content': employee.full_name + ' ажилтаны тойрох хуудас' ,
                            'ntype': 'important',
                            'url': '/worker/routing-slip/?state=approve&employee=' + str(employee.id),
                            'scope_kind': Notification.SCOPE_KIND_USER,
                            'from_kind': Notification.FROM_KIND_POS,
                            'scope_ids': [ commander.user.id ]
                    }
                    Notification.objects.create_notif(request, **notification_body)

        return request.send_info("INF_001")

    def put(self ,request):
        """ Төлөв өөрчлөх || хэрэв тушаалын дугаартай байвал тухайн ажилтанг халах"""

        if 'command' in request.data:
            """ Хэрэв request data-д тушаалын дугаар байвал ажилтанг ажлаас чөлөөлөх хүсэлт гэж үзнэ."""

            # Тухайн тушаал байхгүй бол WRN буцаана.
            command = Command.objects.filter(command_number=request.data['command']).first()
            if command is None:
                return request.send_warning("WRN_006")

            # Тухайн тойрох хуудас байхгүй бол WRN буцаана.
            slip = RoutingSlip.objects.filter(employee=request.data['employee'], state=RoutingSlip.PENDING).first()
            if slip is None:
                return request.send_warning("WRN_005")

            # Тойрох хуудас бөглөсөн удирдах албан тушаалтнууд дунд төлөв нь
            # хүлээгдэж буй эсвэл цуцулагдсан төлөвтэй байгаа эсэхийг хайх
            query = Q(state=RoutingSlipCommanders.DECLINED)
            query.add(Q(state=RoutingSlipCommanders.PENDING), Q.OR)
            query.add(Q(routing_slip=slip.id), Q.AND)

            # Хэрэв тойрох хуудас цуцулах эсвэл хүлэгдэж буй төлөвтэй олдвол алдаа буцаах
            routing_slip = RoutingSlipCommanders.objects.filter(query)
            if routing_slip:
                return request.send_warning("WRN_005")

            # Тухайн хүсэлт бүх шаарлагыг хангасан гэж үзээд тухайн ажилтанг ажлаас чөлөөлөх үйлдэлийг хийнэ.
            old_employee = Employee.objects.filter(pk=request.data['employee']).first()
            EmployeeMigrationsSerializer.create_from_employee(None, old_employee, command.id)

            old_employee.state = Employee.STATE_LEFT
            old_employee.date_left = datetime.datetime.now()
            old_employee.save()

            slip.state = RoutingSlip.APPROVED
            slip.command = command
            slip.save()

        else:
            # Хэрэв тушаалын дугааргүй хүсэлт байвал тухайн хүсэлтийг тойрох хуудас бөглөж байна гэж үзээд төлөв өөрчлөх үйлдэл хийнэ.
            slip = RoutingSlip.objects.filter(pk=request.data['id'], state=RoutingSlip.PENDING)
            if slip is None:
                raise request.send_error("ERR_013")

            routing_slip = RoutingSlipCommanders.objects.filter(routing_slip=request.data['id'], employee=request.employee).first()
            if not routing_slip or 'is_approved' not in request.data:
                raise request.send_error("ERR_013")

            if request.data['is_approved']:
                routing_slip.state = RoutingSlipCommanders.APPROVED
            else:
                routing_slip.state = RoutingSlipCommanders.DECLINED

            if 'diclineDescription' in request.data:
                routing_slip.description = request.data['diclineDescription']

            routing_slip.save()

        return request.send_info("INF_001")

    def delete(self, request, pk):
        """ Тухайн тойрох хуудасыг цуцлах үйлдэл"""
        notification_body = dict()
        slip = RoutingSlip.objects.filter(employee=pk, state=RoutingSlip.PENDING).first()

        if slip:
            employee = Employee.objects.filter(pk=pk).first()

            slip.state = RoutingSlip.DECLINED
            slip.save()

            notification_body = {
                'title': 'Таны тойрох хуудас цуцлагдлаа.',
                'content': 'Таны тойрох хуудас цуцлагдлаа.',
                'ntype': 'important',
                'url': '/worker/routing-slip/?state=self&routingSlip=' + str(slip.id),
                'scope_kind': Notification.SCOPE_KIND_USER,
                'from_kind': Notification.FROM_KIND_POS,
                'scope_ids': [ employee.user.id ]
            }

            Notification.objects.create_notif(request, **notification_body)

        return request.send_info('INF_003')


class RoutingSlipPageAPIView(APIView):
    """ Ажилчидын жагсаалт хуудас """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/toiroh-huudas/routing-slip.html'

    @login_required()
    @has_permission(must_permissions=['command-read'])
    def get(self, request):

        employees = Employee.objects.filter(**request.org_filter, state=Employee.STATE_WORKING).order_by("user__userinfo__first_name")
        commanders =Employee.objects.filter(**request.exactly_org_filter, org_position__is_director=True, state=Employee.STATE_WORKING)

        return Response({
            "units": Command.UNIT_CHOICES,
            "employees": employees,
            "commanders": commanders
        })


class RoutingSlipPaginationApiView(APIView):
    """ Тухайн хэрэглэгчтэй холбоотой хойрох хуудасны мэдээлэл Pagination хүсэлт """

    @login_required()
    def get(self, request, state):
        if state == 'self':
            qs = RoutingSlip.objects.filter(employee=request.employee)
        elif state == 'approve':
            qs = RoutingSlip.objects\
                .filter(
                    routingslipcommanders__employee=request.employee,
                    state=RoutingSlip.PENDING,
                    routingslipcommanders__state=RoutingSlipCommanders.PENDING,
                    employee__user__userinfo__action_status=UserInfo.APPROVED
                    )
        elif state == 'answer':
            qs = RoutingSlip.objects\
                .filter(
                    routingslipcommanders__employee=request.employee,
                    state=RoutingSlip.PENDING,
                    employee__user__userinfo__action_status=UserInfo.APPROVED
                    )
        else:
            query = Q(state=RoutingSlipCommanders.DECLINED)
            query.add(Q(state=RoutingSlipCommanders.APPROVED), Q.OR)
            query.add(Q(routingslipcommanders__employee=request.employee), Q.AND)
            query.add(Q(employee__user__userinfo__action_status=UserInfo.APPROVED), Q.AND)
            qs = RoutingSlip.objects.filter(query)

        qs = qs.annotate(
                    org_position=F("employee__org_position__name"),
                    employee_org=F("employee__org__name"),
                    full_name=F("employee__user__userinfo__first_name"),
                    state_display=WithChoices(RoutingSlip.STATE_STATUS, 'state'),
                )

        paginated = data_table(qs, request)
        paginated['data'] = RoutingSlipPaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class RoutingSlupCommanderPaginationApiView(APIView):
    """ Тухайн тоорох хуудастай холбоотой албан тугаалтны мэдээлэл"""

    def get(self, request, pk):

        qs = RoutingSlipCommanders.objects.filter(routing_slip=pk, employee__user__userinfo__action_status=UserInfo.APPROVED)\
            .annotate(
                employee_org=F("employee__org__name"),
                org_position_name=F("employee__org_position__name"),
                state_display=WithChoices(RoutingSlip.STATE_STATUS, 'state'),
                full_name=F("employee__user__userinfo__first_name"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = RoutingSlupCommanderSerializer(paginated['data'], many=True).data

        return Response(paginated)


class RoutingSlupEmployeePaginationApiView(APIView):
    """ Тухайн тоорох хуудастай холбоотой албан тушаалын мэдээлэл"""

    def get(self, request, pk):

        slip = RoutingSlip.objects.filter(employee=pk, state=RoutingSlip.PENDING).first()

        qs = RoutingSlipCommanders.objects.filter(routing_slip=slip.id if slip else slip, employee__user__userinfo__action_status=UserInfo.APPROVED)\
            .annotate(
                employee_org=F("employee__org__name"),
                org_position_name=F("employee__org_position__name"),
                state_display=WithChoices(RoutingSlip.STATE_STATUS, 'state'),
                full_name=F("employee__user__userinfo__first_name"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = RoutingSlupCommanderSerializer(paginated['data'], many=True).data

        return Response(paginated)


class RoutingSlipListApiView(APIView):
    """ Тухайн ажилтантай холбоотой тойрох хуудасны мэдээлэл буцаах"""

    def get(self, request, pk):

        slip = RoutingSlip.objects.filter(employee=pk, state=RoutingSlip.PENDING).first()

        commanders_slip = RoutingSlipCommanders.objects.filter(routing_slip=slip.id if slip else slip)

        serializer = RoutingSlipCommandersDataSerializer(instance=commanders_slip, many=True)

        return request.send_data(serializer.data)


class RoutingSlipEmployee(APIView):
    """ Удирдах албан тушаалтнуудыг буцаах"""

    def get(self, request):

        employee = Employee.objects.filter(**request.exactly_org_filter, org_position__is_director=True, state=Employee.STATE_WORKING)
        serializer = EmployeeShortDataSerializer(instance=employee, many=True)

        org_position = OrgPosition.objects.filter(org = request.org_filter.get('org'), is_director=True).values('id')

        data = {
            "employee": serializer.data,
            "org_position" : org_position,
        }

        return request.send_data(data)


class TomiloltAttachmets(APIView):
    def get(self, request, pk):
        obj = Tomilolt.objects.get(id=pk)
        serializer = TomiloltAttachListSerializer(instance=obj)
        return request.send_data(serializer.data)


class EmployeeMigrationsApiView(APIView):
    """ Хэрэглэгчийн ажлын түүхтэй холбоотой дата авах"""
    def get(self, request, pk):

        data = None

        if pk:
            user_experience = UserExperience.objects.filter(user=pk, joined_date__isnull=False).order_by('joined_date')
            experience_serilaizer = UserExperienceSerializer(instance=user_experience, many=True)

            employees = Employee.objects.filter(user=pk).order_by("date_joined")

            serializer = EmployeeWithMigrationsSerializer(instance=employees, many=True)
            data = {
                "employee_data": serializer.data,
                "is_mobile": request.user_agent.is_mobile,
                "user_experience": experience_serilaizer.data
            }

        return request.send_data(data)


class CommandUsedEmployeeListApiView(APIView):
    """ Тухаан тушаал дээр үйлдэл хийсэн ажилчдын жагсаалт"""
    def get(self, request, pk=None):
        qs = EmployeeMigrations.objects\
            .filter(command_id=pk, employee__user__userinfo__action_status=UserInfo.APPROVED, employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL)\
            .annotate(
                employee_mood_display=WithChoices(EmployeeMigrations.EMPLOYEE_MOOD, 'employee_mood'),
                first_name = F("employee__user__userinfo__first_name"),
                last_name = F("employee__user__userinfo__last_name"),
                updated_at_info = F("updated_at")
            )

        paginated = data_table(qs, request)
        paginated['data'] = EmployeeMigrationsUsedSerializer(paginated['data'], many=True).data

        return Response(paginated)


class KhodolmoriinGereeApiView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
):
    ''' Хөдөлмөрийн гэрээ
    '''

    queryset = KhodolmoriinGeree.objects
    serializer_class = KhodolmoriinGereeSerializer

    def get_add_attachments(self, request, files):
        attachment_ids = list()

        for _file in request.FILES.getlist('attachments'):
            attachemnt = AttachmentSerializer(data={ "file": _file, "org": request.exactly_org_filter.get("org").id }, many=False)
            attachemnt.is_valid()
            attachemnt.save()
            files.append(attachemnt.data)
            attachment_ids.append(str(attachemnt.data.get("id")))

        return attachment_ids

    def post(self, request):
        with transaction.atomic():

            files = []
            try:

                attachment_ids = self.get_add_attachments(request, files)
                request.data.setlist('attachments', attachment_ids)

                self.create(request)

            except Exception as e:
                for _file in files:
                    zam = str(settings.BASE_DIR) + _file.get('file')
                    remove_file(zam)

                raise e

            return request.send_info("INF_001")

    def delete(self, request, pk=None):
        try:
            snippet = KhodolmoriinGeree.objects.get(id=pk)
            remove_file(snippet.attachments.file.path)
            snippet.delete()
            return request.send_info("INF_003")
        except Exception as e:
            raise e


class DefinitionApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/definition/index.html'

    def get(self, request, pk):

        org_qs = Orgs.objects.last()
        org_data = OrgsSerializer(org_qs, many=False).data

        employee_qs = Employee.objects.get(pk=pk)
        employee_data = EmployeeDefinitionSerializer(employee_qs, many=False).data

        return Response({
            "org": org_data,
            "employee": employee_data,
        })


class AnketApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/anket/index.html'

    @login_required()
    def get(self, request):

        sub_org_show = False
        sub_org_list = list()

        tree_data, pos = Salbars.get_tree(request)
        positions = OrgPosition.objects.filter(org=request.org_filter.get("org")).values("id", "name", "description")
        positions_director = OrgPosition\
                                .objects\
                                .filter(org=request.org_filter.get("org"), is_director=True)\
                                .values("id", "name", "description")

        # сүүлийн долоо хоногт шинээр нэмэгдсэн албан тушаал-н тоо
        week = str(datetime.datetime.now().replace(tzinfo=timezone.utc) - datetime.timedelta(days=7))
        # байгуулгын бүх албан тушаалтан
        employee_pos = Employee.objects.filter(**request.exactly_org_filter, org_position__is_director=True, state=Employee.STATE_WORKING)
        serializer = EmployeeShortDataSerializer(instance=employee_pos, many=True)

        # Хэрвээ дэд байгууллага харьяалагддаггүй байгууллагын гар бол дэд байгууллагуудаа сонгодог хэсэг харуулах
        if (request.org_filter.get("org") and not request.org_filter.get("sub_org") and not request.org_filter.get("salbar")):
            sub_org_show = True
            sub_org_list = SubOrgs.objects.filter(org=request.org_filter.get("org"))
        else:
            sub_org_list = SubOrgs.objects.filter(pk=request.org_filter.get("sub_org").id)

        return Response({
            "choices": {
                "pos": pos,
                "tree_data": json.dumps(list(tree_data)),
                "positions": positions,
                "positions_director": positions_director,
                "positions_director_list": json.dumps(list(positions_director)),
                "employee_pos": json.dumps(list(serializer.data)),
            },
            "sub_org": {
                "show": sub_org_show,
                "sub_org_list": sub_org_list
            }
        })


class AnketRegisterApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/anket-register/index.html'

    @login_required()
    def get(self, request):

        data = dict()
        anket_employee = AnketEmployee.objects.filter(employee__id=request.employee.id)

        if anket_employee.exists():
            data = AnketEmployeeSerializer(anket_employee.last(), many=False).data

        return Response({ "data": data })


class AnketRegisterActionApiView(APIView):

    @login_required()
    def post(self, request):

        request.data._mutable = True
        request.data['employee']= request.employee.id
        request.data._mutable = False

        anket_employee_qs = AnketEmployee.objects.filter(employee__id=request.employee.id)

        if anket_employee_qs:

            serializer = AnketEmployeeSerializer(instance=anket_employee_qs.last(), data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")
            else:
                return request.send_info("INF_001")

        serializer = AnketEmployeeSerializer(data=request.data)

        if not serializer.is_valid():
            raise request.send_error("ERR_023")

        serializer.save()
        return request.send_info("INF_001")


class NewEmployeeRegistrationFormApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/new-employee-registration-form/index.html'

    @login_required()
    def get(self, request):

        data = dict()
        anket_employee = NewEmployeeRegistrationForm.objects.filter(employee__id=request.employee.id)

        if anket_employee.exists():
            data = NewEmployeeRegistrationFormSerializer(anket_employee.last(), many=False).data

        return Response({ 'data': data })


class NewEmployeeRegistrationFormActionApiView(APIView):

    @login_required()
    def post(self, request):

        request.data._mutable = True
        request.data['employee']= request.employee.id
        request.data._mutable = False

        anket_employee_qs = NewEmployeeRegistrationForm.objects.filter(employee__id=request.employee.id)

        if anket_employee_qs:

            serializer = NewEmployeeRegistrationFormSerializer(instance=anket_employee_qs.last(), data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")
            else:
                return request.send_info("INF_001")

        serializer = NewEmployeeRegistrationFormSerializer(data=request.data)

        if not serializer.is_valid():
            raise request.send_error("ERR_023")

        serializer.save()
        return request.send_info("INF_001")
