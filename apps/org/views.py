from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from main.decorators import login_required
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from core.models import Orgs
from core.models import User
from core.models import UserInfo
from core.models import Employee
from core.models import OrgPosition
from core.models import CountNumber
from core.models import PropertyType
from core.models import EducationalInstitutionCategory

from .help.roles import default_roles

from .serializer import OrgsSerializer
from .serializer import OrgJsonSerializer
from .serializer import EmployeeSerializer
from .serializer import UserSaveSerializer
from .serializer import UserFirstRegisterSerializer
from .serializer import EmailOrgSerializer
from worker.serializer import EmployeeMigrationsSerializer

from main.decorators import has_permission
from main.decorators import login_required


# Create your views here.
class HomeApiView(View):
    def get(self, request):
        return HttpResponse("dsadsa")

class OrgRegisterJsonAPIView(APIView):
    @login_required()
    def get(self, request):
        ''' Энэ нь orgs jstree-гийн утгыг авах функц
        '''
        # бүх утгыг баазаас авна
        filters = {}

        if "org" in request.org_filter and not request.user.is_superuser:
            filters['id'] = request.org_filter.get("org").id

        orgsData = Orgs.objects.filter(**filters).order_by("created_at")

        serialized_data = OrgJsonSerializer(orgsData, many=True).data
        if request.user.is_superuser:
            if orgsData.count() < 1:
                serialized_data.append(
                    {
                        "text": "Шинээр үүсгэх",
                        "a_attr": {
                            "href": "/org/org-register/"
                        },
                        "icon": "fa fa-folder-plus"
                    }
                )

        # json файл буцаана
        return Response(serialized_data)


class OrgAPIView(APIView):

    ''' Хамгийн том Байгууллага crud үйлдэл
    '''
    serializer_class = OrgsSerializer
    queryset = Orgs.objects

    crud_serializer = OrgJsonSerializer

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/org/index.html'

    @login_required()
    @has_permission(must_permissions=['org-read'])
    def get(self, request, pk=None):
        if pk:
            self.queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=self.queryset, many=False)

            property_type = PropertyType.objects.all().values('name', 'id')
            educational_institution_category = EducationalInstitutionCategory.objects.all().values('name', 'id')

            return Response({ 'serializer': serializer, "pk": pk, 'user_serializer': UserFirstRegisterSerializer, 'property_type': property_type, 'educational_institution_category': educational_institution_category })
        serializer = self.serializer_class()
        return Response({ 'serializer': serializer, 'user_serializer': UserFirstRegisterSerializer })

    #post
    @login_required()
    @has_permission(allowed_permissions=['org-create', 'org-update'])
    @transaction.atomic
    def post(self, request, pk=None):
        """ шинээр үүсгэх нь:
        - ``name`` - нэр
        """

        if pk:
            instance = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=instance, data=request.data)
            if not request.data['logo']:
                request.data._mutable = True
                request.data.pop('logo')
                request.data._mutable = False

            if not request.data['todorkhoilolt_signature']:
                request.data._mutable = True
                request.data.pop('todorkhoilolt_signature')
                request.data._mutable = False

            if not request.data['todorkhoilolt_tamga']:
                request.data._mutable = True
                request.data.pop('todorkhoilolt_tamga')
                request.data._mutable = False

            if not serializer.is_valid():
                request.send_message('error', 'ERR_001')
                return Response({ 'serializer': serializer, 'pk': pk })

            try:
                request.data['logo']
                if instance.logo:
                    instance.logo.delete()
            except:
                None

            serializer.save()

        else:
            with transaction.atomic():

                sid = transaction.savepoint()       # transaction savepoint зарлах нь хэрэв алдаа гарвад roll back хийнэ
                employee_body = dict()              # Ажилтны мэдээллийг хадгалах хувьсагч
                user_body = dict()                  # Хэрэглэгчийн мэдээллийг хадгалах хувьсагч

                #Байгуулга үүгэх
                serializer = self.serializer_class(data=request.data)
                if not serializer.is_valid():
                    request.send_message('error', 'ERR_001')
                    transaction.savepoint_rollback(sid)
                    return Response({ 'serializer': serializer, 'data': request.data , 'user_serializer': UserFirstRegisterSerializer })

                org = serializer.save()

                # Байгуулгын хүний нөөцийн ажилтан эрх
                for role_info in default_roles:
                    org_position = self.serializer_class.create_defualt_role(role_info['name'], role_info['description'], role_info['permissions'], org.id)
                    if org_position is False:
                        transaction.savepoint_rollback(sid)
                        request.send_message('error', 'ERR_004')

                user_body = {
                    'password': request.data['phone_number'],
                    'email': request.data['email'],
                    'phone_number': request.data['phone_number'],
                    'mail_verified': True,
                }

                #Байгуулгын хүний нөөцийн ажилтаны account үүсгэх
                user_serializer = UserSaveSerializer(data=user_body)
                if not user_serializer.is_valid():
                    request.send_message('error', 'ERR_012')
                    user_serializer = UserFirstRegisterSerializer(data=request.data)
                    user_serializer.is_valid()
                    transaction.savepoint_rollback(sid)
                    return Response({ 'serializer': serializer, 'data': request.data, 'user_serializer': user_serializer})

                user = user_serializer.save()

                #  хоосон userinfo үүсгэх
                if user:
                    UserInfo.objects.create(user=user, first_name=user.email, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)

                # Шинээр үүссэн байгуулгат хэрэглэгчийн ажилтны мэдээллийг үүсгэх
                org_position = OrgPosition.objects.filter(org_id=org.id, is_hr=True).values('id').first()

                count_number = CountNumber.objects.filter(name='time_register_employee').last()
                time_register_id_count = count_number.count

                employee_body = {
                    'org_position': org_position['id'],
                    'org': org.id,
                    'user': user.id,
                    'time_register_employee': time_register_id_count
                }

                employee_serializer = EmployeeSerializer(data=employee_body)

                if not employee_serializer.is_valid():
                    request.send_message('error', 'ERR_012')
                    user_serializer = UserFirstRegisterSerializer(data=request.data)
                    user_serializer.is_valid()
                    transaction.savepoint_rollback(sid)
                    return Response({ 'serializer': serializer, 'data': request.data, 'user_serializer': user_serializer})

                employee = employee_serializer.save()

                # Ажилтны албан тушаалын шилжилтийн мэдээллийг хадгалах нь
                EmployeeMigrationsSerializer.create_from_employee(employee, None, None)

                # Ажилтнаа нэмсний дараа ажилчны тоог нэмнэ
                time_register_id_count = time_register_id_count + 1
                count_number.count = time_register_id_count
                count_number.save()


        request.send_message('success', 'INF_015')
        return redirect('org-register')


