import json
import datetime
import re
import requests

import pandas as pd

from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from django.db.models import F
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from rest_framework import mixins
from rest_framework import generics
from rest_framework import exceptions

from core.models import Feedback, RequestTimeVacationRegister, SkillDefWithUser, StaticShagnal, UserProgress, WorkJoinRequests, UserToken
from core.models import User, UserTalent
from core.models import Unit1
from core.models import Unit2
from core.models import Salbars
from core.models import SubOrgs
from core.models import Employee
from core.models import UserInfo
from core.models import UserReward
from core.models import OrgPosition
from core.models import UserContactInfoRequests
from core.models import Orgs
from core.models import UserEducation, UserEmergencyCall, UserFamilyMember, UserHamaatan
from core.models import ExtraSkillsDefinations, UserEducationDoctor, UserEducationInfo, UserErdmiinTsol, UserLanguage, UserOfficeKnowledge, UserProfessionInfo, UserProgrammKnowledge, UserWorkExperience
from core.models import UserExperience
from core.models import AccessHistory
from core.models import ShagnalEmployee
from core.models import BankInfo
from core.models import UserBookMarkPages
from core.models import MainMedicalExamination
from core.models import AdditiveMedicalExamination
from core.models import InspectionType
from core.models import InspectionMedicalExamination
from core.models import KhodolmoriinGeree
from core.models import StudentLogin

from main.utils.mail_html.resetPasswordMail import resetPasswordMail
from main.utils.mail_html.verifyMail import verifyMail

from .serializer import NormalRegiseterSerializer, UserAllInfoSerializer, UserCholooSerializer, UserInfoSerializer2, UserSanalHvseltSerializer, UserTokenSerializer
from .serializer import NormalRegisterMailVerifierSerializer
from .serializer import UserEducationSerializer
from .serializer import UserProfileImageSerializer
from .serializer import UserSerializer
from .serializer import UserTalentSerializer
from .serializer import Unit1Serializer
from .serializer import UserInfoSerializer
from .serializer import UserRewardSerializer
from .serializer import UserCreateSerializer
from .serializer import UserRegisterSerializer
from .serializer import UserExtraInfoSerializer
from .serializer import UserContactInfoSerializer
from .serializer import UserGeneralInfoSerializer
from .serializer import UserInfoRegisterSerializer
from .serializer import UserChangeContactInfoSerializer
from .serializer import UserExtraInfoPaginationSerializer
from .serializer import UserContactInfoPagniationSerializer
from .serializer import UserGeneralInfoPaginationSerializer
from .serializer import UserFamilyMemberSerializer
from .serializer import UserHamaatanSerializer
from .serializer import UserEmergencyCallSerializer
from .serializer import UserProfessionInfoSerializer
from .serializer import UserWorkExperienceSerializer
from .serializer import UserErdmiinTsolSerializer
from .serializer import UserLanguageSerializer
from .serializer import UserOfficeKnowledgeSerializer
from .serializer import UserProgrammKnowledgeSerializer
from .serializer import ExtraSkillsDefinationsSerializer
from .serializer import UserExperienceSerializer
from .serializer import UserShagnalSerializer
from .serializer import AccessHistorySerializer
from .serializer import UserShagnalGETSerializer
from .serializer import MainMedicalExaminationSerializer
from .serializer import AdditiveMedicalExaminationSerializer
from .serializer import InspectionTypeSerializer
from .serializer import InspectionMedicalExaminationSerializer

from main.decorators import login_required
from main.utils.register import calculate_birthday
from main.utils.datatable import data_table
from main.decorators import has_permission
from main.utils.encrypt import decrypt, encrypt
from main.utils.user_percent import CalcUserPercent


class RegisterApiView(APIView):
    """ Хэрэглэгч системд бүртгүүлэх хэсэг
    """
    def post(self, request):
        ''' User шинээр үүсгэх
        ------
        ``is_SSO - str`` :
        ``gender - str`` : Хүйс
        ``email - str`` : И-мэйл
        ``password - str`` : нууц үг
        ``is_staff - str`` : Ажилтан эсэх
        ``first_name - str`` : Хэрэглэгчийн нэр
        ``last_name - str`` : Хэрэглэгчийн овог
        ``register - str`` : Регистерийн дугаар
        ``is_super_user - boolean`` : SuperUser мөн эсэх

        '''
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Нууц үг таарахгүй байна')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return request.send_info("INF_001")


class LoginApiView(APIView):
    """ Хэрэглэгч системд нэвтрэх хэсэг
    """
    serializer_class = UserSerializer
    queryset = User.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'sign-in.html'

    def get(self, request, pk=None):

        return Response(
        {
            'serializer': self.serializer_class,
            "email": request.COOKIES.get("remember") or ""
        })

    def post(self, request):
        ''' User системд нэвтрэх
        ------
        ``email - str`` : Хэрэглэгчийн нэр
        ``password - str`` : нууц үг
        '''
        access_history_body = dict()    #Хандалтын түүхүүд хадгалах хувьсагч

        email = request.data['email']
        password = request.data['cpassword']
        remember = request.data.get('remember')

        # Оюутан оюутны кодоор хайж байгаа бол
        pattern = "^\S+@\S+\.\S+$"
        check_email_format = re.search(pattern, email)
        if not check_email_format:
            student_login = StudentLogin.objects.filter(student__code=email).last()

            if student_login:
                student_pass_check = check_password(password, student_login.password)

                if student_pass_check:
                    url = settings.STUDENT_LOGIN_API
                    res = requests.post(url=url, data={ 'username': email, 'password': password })
                    if res.status_code == 200:
                        request.send_message('success', 'INF_011')
                        return redirect('home')

        user = authenticate(email=email.strip(), password=password)
        if user is not None:
            login(request, user)
            access_history_body = {
                "user": user.id,
                "device": str(request.user_agent),
                "state": AccessHistory.LOGIN,
                "location": request.META.get('REMOTE_ADDR', None),
                "is_mobile": request.user_agent.is_mobile
            }

            access_history_serilaizer = AccessHistorySerializer(data=access_history_body)
            if not access_history_serilaizer.is_valid():
                return request.send_error_valid(access_history_serilaizer.errors)

            access_history_serilaizer.save()

            request.send_message('success', 'INF_011')
            response = redirect('home')
            if remember:
                response.set_cookie('remember', email)
            else:
                response.delete_cookie('remember')
            return response

        request.send_message('error', 'ERR_007')
        return redirect('account-user-login')


class LogoutApiView(APIView):

    # @login_required()
    def get(self, request):
        access_history_body = dict()    #Хандалтын түүхүүд хадгалах хувьсагч
        user_id = request.user.id
        logout(request)

        access_history_body = {
            "user": user_id,
            "device": str(request.user_agent),
            "state": AccessHistory.LOGOUT,
            "location": request.META.get('REMOTE_ADDR', None),
            "is_mobile": request.user_agent.is_mobile
        }

        access_history_serilaizer = AccessHistorySerializer(data=access_history_body)
        if not access_history_serilaizer.is_valid():
            return request.send_error_valid(access_history_serilaizer.errors)

        access_history_serilaizer.save()
        response = Response()

        response = redirect('account-user-login')
        response.delete_cookie("pageList")
        request.send_message('success', 'INF_014')
        return response


class UserRewardApiView(APIView):

    def get(self, request, pk=None):

        user_id = pk if pk else request.user.pk

        snippets = ShagnalEmployee \
                .objects \
                .filter(
                    user_id=user_id, kind=ShagnalEmployee.KIND_STATIC
                ).values()
        return Response(snippets)

    def post(self, request, pk=None):
        request.data['user'] = pk if pk else request.user.pk
        request.data['kind'] = ShagnalEmployee.KIND_STATIC

        serializer = UserShagnalGETSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_001")
        return request.send_error_valid(serializer.errors)