class OrgDelete(
    APIView
):

    @login_required()
    @has_permission(must_permissions=['org-delete'])
    def get(self, request, pk):
        Orgs.objects.filter(pk=pk).delete()
        request.send_message("success", 'INF_003')
        return redirect("org-register")


class SuperUserChangeOrg(APIView):

    @login_required()
    @has_permission(must_permissions=['salbar-delete'])
    def get(self, request, pk):

        if request.user.is_superuser:
            Employee.objects.update_or_create(
                user=request.user,
                defaults={
                    'org_id': pk,
                    'sub_org': None,
                    "salbar": None
                }
            )

        request.send_message("success", 'INF_002')
        return redirect("org-register")


class UserRegisterOrg(APIView):

    @login_required()
    @has_permission(allowed_permissions=['org-update'])
    @transaction.atomic
    def post(self, request, pk):

        if request.user.is_superuser:
            sid = transaction.savepoint()       # transaction savepoint зарлах нь хэрэв алдаа гарвад roll back хийнэ
            employee_body = dict()              # Ажилтны мэдээллийг хадгалах хувьсагч
            user_body = dict()                  # Хэрэглэгчийн мэдээллийг хадгалах хувьсагч

            user = User.objects.filter(email=request.data['email']).first()
            if user:
                raise request.send_error("ERR_002", "и-мэйл")

            # Байгуулгын хүний нөөцийн ажилтан эрх
            org_position = OrgPosition.objects.filter(org_id=pk, is_hr=True).values('id').first()

            #Хэрэглэгч үүсгэх
            user_body = {
                'password': request.data['phone_number'],
                'email': request.data['email'],
                'phone_number': request.data['phone_number'],
                'mail_verified': True,
            }
            user_serializer = UserSaveSerializer(data=user_body)

            if not user_serializer.is_valid():
                transaction.savepoint_rollback(sid)
                raise request.send_error("ERR_001")

            user = user_serializer.save()

            #  хоосон userinfo үүсгэх
            if user:
                UserInfo.objects.create(user=user, first_name=user.email, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)

            count_number = CountNumber.objects.filter(name='time_register_employee').last()
            time_register_id_count = count_number.count

            # Шинээр үүссэн байгуулгат хэрэглэгчийн ажилтны мэдээллийг үүсгэх
            employee_body = {
                'org_position': org_position['id'],
                'org': pk,
                'user': user.id,
                'time_register_employee': time_register_id_count,
            }

            employee_serializer = EmployeeSerializer(data=employee_body)

            if not employee_serializer.is_valid():
                transaction.savepoint_rollback(sid)
                raise request.send_error("ERR_001")

            employee = employee_serializer.save()

            # Ажилтны албан тушаалын шилжилтийн мэдээллийг хадгалах нь
            EmployeeMigrationsSerializer.create_from_employee(employee, None, None)

            # Ажилтнаа нэмсний дараа ажилчны тоог нэмнэ
            time_register_id_count = time_register_id_count + 1
            count_number.count = time_register_id_count
            count_number.save()

        return  request.send_info("INF_001")


class OrgSystemEmailApiView(APIView):

    serializer_class = EmailOrgSerializer
    queryset = Orgs.objects

    def post(self, request, pk=None):

        request.data._mutable = True
        request.data["email_use_tls"] = request.data.get("email_use_tls") == "on"
        request.data._mutable = False

        if pk:

            instance = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=instance, data=request.data)
            if not serializer.is_valid():
                request.send_message('error', 'ERR_001')
                return redirect("org-register", pk=pk)

            serializer.save()
            return redirect("org-register", pk=pk)

        else:
            request.send_message('error', 'ERR_022')
            return redirect("org-register")