class UserRewardApiViewDetail(APIView):

    def get_object(self, pk, request):

        try:
            return ShagnalEmployee.objects.get(pk=pk)
        except UserReward.DoesNotExist:
            raise request.send_error("ERR_003")

    def get(self, request, pk):

        snippet = self.get_object(pk, request)
        serializer = UserShagnalGETSerializer(snippet)
        return request.send_data(serializer.data)

    def put(self, request, pk):

        snippet = self.get_object(pk, request)
        request.data['kind'] = ShagnalEmployee.KIND_STATIC
        serializer = UserShagnalGETSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_002")

        return request.send_error_valid(serializer.errors)

    def delete(self, request, pk, format = None):

        snippet = self.get_object(pk, request)
        snippet.delete()
        return request.send_info("INF_003")


class UserRewardPaginationApiView(APIView):

    def get(self, request, pk=None):
        user_id = pk if pk else request.user.pk
        qs = ShagnalEmployee \
                .objects \
                .filter(
                    user_id=user_id, kind=ShagnalEmployee.KIND_STATIC
                ) \
                .annotate(
                    name=F("static_shagnal__name")
                )
        paginated = data_table(qs, request)
        paginated['data'] = UserShagnalSerializer(paginated['data'], many = True).data
        return Response(paginated)


class UserInfoApiView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    serializer_class = UserInfoSerializer
    queryset = UserInfo.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/user/user-info-register.html'

    @login_required()
    @has_permission(must_permissions = ['employee-read'])
    def get(self, request, pk=None):

        if pk:
            return Response(
            {
                'serializer': self.serializer_class,
                'data': queryset
            })

        queryset = self.queryset.all()
        unit2_list = list(Unit2.objects.all().values('id', 'name', parents_id=F('unit1_id')))
        sub_org_list = list(SubOrgs.objects.filter(org_id=request.employee.org.id).values('id', 'name', parents_id=F('org_id')))
        salbars_list = list(Salbars.objects.filter(org_id=request.employee.org.id).values('id', 'name', parents_id=F('sub_orgs_id')))
        org_position_list = list(OrgPosition.objects.filter(org_id=request.employee.org.id).values('id', 'name'))
        return Response(
        {
            'user_serializer' : UserRegisterSerializer,
            'serializer': self.serializer_class,
            'data': queryset,
            'unit2_data': json.dumps(unit2_list),
            'salbars_data': json.dumps(salbars_list),
            'subOrg_data': json.dumps(sub_org_list),
            'orgPosition_data': json.dumps(org_position_list)
        })

    # post
    @login_required()
    @transaction.atomic
    @has_permission(allowed_permissions=['employee-read', 'employee-update'])
    def post(self, request, pk=None):
        """ шинээр үүсгэх нь:
        - ``name`` - Нэр
        """
        with transaction.atomic():
            sid = transaction.savepoint()
            request.data._mutable = True
            request.data['password'] = request.data['register'][-8:]
            request.data._mutable = False
            user_serializer = UserCreateSerializer(data = request.data, context={ "org": request.org_filter['org']})
            valid = user_serializer.is_valid()
            if not valid:
                user_serializer =UserRegisterSerializer(data = request.data, context={ "org": request.org_filter['org']})
                serializer =UserInfoSerializer(data = request.data, context={ "org": request.org_filter['org']})
                user_serializer.is_valid()
                serializer.is_valid()
                return Response({ 'user_serializer': user_serializer, 'data': request.data, 'serializer': serializer})
            user = user_serializer.save()
            request.data._mutable = True
            request.data['user'] = str(user.id)
            request.data['birthday'], request.data['gender'] = calculate_birthday(request.data['register'])
            if not request.data['birthday']:
                transaction.savepoint_rollback(sid)
                request.send_message('error', 'ERR_014')
            request.data['action_status'] = UserInfo.APPROVED
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            request.data._mutable = False
            self.serializer_class = UserInfoRegisterSerializer
            if pk:
                instance = self.queryset.get(pk=pk)
                serializer = self.serializer_class(instance=instance, data=request.data)
                if not serializer.is_valid():
                    return Response({ 'serializer': serializer, 'pk': pk })
            else:
                serializer = self.serializer_class(data=request.data)
                if not serializer.is_valid():
                    user_serializer =UserRegisterSerializer(data = request.data, context={ "org": request.org_filter['org']})
                    serializer =UserInfoSerializer(data = request.data, context={ "org": request.org_filter['org']})
                    user_serializer.is_valid()
                    serializer.is_valid()
                    return Response({ 'user_serializer': user_serializer, 'data': request.data, 'serializer': serializer })

            serializer.save()
            request.send_message('success', 'INF_001')
            return redirect('home')

    # delete
    @login_required()
    @has_permission(must_permissions=['employee-delete'])
    def delete(self, request, pk=None):
        """устгах үйлдэл
        """
        self.destroy(request, pk)
        queryset = self.queryset.all()
        return Response(
        {
            'serializer': self.serializer_class,
            'data': queryset
        })


class WorkerPageApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/index.html'
    @login_required()
    def get(self, request, pk=None, format=None):

        empoyee = Employee.objects.filter(user_id=request.user.pk, state__in=[Employee.STATE_FIRED, Employee.STATE_LEFT]).first()
        skill_choices = SkillDefWithUser.LEVEL_CHOICES
        genders = UserInfo.GENDER_TYPE
        shagnals = StaticShagnal.objects.all().order_by("order")
        bank_info = BankInfo.objects.all().order_by("order")
        p_percent = CalcUserPercent.display_progress_percent(user=request.user)
        suuts_choices = UserInfo.SUUTS_TYPE

        return Response({
            "empoyee_qs": empoyee,
            'skill_choices': json.dumps(skill_choices),
            "genders": genders,
            "shagnals": shagnals,
            "p_percent": p_percent,
            "bank_info": bank_info,
            'suuts_choices': suuts_choices
        })


class WorkerPageUpdateApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/hrUpdateProfile/index.html'

    def get(self, request, pk, format=None):
        empolee = Employee.objects.get(id=pk)
        userinfo = UserInfo.objects.get(user_id=empolee.user.id, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
        genders = UserInfo.GENDER_TYPE
        shagnals = StaticShagnal.objects.all().order_by("order")
        p_percent = CalcUserPercent.display_progress_percent(user=empolee.user)
        bank_info = BankInfo.objects.all().order_by("order")
        khodolmoriin_geree = KhodolmoriinGeree.objects.filter(employee=pk).order_by('-created_at')
        suuts_choices = UserInfo.SUUTS_TYPE

        return Response({
            'empolee': empolee,
            'selected_user_data': empolee.user,
            'selected_userinfo_data': userinfo,
            "genders": genders,
            "shagnals": shagnals,
            "p_percent": p_percent,
            "bank_info": bank_info,
            "khodolmoriin_geree": khodolmoriin_geree,
            'suuts_choices': suuts_choices,
            "worker_type": Employee.WORKER_TYPE,
            "teacher_rank_type": Employee.TEACHER_RANK_TYPE,
            "education_level": Employee.EDUCATION_LEVEL,
            "degree_type": Employee.DEGREE_TYPE,
        })


class UserGeneralInfoViews(APIView):
    def get(self, request, format=None):
        snippets = UserInfo.objects.filter(user=request.user.pk)
        serializer = UserGeneralInfoSerializer(snippets, many=True)

        return request.send_data(serializer.data)

    def post(self, request, pk=None):
        request.data['user'] = request.user.pk
        request.data['birthday'], request.data['gender'] = calculate_birthday(request.data['register'])

        if "org" in request.org_filter:
            if request.org_filter['org'] != None:
                request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        if request.data['birthday'] == None:
            return request.send_error_valid({ "register": ["Регистерийн дугаар алдаатай байна."] })
        # Хүний нөөц, админ эсвэл ажилгүй хүн бол
        if request.user.is_employee == False or request.employee.is_hr:
            userinfo = UserInfo.objects.filter(user_id=request.user.pk, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL).first()
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            request.data['action_status'] = UserInfo.APPROVED
            serializer = UserGeneralInfoSerializer(instance=userinfo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)

        else:
            serializer = UserGeneralInfoSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)


class UserGeneralInfoOneViews(APIView):
    def get_object(self, pk, request):
        try:
            return UserInfo.objects.get(pk=pk)
        except UserInfo.DoesNotExist:
            raise request.send_error("ERR_003")

    def put(self, request, pk, format=None):

        request.data['user'] = request.user.pk

        request.data['birthday'], request.data['gender'] = calculate_birthday(request.data['register'])
        if request.data['birthday'] == None:
            return request.send_error_valid({ "register": ["Регистерийн дугаар алдаатай байна."] })

        if "org" in request.org_filter:
            if request.org_filter['org'] != None:
                request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        # Хүний нөөц, админ эсвэл ажилгүй хүн бол
        if request.user.is_employee == False or request.employee.is_hr:
            userInfo = UserInfo.objects.filter(user_id=request.user.pk, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL).first()
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            request.data['action_status'] = UserInfo.APPROVED
            serializer = UserGeneralInfoSerializer(instance=userInfo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)

        else:
            request.data['action_status'] = UserInfo.PENDING

            snippet = self.get_object(pk, request)
            serializer = UserGeneralInfoSerializer(snippet, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_002")

            return request.send_error_valid(serializer.errors)


class ApproveUserGeneralInfoViews(APIView):
    def get_object(self, pk, action_status, action_status_type, request):
        try:
            return UserInfo.objects.get(user=pk, action_status=action_status, action_status_type=action_status_type)
        except UserInfo.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(must_permissions=['userinfo-request-action'])
    def put(self, request, pk=None, format=None):
        # Мэдээлэл солихийг зөвшөөрөх
        current_request = UserInfo.objects.get(id=request.data['id'])
        if request.data['action_status'] == UserInfo.APPROVED:
            # Өмнөх зөвшөөрөгдсөн мэдээллийг олох гэж оролдох
            try:
                snippet = UserInfo.objects.get(user=request.data['user'], action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
                request.data['gender'] = current_request.gender
                serializer = UserGeneralInfoSerializer(instance=snippet, data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    # Хүсэлтийн зөвшөөрч байгаа учир.. Өмнөх зөвшөөрөгдсөн мэдээллийг шинэчлэж хүсэлтийг нь устгана
                    UserInfo.objects.get(id=request.data['id']).delete()
                    return request.send_info("INF_015")

                return request.send_error_valid(serializer.errors)

            # Өмнөх зөвшөөрөгдсөн мэдээлэл байхгүй бол шинээр үүсгэх
            except UserInfo.DoesNotExist:
                request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
                request.data['gender'] = current_request.gender
                serializer = UserGeneralInfoSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    UserInfo.objects.get(id=request.data['id']).delete()
                    return request.send_info("INF_015")

                return request.send_error_valid(serializer.errors)

        # Татгалзсан бол action status ийг татгалзсан болгоно
        elif request.data['action_status'] == UserInfo.DECLINED:
            request.data['gender'] = current_request.gender
            serializer = UserGeneralInfoSerializer(instance=current_request, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_015")

            return request.send_error_valid(serializer.errors)


class GeneralInfoChangeRequest(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/generalInfoReq/index.html'

    def get(self, request):
        return Response({})


class UserExtraInfoUnits(
    generics.GenericAPIView,
    mixins.ListModelMixin,
):
    serializer_class = Unit1Serializer
    queryset = Unit1.objects

    def get(self, request):
        '''
        Unit ийн жагсаалтыг TREE хэлбэрээр буцаах
        '''
        orderedDictData = self.list(request).data

        return request.send_data(orderedDictData)


class UserExtraInfoViews(APIView):
    def get(self, request, format=None):
        snippets = UserInfo.objects.filter(user=request.user.pk).order_by("-created_at")
        serializer = UserExtraInfoSerializer(snippets, many=True)

        return request.send_data(serializer.data)

    def post(self, request, pk=None):

        request.data['user'] = request.user.pk
        request.data['action_status'] = UserInfo.PENDING
        request.data['unit1'] = request.data['unit1_id']
        request.data['unit2'] = request.data['unit2_id']
        request.data['blood_type'] = None if not request.data['blood_type'] else request.data['blood_type']

        if "org" in request.org_filter:
            if request.org_filter['org'] != None:
                request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        # Хүний нөөц, админ эсвэл ажилгүй хүн бол
        if request.user.is_employee == False or request.employee.is_hr:
            userinfo = UserInfo.objects.filter(user_id=request.user.pk, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL).first()
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            request.data['action_status'] = UserInfo.APPROVED
            serializer = UserExtraInfoSerializer(instance=userinfo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)

        else:
            serializer = UserExtraInfoSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)


class UserExtraInfoOneViews(APIView):
    def get_object(self, pk, request):
        try:
            return UserInfo.objects.get(pk=pk)
        except UserInfo.DoesNotExist:
            raise request.send_error("ERR_003")

    def put(self, request, pk, format=None):
        request.data['user'] = request.user.pk
        request.data['action_status'] = UserInfo.PENDING
        request.data['unit1'] = request.data['unit1_id']
        request.data['unit2'] = request.data['unit2_id']

        if "org" in request.org_filter:
            if request.org_filter['org'] != None:
                request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        # Хүний нөөц, админ эсвэл ажилгүй хүн бол
        if request.user.is_employee == False or request.employee.is_hr:
            userinfo = UserInfo.objects.filter(user_id=request.user.pk, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL).first()
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            request.data['action_status'] = UserInfo.APPROVED
            serializer = UserExtraInfoSerializer(instance=userinfo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)
        else:
            snippet = self.get_object(pk, request)
            serializer = UserExtraInfoSerializer(snippet, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_002")

            return request.send_error_valid(serializer.errors)


class UserExtraInfoPaginationViews(APIView):

    def get(self, request):
        qs = UserInfo.objects.filter(**request.exactly_org_filter, action_status=UserInfo.PENDING, action_status_type=UserInfo.ACTION_TYPE_EXTRA)

        paginated = data_table(qs, request)
        paginated['data'] = UserExtraInfoPaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class UserGeneralInfoPaginationViews(APIView):

    def get(self, request):
        qs = UserInfo.objects.filter(**request.exactly_org_filter, action_status=UserInfo.PENDING, action_status_type=UserInfo.ACTION_TYPE_GENERAL)

        paginated = data_table(qs, request)
        paginated['data'] = UserGeneralInfoPaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class ApproveUserExtraInfoViews(APIView):
    def get_object(self, pk, action_status, action_status_type, request):
        try:
            return UserInfo.objects.get(user=pk, action_status=action_status, action_status_type=action_status_type)
        except UserInfo.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(must_permissions=['userinfo-request-action'])
    def put(self, request, pk=None, format=None):
        # Мэдээлэл солихийг зөвшөөрөх
        current_reqeust = UserInfo.objects.get(id=request.data['id'])

        blood_type_name = request.data['blood_type_name']
        for blood_id, blood_name in UserInfo.BLOOD_TYPE:
            if blood_type_name == blood_name:
                request.data['blood_type'] = blood_id

        if request.data['action_status'] == UserInfo.APPROVED:
            # Өмнөх зөвшөөрөгдсөн мэдээллийг олох гэж оролдох
            try:
                snippet = UserInfo.objects.get(user=request.data['user'], action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
                request.data['birthday'] = snippet.birthday
                request.data['register'] = snippet.register
                request.data['unit1'] = current_reqeust.unit1_id
                request.data['unit2'] = current_reqeust.unit2_id

                serializer = UserExtraInfoSerializer(instance=snippet, data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    # Хүсэлтийн зөвшөөрч байгаа учир.. Өмнөх зөвшөөрөгдсөн мэдээллийг шинэчлэж хүсэлтийг нь устгана
                    UserInfo.objects.get(id=request.data['id']).delete()
                    return request.send_info("INF_015")

                return request.send_error_valid(serializer.errors)

            # Өмнөх зөвшөөрөгдсөн мэдээлэл байхгүй бол шинээр үүсгэх
            except UserInfo.DoesNotExist:
                raise request.send_error("ERR_015")

        # Татгалзсан бол action status ийг татгалзсан болгоно
        elif request.data['action_status'] == UserInfo.DECLINED:
            request.data['unit1'] = current_reqeust.unit1_id
            request.data['unit2'] = current_reqeust.unit2_id
            serializer = UserExtraInfoSerializer(instance=current_reqeust, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_015")

            return request.send_error_valid(serializer.errors)


class UserContactInfoViews(APIView):
    def get(self, request, format=None):
        snippets = UserContactInfoRequests.objects.filter(user=request.user.pk)
        serializer = UserContactInfoSerializer(snippets, many=True)

        return request.send_data(serializer.data)

    def check_email_already_taken(self, request):
        try:
            exist = User.objects.get(email=request.data.get('email'))
            if request.user.email == exist.email:
                return False
            return True
        except:
            return None

    def post(self, request, pk=None):
        if self.check_email_already_taken(request) == True:
            return request.send_error_valid({'email': ["Имэйл хаяг бүртгэлтэй байна."]})

        request.data['user'] = request.user.pk
        request.data['action_status'] = UserContactInfoRequests.PENDING

        if "org" in request.org_filter:
            if request.org_filter['org'] != None:
                request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        # Хүний нөөц, админ эсвэл ажилгүй хүн бол
        if request.user.is_employee == False or request.employee.is_hr == False:
            userinfo = User.objects.get(pk=request.user.pk)
            serializer = UserChangeContactInfoSerializer(instance=userinfo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)

        else:
            serializer = UserContactInfoSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)


class UserContactInfoOneViews(APIView):
    def get_object(self, pk, request):
        try:
            return UserContactInfoRequests.objects.get(pk=pk)
        except UserContactInfoRequests.DoesNotExist:
            raise request.send_error("ERR_003")

    def check_email_already_taken(self, request):
        try:
            exist = User.objects.get(email=request.data.get('email'))
            if request.user.email == exist.email:
                return False
            return True
        except:
            return False

    def put(self, request, pk, format=None):
        if self.check_email_already_taken(request) == True:
            return request.send_error_valid({'email': ["Имэйл хаяг бүртгэлтэй байна."]})

        request.data['user'] = request.user.pk
        request.data['action_status'] = UserContactInfoRequests.PENDING
        snippet = self.get_object(pk, request)

        if "org" in request.org_filter:
            if request.org_filter['org'] != None:
                request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        # Хүний нөөц, админ эсвэл ажилгүй хүн бол
        if request.user.is_employee == False or request.employee.is_hr == False:
            userinfo = User.objects.get(pk=pk)
            serializer = UserChangeContactInfoSerializer(instance=userinfo, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)

        else:
            serializer = UserContactInfoSerializer(snippet, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_002")

            return request.send_error_valid(serializer.errors)


class UserContactInfoPaginationViews(APIView):

    def get(self, request):
        qs = UserContactInfoRequests.objects.filter(**request.exactly_org_filter, action_status=UserContactInfoRequests.PENDING)

        paginated = data_table(qs, request)
        paginated['data'] = UserContactInfoPagniationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class ApproveUserContactInfoViews(APIView):
    def get_object(self, pk, request):
        try:
            return UserContactInfoRequests.objects.get(pk=pk)
        except UserContactInfoRequests.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(must_permissions=['userinfo-request-action'])
    def put(self, request, pk=None, format=None):
        # Мэдээлэл солихийг зөвшөөрөх
        if request.data['action_status'] == UserContactInfoRequests.APPROVED:
            # Өмнөх зөвшөөрөгдсөн мэдээллийг олох гэж оролдох
            try:
                snippet = User.objects.get(id=request.data['user_id'])
                serializer = UserChangeContactInfoSerializer(instance=snippet, data=request.data)

                # Хүсэлтийн зөвшөөрч байгаа учир.. Өмнөх зөвшөөрөгдсөн мэдээллийг шинэчлэж хүсэлтийг нь устгана
                if serializer.is_valid():
                    serializer.save()
                    UserContactInfoRequests.objects.get(id=request.data['id']).delete()
                    return request.send_info("INF_015")

                return request.send_error_valid(serializer.errors)

            # Өмнөх зөвшөөрөгдсөн мэдээлэл байхгүй бол
            except User.DoesNotExist:
                raise request.send_error("ERR_013")

        # Татгалзсан бол action status ийг татгалзсан болгоно
        elif request.data['action_status'] == UserContactInfoRequests.DECLINED:
            snippet = self.get_object(pk=request.data['id'], request=request)
            serializer = UserContactInfoSerializer(instance=snippet, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_015")

            return request.send_error_valid(serializer.errors)


class UserContactInfoHrApiView(APIView):
    def put(self, request, pk):
        try:

            if not request.data.get('email'):
                request.data['email'] = None

            snippet = User.objects.get(id=pk)
            serializer = UserChangeContactInfoSerializer(instance=snippet, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_015")

            return request.send_error_valid(serializer.errors)

        # Өмнөх зөвшөөрөгдсөн мэдээлэл байхгүй бол
        except User.DoesNotExist:
            raise request.send_error("ERR_013")


class UserGeneralInfoHrApiViews(APIView):
    def put(self, request, pk):
        try:
            qs = UserInfo.objects.get(user_id=pk, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
        except:
            return None
        if qs:
            request.data['birthday'], request.data['gender'] = calculate_birthday(request.data['register'])

            if request.data['birthday'] == None:
                return request.send_error_valid({ "register": ["Регистерийн дугаар алдаатай байна."] })

            request.data['user'] = pk
            request.data['user_id'] = pk
            request.data['action_status'] = UserInfo.APPROVED
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            serializer = UserGeneralInfoSerializer(instance=qs, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_015")

            return request.send_error_valid(serializer.errors)
        else:
            request.data['birthday'], request.data['gender'] = calculate_birthday(request.data['register'])

            if request.data['birthday'] == None:
                return request.send_error_valid({ "register": ["Регистерийн дугаар алдаатай байна."] })

            request.data['user'] = pk
            request.data['user_id'] = pk
            request.data['action_status'] = UserInfo.APPROVED
            request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
            serializer = UserGeneralInfoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_015")

            return request.send_error_valid(serializer.errors)


class UserExtraInfoHrApiViews(APIView):
    def put(self, request, pk):
        try:
            qs = UserInfo.objects.get(user_id=pk, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
        except:
            raise request.send_error("ERR_015")
        request.data['birthday'] = qs.birthday
        request.data['user'] = pk
        request.data['user_id'] = pk
        request.data['unit1'] = request.data['unit1_id']
        request.data['unit2'] = request.data['unit2_id']
        request.data['action_status'] = UserInfo.APPROVED
        request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
        request.data['blood_type'] = None if not request.data['blood_type'] else request.data['blood_type']

        serializer = UserExtraInfoSerializer(instance=qs, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_015")

        return request.send_error_valid(serializer.errors)


class ResetPasswordApiView(APIView):

    def put(self, request):
        ''' Хэрэглэгч нууц үгээ солих
        ------
        ``email - str`` : Хэрэглэгчийн нэр
        ``password - str`` : нууц үг
        '''
        # Хуучин нууц үг
        old_password = request.data['oldPassword']
        # Шинэ нууц үг
        password = request.data['password']
        # Шинэ давтах нууц үг
        password_confirm = request.data['confirm']

        # Шинээр оруулсан нууц үг таарахгүй бол
        if password != password_confirm:
            return request.send_error_valid({ "confirm": ["Шинээр оруулж байгаа нууц үг ижил байх ёстой."] })

        # Хуучин нууц үг таарахгүй байвал алдаа буцаана
        if check_password(old_password, request.user.password) is False:
            return request.send_error_valid({ "errNm1": ["Хуучин нууц үг буруу байна."] })

        request.user.set_password(password)
        request.user.save()

        login(request, request.user)

        return request.send_info("INF_015")


class UserProfileImageApiView(APIView):

    @login_required()
    def put(self, request, pk=None):
        ''' Хэрэглэгч нүүр зургаа солих'''

        with transaction.atomic():
            if pk:
                # Хүний нөөцийн хүн шууд солих
                user_obj = User.objects.get(pk=pk)
                real_photo = user_obj.real_photo
                request.data['email'] = user_obj.email
                serializer = UserProfileImageSerializer(instance=user_obj, data=request.data)

                serializer.is_valid(raise_exception=True)
                try:
                    if real_photo:
                        real_photo.delete()
                except:
                    pass
                serializer.save()
                return request.send_info("INF_002")

            else:
                user_obj = User.objects.get(pk=request.user.pk)
                real_photo = user_obj.real_photo
                request.data['email'] = request.user.email
                serializer = UserProfileImageSerializer(instance=user_obj, data=request.data)

                serializer.is_valid(raise_exception=True)
                try:
                    if real_photo:
                        real_photo.delete()
                except:
                    pass
                serializer.save()
                return request.send_info("INF_002")


class UserTalentApiView(APIView):
    def get_object(self, pk, request):
        try:
            return UserTalent.objects.get(pk = pk)
        except UserTalent.DoesNotExist:
            raise request.send_error("ERR_003")

    def post(self, request, pk=None):
        request.data['user'] = pk if pk else request.user.pk

        serializer = UserTalentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_001")
        return request.send_error_valid(serializer.errors)

    def get(self, request, pk=None):
        snippet = self.get_object(pk, request)
        serializer = UserTalentSerializer(snippet)
        return request.send_data(serializer.data)

    def put(self, request, pk=None):
        snippet = self.get_object(pk, request)

        serializer = UserTalentSerializer(snippet, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_002")
        return request.send_error_valid(serializer.errors)

    def delete(self, request, pk=None):
        snippet = self.get_object(pk, request)
        snippet.delete()
        return request.send_info("INF_003")


class UserTalentPaginationApiView(APIView):

    def get(self, request, pk=None):
        qs = UserTalent.objects.filter(user_id=pk if pk else request.user.pk)
        paginated = data_table(qs, request)
        paginated['data'] = UserTalentSerializer(paginated['data'], many = True).data
        return Response(paginated)


class NormalRegisterPageApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'sign-up.html'
    def get(self, request):
        return Response({})


class NormalRegisterApiView(APIView):
    def post(self, request, format=None):
        with transaction.atomic():

            unverified_user = User.objects.filter(email=request.data['email'], mail_verified=False).first()

            # Өмнөн баталгаажуулах мэйл илгээгдсэн гэхдээ бүртгэл баталгаажаагүй байвал дахин хэрэглэгч үүсгэхгүй гээр
            # баталгаажуулах мэйл дахин илгээж байна
            if unverified_user:
                encrypted_mail =  encrypt(request.data['email'])

                send_mail(
                    subject='Майлээ баталгаажуулах!',
                    message="",
                    from_email=request.data['email'],
                    recipient_list=[request.data['email']],
                    html_message=verifyMail(encrypted_mail, request.data['last_name'], request.data['first_name'], request.build_absolute_uri('/')[:-1])
                )
                return request.send_info("INF_008")

            serializer = NormalRegiseterSerializer(data=request.data, context={ "request": request })
            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_008")
            return request.send_error_valid(serializer.errors)


class ErrorVerifyMail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/verifyMail/tokenmissing.html'
    def get(self, request):
        return Response({})


class ResendVerifyMail(APIView):
    def post(self, request):
        """Баталгаажуулах мэйл дахин илгээх"""
        encrypted_mail =  encrypt(request.data['email'])

        send_mail(
            subject='Майлээ баталгаажуулах!',
            message="",
            from_email=request.data['email'],
            recipient_list=[request.data['email']],
            html_message=verifyMail(encrypted_mail, request.data['last_name'], request.data['first_name'], request.build_absolute_uri('/')[:-1])
        )
        return request.send_info("INF_008")


class NormalRegisterVerifyMail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'sign-in.html'

    def get(self, request, format=None):
        encrypted_mail = request.GET.get('token', 'token missing')

        if encrypted_mail == 'token missing':
            return redirect('token-error')

        try:
            decrypted_mail = decrypt(encrypted_mail)
        except:
            return redirect('token-error')

        if not decrypted_mail:
            return redirect('token-error')

        user_obj = User.objects.get(email=decrypted_mail)

        if not user_obj:
            return redirect('token-error')

        request.data['mail_verified'] = True

        serializer = NormalRegisterMailVerifierSerializer(instance=user_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            request.send_message('success', 'INF_012')
            return redirect('account-user-login')
        return redirect('token-error')


def happyBrithdaySendMail():

    now_time = datetime.datetime.now()

    # Өдөр болон сар
    day = now_time.day
    month = now_time.month

    hunii_nootsuud = Employee.objects.filter(org_position__is_hr=True)
    for hunii_noots in hunii_nootsuud:

        employee_filter = dict()
        if hunii_noots.org:
            employee_filter['org'] = hunii_noots.org
        if hunii_noots.sub_org:
            employee_filter['sub_org'] = hunii_noots.sub_org
        if hunii_noots.salbar:
            employee_filter['salbar'] = hunii_noots.salbar

        birthdays = Employee.objects.filter(
            **employee_filter,
            user__userinfo__birthday__day=day,
            user__userinfo__birthday__month=month,
            state=Employee.STATE_WORKING
        ).values('user__userinfo__first_name', 'user__userinfo__last_name')

        # Байхгүй бол дараачийн компаниас хайна
        if not birthdays:
            continue

        # Төрсөн хүн байвал бүх нэрүүдийг нийлүүлнэ
        all_employees_names = ''
        for birthday in birthdays:

            if birthday == list(birthdays)[-1]:
                full_name = birthday['user__userinfo__last_name'] + ' овогтой ' + birthday['user__userinfo__first_name']
                all_employees_names = all_employees_names + full_name
                break

            full_name = birthday['user__userinfo__last_name'] + ' овогтой ' + birthday['user__userinfo__first_name'] + ' , '
            all_employees_names = all_employees_names + full_name

        # # Тухайн компанийн хүний нөөцүүдийг олж майл илгээнэ
        # hunii_noots = Employee.objects.filter(
        #     org_position__is_hr=True,
        #     org=org.id,
        #     state=Employee.STATE_WORKING
        # ).values_list('user__email', flat=True)

        hunii_noots_email = hunii_noots.user.email if hunii_noots.user.email else ''

        send_mail(
            subject='Төрсөн өдрийн мэдэгдэл.',
            message="",
            from_email='mnhrsystem@gmail.com',
            recipient_list=[hunii_noots_email],
            html_message=f'{all_employees_names} ажилчдын төрсөн өдөр тохиож байна.'
        )

    # # Бүх байгууллагуудаар давтана
    # orgs = Orgs.objects.all()

    # for org in orgs:

    #     # Тэрхүү байгууллагын бүх ажилчдаас нь өнөөдөр төрсөн хүн байна уу гэдгийг хайна
    #     birthdays = Employee.objects.filter(
    #         user__userinfo__birthday__day=day,
    #         user__userinfo__birthday__month=month,
    #         org=org.id,
    #         state=Employee.STATE_WORKING
    #     ).values('user__userinfo__first_name', 'user__userinfo__last_name')

    #     # Байхгүй бол дараачийн компаниас хайна
    #     if not birthdays:
    #         continue

    #     # Төрсөн хүн байвал бүх нэрүүдийг нийлүүлнэ
    #     all_employees_names = ''
    #     for birthday in birthdays:

    #         if birthday == list(birthdays)[-1]:
    #             full_name = birthday['user__userinfo__last_name'] + ' овогтой ' + birthday['user__userinfo__first_name']
    #             all_employees_names = all_employees_names + full_name
    #             break

    #         full_name = birthday['user__userinfo__last_name'] + ' овогтой ' + birthday['user__userinfo__first_name'] + ' , '
    #         all_employees_names = all_employees_names + full_name

    #     # Тухайн компанийн хүний нөөцүүдийг олж майл илгээнэ
    #     hunii_noots = Employee.objects.filter(
    #         org_position__is_hr=True,
    #         org=org.id,
    #         state=Employee.STATE_WORKING
    #     ).values_list('user__email', flat=True)

    #     send_mail(
    #         subject='Төрсөн өдрийн мэдэгдэл.',
    #         message="",
    #         from_email='mnhrsystem@gmail.com',
    #         recipient_list=list(hunii_noots),
    #         html_message=f'{all_employees_names} ажилчдын төрсөн өдөр тохиож байна.'
    #     )


class UserAnketApiView(APIView):

    @login_required()
    def get(self, request):
        user = request.user
        family = UserFamilyMemberSerializer(instance=UserFamilyMember.objects.filter(user=user), many=True).data
        family2 = UserHamaatanSerializer(instance=UserHamaatan.objects.filter(user=user), many=True).data
        numbers = UserEmergencyCallSerializer(instance=UserEmergencyCall.objects.filter(user=user), many=True).data
        user_education = UserEducation.objects.filter(user=user).first()
        education1 = []
        education2 = []
        edu = dict()
        if user_education:
            education1 = UserEducationInfo.objects.filter(user_education=user_education).annotate(cid=F("id")).values()
            education2 = UserEducationDoctor.objects.filter(user_education=user_education).annotate(cid=F("id")).values()
            edu['bachelor_sedew'] = user_education.bachelor_sedew
            edu['dr_sedew'] = user_education.dr_sedew

        mergeshil1 = UserProfessionInfoSerializer(instance=UserProfessionInfo.objects.filter(user=user), many=True).data
        mergeshil2 = UserWorkExperienceSerializer(instance=UserWorkExperience.objects.filter(user=user), many=True).data
        mergeshil3 = UserErdmiinTsolSerializer(instance=UserErdmiinTsol.objects.filter(user=user), many=True).data
        extra_skills = ExtraSkillsDefinationsSerializer(instance=ExtraSkillsDefinations.objects.filter(user=user), many=True).data
        languages = UserLanguageSerializer(instance=UserLanguage.objects.filter(user=user), many=True).data
        pc_chadwar = UserProgrammKnowledgeSerializer(instance=UserProgrammKnowledge.objects.filter(user=user), many=True).data
        experience = UserExperienceSerializer(instance=UserExperience.objects.filter(user=user), many=True).data
        data = {
            "family": family,
            "family2": family2,
            "numbers": numbers,
            "education1": education1,
            "education2": education2,
            "mergeshil1": mergeshil1,
            "mergeshil2": mergeshil2,
            "mergeshil3": mergeshil3,
            "extra-skills": extra_skills,
            "languages": languages,
            "pc-chadwar": pc_chadwar,
            "experience": experience,
        }

        skills = SkillDefWithUser.objects.filter(user=user).values("id", 'skill_def', 'level')
        office = UserOfficeKnowledge.objects.filter(user=user).values().first()
        return_data = {
            "repeater": data,
        }
        real_body = dict()
        real_body.update({ "skills": skills if skills else [] })
        real_body.update(edu)
        if office:
            real_body.update(office)

        return_data.update(real_body)
        return request.send_data(return_data)

    @login_required()
    def post(self, request):
        repeators = request.data.get("repeatorsVal")
        body = request.data.get("realBody")
        with transaction.atomic():

            ur_chadwar = dict()
            for key in body.keys():
                if key.startswith("skill-"):
                    id = key.replace("skill-", '')
                    ur_chadwar[id] = body[key]

            for key_id in ur_chadwar:
                obj, created = SkillDefWithUser \
                    .objects \
                    .update_or_create(
                        skill_def_id=key_id,
                        user=request.user,
                        defaults={
                            "level": int(ur_chadwar[key_id])
                        }
                    )

            family = repeators.get("family")
            if family:
                for family_item in family:
                    if not family_item.get("birthday"):
                        family_item['birthday'] = None
                user_family_serializer = UserFamilyMemberSerializer(data=family, many=True, context={ "request": request })
                if user_family_serializer.is_valid(raise_exception=True):
                    user_family_serializer.save()

            family2 = repeators.get("family2")
            if family2:
                for family_item in family2:
                    if not family_item.get("birthday"):
                        family_item['birthday'] = None
                user_hamaatan_serializer = UserHamaatanSerializer(data=family2, many=True, context={ "request": request })
                if user_hamaatan_serializer.is_valid(raise_exception=True):
                    user_hamaatan_serializer.save()

            numbers = repeators.get("numbers")
            if numbers:
                user_emergency_serializer = UserEmergencyCallSerializer(data=numbers, many=True, context={ "request": request })
                if user_emergency_serializer.is_valid(raise_exception=True):
                    user_emergency_serializer.save()

            education1 = repeators.get("education1")
            education2 = repeators.get("education2")
            for family_item in education1:
                if not family_item.get("start_date"):
                    family_item['start_date'] = None
                if not family_item.get("end_date"):
                    family_item['end_date'] = None
            for family_item in education2:
                if not family_item.get("start_date"):
                    family_item['start_date'] = None
                if not family_item.get("end_date"):
                    family_item['end_date'] = None
            education_serializer = UserEducationSerializer(
                data=body,
                many=False,
                context={
                    "usereducationinfo": education1,
                    "usereducationdoctor": education2,
                    'request': request,
                }
            )
            if education_serializer.is_valid(raise_exception=True):
                education_serializer.save()

            mergeshil1 = repeators.get("mergeshil1")
            if mergeshil1:
                for family_item in mergeshil1:
                    if not family_item.get("start_date"):
                        family_item['start_date'] = None
                    if not family_item.get("end_date"):
                        family_item['end_date'] = None
                    if not family_item.get("learned_days"):
                        family_item['learned_days'] = 0
                mergeshil1_serializer = UserProfessionInfoSerializer(data=mergeshil1, many=True, context={ "request": request })
                if mergeshil1_serializer.is_valid(raise_exception=True):
                    mergeshil1_serializer.save()

            mergeshil2 = repeators.get("mergeshil2")
            if mergeshil2:
                mergeshil2_serializer = UserWorkExperienceSerializer(data=mergeshil2, many=True, context={ "request": request })
                if mergeshil2_serializer.is_valid(raise_exception=True):
                    mergeshil2_serializer.save()

            mergeshil3 = repeators.get("mergeshil3")
            if mergeshil3:
                for family_item in mergeshil3:
                    if not family_item.get("give_date"):
                        family_item['give_date'] = None
                mergeshil3_serializer = UserErdmiinTsolSerializer(data=mergeshil3, many=True, context={ "request": request })
                if mergeshil3_serializer.is_valid(raise_exception=True):
                    mergeshil3_serializer.save()

            extra_skills = repeators.get("extra-skills")
            if extra_skills:
                extra_skills_serializer = ExtraSkillsDefinationsSerializer(data=extra_skills, many=True, context={ "request": request })
                if extra_skills_serializer.is_valid(raise_exception=True):
                    extra_skills_serializer.save()

            languages = repeators.get("languages")
            if languages:
                languages_serializer = UserLanguageSerializer(data=languages, many=True, context={ "request": request })
                if languages_serializer.is_valid(raise_exception=True):
                    languages_serializer.save()

            pc_chadwar = repeators.get("pc-chadwar")
            if pc_chadwar:
                pc_chadwar_serializer = UserProgrammKnowledgeSerializer(data=pc_chadwar, many=True, context={ "request": request })
                if pc_chadwar_serializer.is_valid(raise_exception=True):
                    pc_chadwar_serializer.save()

            office_know_serializer = UserOfficeKnowledgeSerializer(data=body, many=False, context={ "request": request })
            if office_know_serializer.is_valid(raise_exception=True):
                office_know_serializer.save()

            experience = repeators.get("experience")
            if experience:
                for family_item in experience:
                    if not family_item.get("joined_date"):
                        family_item['joined_date'] = None
                    if not family_item.get("left_date"):
                        family_item['left_date'] = None
                experience_serializer = UserExperienceSerializer(data=experience, many=True, context={ "request": request })
                if experience_serializer.is_valid(raise_exception=True):
                    experience_serializer.save()

        return request.send_info("INF_015")

    @login_required()
    def delete(self, request, pk, modeltype):
        Model = {
            "family": UserFamilyMember,
            "family2": UserHamaatan,
            "numbers": UserEmergencyCall,
            "education1": UserEducationInfo,
            "education2": UserEducationDoctor,
            "mergeshil1": UserProfessionInfo,
            "mergeshil2": UserWorkExperience,
            "mergeshil3": UserErdmiinTsol,
            "extra-skills": ExtraSkillsDefinations,
            "languages": UserLanguage,
            "pc_chadwar": UserProgrammKnowledge,
            "experience": UserExperience,
        }.get(modeltype)
        if not Model:
            raise request.send_error("ERR_013")

        rows, datas = Model.objects.filter(pk=pk).delete()
        if rows == 0:
            raise request.send_error("ERR_013")

        return request.send_info("INF_003")


class HRAnketApiView(APIView):

    @login_required()
    def get(self, request):

        token = request.GET.get('token')
        userId = request.GET.get("userId")
        if token and token != 'null':
            join_request_id = decrypt(token)
            join_request = WorkJoinRequests.objects.filter(id=join_request_id).first()
            if not join_request:
                raise request.send_error("ERR_003")
            user = User.objects.filter(id=join_request.user.id).first()
        else:
            user = User.objects.filter(id=userId).first()
            if not user:
                raise request.send_error("ERR_003")

        family = UserFamilyMemberSerializer(instance=UserFamilyMember.objects.filter(user=user), many=True).data
        family2 = UserHamaatanSerializer(instance=UserHamaatan.objects.filter(user=user), many=True).data
        numbers = UserEmergencyCallSerializer(instance=UserEmergencyCall.objects.filter(user=user), many=True).data
        user_education = UserEducation.objects.filter(user=user).first()
        education1 = []
        education2 = []
        edu = dict()
        if user_education:
            education1 = UserEducationInfo.objects.filter(user_education=user_education).annotate(cid=F("id")).values()
            education2 = UserEducationDoctor.objects.filter(user_education=user_education).annotate(cid=F("id")).values()
            edu['bachelor_sedew'] = user_education.bachelor_sedew
            edu['dr_sedew'] = user_education.dr_sedew

        mergeshil1 = UserProfessionInfoSerializer(instance=UserProfessionInfo.objects.filter(user=user), many=True).data
        mergeshil2 = UserWorkExperienceSerializer(instance=UserWorkExperience.objects.filter(user=user), many=True).data
        mergeshil3 = UserErdmiinTsolSerializer(instance=UserErdmiinTsol.objects.filter(user=user), many=True).data
        extra_skills = ExtraSkillsDefinationsSerializer(instance=ExtraSkillsDefinations.objects.filter(user=user), many=True).data
        languages = UserLanguageSerializer(instance=UserLanguage.objects.filter(user=user), many=True).data
        pc_chadwar = UserProgrammKnowledgeSerializer(instance=UserProgrammKnowledge.objects.filter(user=user), many=True).data
        experience = UserExperienceSerializer(instance=UserExperience.objects.filter(user=user), many=True).data
        data = {
            "family": family,
            "family2": family2,
            "numbers": numbers,
            "education1": education1,
            "education2": education2,
            "mergeshil1": mergeshil1,
            "mergeshil2": mergeshil2,
            "mergeshil3": mergeshil3,
            "extra-skills": extra_skills,
            "languages": languages,
            "pc-chadwar": pc_chadwar,
            "experience": experience,
        }

        skills = SkillDefWithUser.objects.filter(user=user).values("id", 'skill_def', 'level')
        office = UserOfficeKnowledge.objects.filter(user=user).values().first()
        return_data = {
            "repeater": data,
        }
        real_body = dict()
        real_body.update({ "skills": skills if skills else [] })
        real_body.update(edu)
        if office:
            real_body.update(office)

        return_data.update(real_body)
        user_info_serializer = UserInfoSerializer2(instance=user.info).data
        userInfoGG = UserAllInfoSerializer(instance=user).data
        return request.send_data({"return_data": return_data, "userInfo": user_info_serializer, "user": userInfoGG})


class ForgotPassordApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/forgot-password/forgot-password.html'
    def get(self, request):
        return Response({})


class ForgotPasswordSendMailApiView(APIView):
    def post(self, request):
        user_obj = User.objects.filter(email=request.data['email']).first()

        if not user_obj:
            return request.send_info("INF_017")

        encrypted_mail = encrypt(user_obj)

        fiftheen_minuts = datetime.datetime.now() + datetime.timedelta(minutes=15)

        token_serializer = UserTokenSerializer(data={"token": encrypted_mail, "expire_date": fiftheen_minuts, "user": user_obj.id})
        if token_serializer.is_valid():
            token_serializer.save()
        else:
            raise request.send_error("ERR_019")

        send_mail(
            subject='Нууц үг солих',
            message="",
            from_email=user_obj,
            recipient_list=[user_obj],
            html_message=resetPasswordMail(user_obj.info.last_name, user_obj.info.first_name, encrypted_mail, request.build_absolute_uri('/')[:-1])
        )

        return request.send_info("INF_017")


class ForgotPassordHTMLApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/forgot-password/forgot-password-pass.html'
    def get(self, request):
        token = request.GET.get('token', 'token missing')
        token_gg = UserToken.objects.filter(token=token).first()

        if not token_gg:
            return redirect('token-error')

        if token == 'token missing':
            return redirect('token-error')

        try:
            decrypted_mail = decrypt(token)
        except:
            return redirect('token-error')

        if not decrypted_mail:
            return redirect('token-error')

        user_obj = User.objects.get(email=decrypted_mail)

        if not token_gg.expire_date > datetime.datetime.now():
            return redirect('token-error')

        if not user_obj:
            return redirect('token-error')

        return Response({ "email": decrypted_mail, "token": token })


class ForgotPassordChangePasswordApiView(APIView):
    def post(self, request):
        user_obj = User.objects.get(email=request.data['email'])
        password = request.data['password']

        token = request.GET.get('token', 'token missing')
        token_gg = UserToken.objects.filter(token=token).first()

        if not token_gg:
            return redirect('token-error')

        if token == 'token missing':
            return redirect('token-error')

        if not token_gg.expire_date > datetime.datetime.now():
            return redirect('token-error')

        user_obj.set_password(password)
        user_obj.save()
        request.send_message("success", "INF_015")
        return request.send_info("INF_015")


class UserCholooPaginateApiView(APIView):
    def get(self, request, pk):
        emp_obj = Employee.objects.filter(user_id=pk, **request.org_filter).order_by('date_joined').last()
        qs = RequestTimeVacationRegister.objects.filter(employee=emp_obj)
        paginated = data_table(qs, request)
        paginated['data'] = UserCholooSerializer(paginated['data'], many = True).data
        return Response(paginated)


class UserSanalHvseltApiView(APIView):
    def get(self, request, pk):
        emp_obj = Employee.objects.filter(user_id=pk, **request.org_filter).order_by('date_joined').last()
        qs = Feedback.objects.filter(from_employee=emp_obj)
        paginated = data_table(qs, request)
        paginated['data'] = UserSanalHvseltSerializer(paginated['data'], many = True).data
        return Response(paginated)


class AccessHistoryApiView(APIView):
    """ Нэвтэрсэн хэрэглэгчийн хандалтын түүхийг харах"""
    @login_required()
    def get(self, request):

        data = None
        acces_history = AccessHistory.objects.filter(user=request.user.id).order_by('-created_at')
        serializer = AccessHistorySerializer(acces_history, many=True)
        data = serializer.data

        return request.send_data(data)


class UserMedicalApiView(generics.GenericAPIView):
    """ Хэрэглэгчийн эрүүл мэндийн мэдээлэл
    """

    serializer_class = MainMedicalExaminationSerializer
    queryset = MainMedicalExamination.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/user/medical.html'

    @login_required()
    def get(self, request, pk=None):

        search_user_id = request.user.id
        full_name = ''
        hunii_noots = False
        pkStatic = ""

        # user Id=тай байвал тэрний утгыг харуулна
        if pk:
            check_user = User.objects.filter(id=pk).last()
            # Тийм ID-тай user байхгүй бол шууд өөр лүүн буцаана
            if not check_user:
                return redirect('medical')
            search_user_id = pk
            full_name = check_user.info.last_name + ' ' + check_user.info.first_name
            hunii_noots = True
            pkStatic = pk

        # Баазаас хайгаад сүүлийн утгуудыг буцаана
        main_datas = MainMedicalExamination.objects.filter(user=search_user_id).last()
        additive_datas = AdditiveMedicalExamination.objects.filter(user=search_user_id).last()

        inspectionValues = dict()

        # Эрүүл мэндийн үзлэгийн хуудасын сүүлийн утгуудыг буцаана
        for inspectionType in InspectionType.objects.all():
            code = inspectionType.code
            value = InspectionMedicalExamination.objects.filter(
                user=search_user_id,
                inspectionType=code
            ).values('inspectionText').last()

            inspectionValues[code] = value

        return Response({
            'main_datas': main_datas,
            'additive_datas': additive_datas,
            'inspectionValues': inspectionValues,
            'full_name': full_name,
            'hunii_noots': hunii_noots,
            'pkStatic': pkStatic
        })


class UserMedicalMainAjaxApiView(APIView):
    ''' Бие бялдарын үндсэн үзүүлэлт нэмэх үйлдэл
    '''
    @login_required()
    def post(self, request):

        obj = MainMedicalExamination.objects.create(
            user=request.user,
            **request.data,
        )
        serializer = MainMedicalExaminationSerializer(obj)

        return request.send_rsp("INF_015", serializer.data)


class UserMedicalMainJsonApiView(generics.GenericAPIView):
    ''' Бие бялдарын үндсэн үзүүлэлт datatable утга
    '''
    @login_required()
    def get(self, request):

        user_id = request.user.id

        if request.GET.get('userid'):
            user_id = request.GET.get('userid')

        qs = MainMedicalExamination.objects.filter(user=user_id).order_by("a_date")
        paginated = data_table(qs, request)
        paginated['data'] = MainMedicalExaminationSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class UserMedicalAdditiveAjaxApiView(APIView):
    ''' Бие бялдарын нэмэлт үзүүлэлт нэмэх үйлдэл
    '''
    @login_required()
    def post(self, request):

        obj = AdditiveMedicalExamination.objects.create(
            user=request.user,
            **request.data,
        )
        serializer = AdditiveMedicalExaminationSerializer(obj)

        return request.send_rsp("INF_015", serializer.data)


class UserMedicalAdditiveJsonApiView(generics.GenericAPIView):
    ''' Бие бялдарын нэмэлт үзүүлэлт datatable утга
    '''
    @login_required()
    def get(self, request):

        user_id = request.user.id

        if request.GET.get('userid'):
            user_id = request.GET.get('userid')

        qs = AdditiveMedicalExamination.objects.filter(user=user_id).order_by("b_date")
        paginated = data_table(qs, request)
        paginated['data'] = AdditiveMedicalExaminationSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class UserMedicalInpectionAjaxApiView(APIView):
    ''' Эрүүл мэндийн үзлэгийн хуудас нэмэх үйлдэл
    '''
    @login_required()
    def post(self, request):

        code = request.data.get('code')
        text = request.data.get('text')

        inspectionTypeId = InspectionType.objects.filter(code=code).last()

        obj = InspectionMedicalExamination.objects.create(
            user=request.user,
            inspectionType=inspectionTypeId,
            inspectionText=text
        )
        serializer = InspectionMedicalExaminationSerializer(obj)

        return request.send_rsp("INF_015", serializer.data)


class UserMedicalInpectionJsonApiView(generics.GenericAPIView):
    ''' Эрүүл мэндийн үзлэгийн хуудас datatable утга
    '''
    @login_required()
    def get(self, request):

        type_code = request.GET.get('inspectionType')

        user_id = request.user.id

        if request.GET.get('userid'):
            user_id = request.GET.get('userid')

        qs = InspectionMedicalExamination.objects.filter(user=user_id, inspectionType__code=type_code).order_by("created_at")
        paginated = data_table(qs, request)
        paginated['data'] = InspectionMedicalExaminationSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class PageBookmarksApiView(APIView):

    @login_required()
    def post(self, request):

        page = request.data.get('page')
        if not page:
            raise request.send_error("ERR_013")

        bookmark_qs = UserBookMarkPages.objects.filter(user=request.user)
        ## шинээр үүсгэж байгаа үе
        if not bookmark_qs.exists():
            bookmark_qs.create(
                user=request.user,
                pages=[page]
            )
        ##  хуучин байсан бол шинэ датаг нэмэх нь
        else:
            bookmark = bookmark_qs.first()
            if len(bookmark.pages) >= 5:
                return request.send_warning("WRN_010", [], 5)

            if page not in bookmark.pages:
                bookmark.pages.append(page)
                bookmark.save()

        return request.send_info("INF_015")

    @login_required()
    def delete(self, request):

        page = request.GET.get('page')
        if not page:
            raise request.send_error("ERR_013")
        bookmark_qs = UserBookMarkPages.objects.filter(user=request.user)
        if bookmark_qs.exists():
            bookmark = bookmark_qs.first()
            if page in bookmark.pages:
                bookmark.pages.remove(page)
                bookmark.save()

        return request.send_info("INF_015")


class UserEmployeeSalaryEditApiView(APIView):
    ''' Ажилчны мэдээлэл засах
    '''
    @login_required()

    def post(self, request, pk):

        body_data = request.data

        data = dict()

        if body_data.get('work_for_hire'):
            data['work_for_hire'] = True
        else:
            data['work_for_hire'] = False

        if int(body_data.get('worker_type')) == 3:
            data['basic_salary_information'] = 0
            data['hourly_wage_information'] = 0
            data['hire_wage_information'] = 0

        elif int(body_data.get('worker_type')) == 2:
            data['basic_salary_information'] = body_data.get('basic_salary_information')
            if body_data.get('work_for_hire'):
                data['hire_wage_information'] = body_data.get('hire_wage_information')
            else:
                data['hire_wage_information'] = 0
            data['hourly_wage_information'] = 0

        elif int(body_data.get('worker_type')) == 1:
            data['hourly_wage_information'] = body_data.get('hourly_wage_information')
            data['hire_wage_information'] = 0
            data['basic_salary_information'] = 0

        data['worker_type'] = body_data.get('worker_type')

        employee_qs = Employee.objects.filter(id=pk)

        employee_qs.update(**data)

        return request.send_info("INF_015")


class UserEmployeeRankLevelDegreeEditApiView(APIView):
    ''' Ажилчны мэдээлэл засах
    '''
    @login_required()

    def post(self, request, pk):

        body_data = request.data

        data = dict()

        data['teacher_rank_type'] = body_data.get('teacher_rank_type')
        data['education_level'] = body_data.get('education_level')
        data['degree_type'] = body_data.get('degree_type')

        employee_qs = Employee.objects.filter(id=pk)
        employee_qs.update(**data)

        return request.send_info("INF_015")


class ExcelAddEmployeeCode(APIView):

    def get(self, request):

        my_data = pd.read_excel('static/file/kod.xlsx', sheet_name='ajilchid', header=None)

        oldohgui_humus = list()

        with transaction.atomic():
            for idx in my_data.index:

                if idx > 3:
                    phone_numbers = my_data.loc[idx][9]

                    for phoneIdx in [s.strip() for s in str(phone_numbers).split(",")]:
                        print('phoneIdx', idx, phoneIdx, my_data.loc[idx][4], my_data.loc[idx][5])

                        code = my_data.loc[idx][1]

                        user_by_phone_qs = User.objects.filter(phone_number=phoneIdx).values('id')
                        if user_by_phone_qs:
                            employee_qs = Employee.objects.filter(user_id__in=user_by_phone_qs).last()
                            print('employee_qs', employee_qs)
                            employee_qs.time_register_employee = code
                            employee_qs.register_code = code
                            employee_qs.save()
                            continue
                        else:
                            user_id = UserInfo.objects.filter(last_name=my_data.loc[idx][4], first_name=my_data.loc[idx][5]).values_list('user')
                            if user_id:
                                employee_qs = Employee.objects.filter(user_id__in=user_id).last()
                                print('employee_qs', employee_qs)
                                employee_qs.time_register_employee = code
                                employee_qs.register_code = code
                                employee_qs.save()
                                continue

                        data = dict()
                        data['idx'] = idx + 1
                        data['last_name'] = my_data.loc[idx][4]
                        data['first_name'] = my_data.loc[idx][5]
                        data['phone_number'] = my_data.loc[idx][9]

                        oldohgui_humus.append(data)

                        print('oldohgui bn')

            return request.send_data(oldohgui_humus)
