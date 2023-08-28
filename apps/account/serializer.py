from django.core.mail import send_mail

from core.models import Feedback, OrgVacationTypes, OrgVacationTypesBranchTypes, RequestTimeVacationRegister, ShagnalEmployee, UserContactInfoRequests
from core.models import UserTalent
from core.models import UserToken
from core.models import UserReward
from core.models import UserInfo
from core.models import Unit1
from core.models import Unit2
from core.models import Unit3
from core.models import User
from core.models import UserEducationInfo
from core.models import UserEducationDoctor
from core.models import UserEducation
from core.models import UserFamilyMember
from core.models import UserHamaatan
from core.models import UserEmergencyCall
from core.models import UserProfessionInfo
from core.models import UserWorkExperience
from core.models import UserErdmiinTsol
from core.models import UserLanguage
from core.models import UserOfficeKnowledge
from core.models import UserProgrammKnowledge
from core.models import ExtraSkillsDefinations
from core.models import UserExperience
from core.models import AccessHistory
from core.models import MainMedicalExamination
from core.models import AdditiveMedicalExamination
from core.models import InspectionType
from core.models import InspectionMedicalExamination

from rest_framework import serializers

from main.utils.encrypt import encrypt
from main.utils.mail_html.verifyMail import verifyMail


class UserSerializer(serializers.ModelSerializer):

    cpassword = serializers.CharField(source='password', label="Нууц үг", style={ "input_type": "password"} )

    class Meta:
        model = User
        fields = 'email', 'cpassword'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class UserRewardSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserReward
        fields = "id", "reward_name", "got_date", "company_name", "explanation", 'user', 'user_id', \
                'org', 'sub_org', 'salbar'


class UserRegisterSerializer(serializers.ModelSerializer):

    # sub_org = serializers.PrimaryKeyRelatedField(
    #     allow_null=True,
    #     label='Харьяалагдах алба нэгж',
    #     style={'template': "form/select.html", "class": "mt-4"},
    #     queryset=SubOrgs.objects.all(), required=False
    # )

    class Meta:
        model = User
        fields = 'email', 'password', 'phone_number', 'home_phone'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInfo
        fields = "__all__"


class MainMedicalExaminationSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainMedicalExamination
        fields = "__all__"


class AdditiveMedicalExaminationSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdditiveMedicalExamination
        fields = "__all__"


class InspectionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = InspectionType
        fields = "__all__"


class InspectionMedicalExaminationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"), read_only=True)

    class Meta:
        model = InspectionMedicalExamination
        fields = "__all__"


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = 'sub_org', 'salbar', 'phone_number', 'org_position', 'email', 'password'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance


class UserInfoRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInfo
        fields = '__all__'


class UserGeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = 'urgiin_ovog', 'last_name', 'first_name', 'gender', 'ys_undes', 'address', \
            'register', 'birthday', 'action_status', 'user_id', 'user', "id", "action_status_type", \
                'org', 'sub_org', 'salbar', 'suutsnii_torol', 'experience_year', 'experience_mnun_year'


class UserExtraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = 'register', 'birthday', "unit1_id", "unit2_id", "unit2", "unit1", "emdd_number", "ndd_number",\
            "body_height", "body_weight", "blood_type", 'action_status', \
                'user_id', 'user', "id", "action_status_type", \
                'org', 'sub_org', 'salbar', 'is_pension', 'is_disabled', 'is_training_licence'


class UserGeneralInfoPaginationSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="get_gender_display")
    requester = serializers.CharField(source="user.email")
    suutsnii_torol_name = serializers.CharField(source="get_suutsnii_torol_display")
    class Meta:
        model = UserInfo
        fields = 'urgiin_ovog', 'last_name', 'first_name', 'gender', 'ys_undes',\
            'address', 'register', 'birthday', 'action_status', 'user_id', 'user', "id", "action_status_type", 'requester', \
                'org', 'sub_org', 'salbar', 'suutsnii_torol', 'suutsnii_torol_name', 'experience_year', 'experience_mnun_year'


class UserExtraInfoPaginationSerializer(serializers.ModelSerializer):
    blood_type = serializers.CharField(source="get_blood_type_display")
    unit1 = serializers.CharField(source="unit1.name")
    unit2 = serializers.CharField(source="unit2.name")
    requester = serializers.CharField(source="user.email")

    class Meta:
        model = UserInfo
        fields = 'register', 'birthday', "emdd_number", "ndd_number",\
            "body_height", "body_weight", 'action_status', \
                'user_id', 'user', "id", "action_status_type", "unit1", "unit2", 'blood_type', 'requester', \
                'org', 'sub_org', 'salbar', 'is_pension', 'is_disabled', 'is_training_licence'


class Unit3Serializer(serializers.ModelSerializer):

    class Meta:
        model = Unit3
        fields = ["id", "name", "code"]


class Unit2Serializer(serializers.ModelSerializer):

    unit3 = Unit3Serializer(
        many=True,
        source="unit3_set"
    )
    class Meta:
        model = Unit2
        fields = ["id", "name", "code", 'unit3']


class Unit1Serializer(serializers.ModelSerializer):

    unit2 = Unit2Serializer(
        many=True,
        source="unit2_set"
    )

    class Meta:
        model = Unit1
        fields = ['id', 'name', "code", 'unit2']


class UserContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactInfoRequests
        fields = '__all__'


class UserContactInfoPagniationSerializer(serializers.ModelSerializer):
    requester = serializers.CharField(source="user.email")
    class Meta:
        model = UserContactInfoRequests
        fields = 'phone_number', 'action_status', 'email', 'user_id', 'user', 'home_phone', 'requester', 'id', \
                'org', 'sub_org', 'salbar'


class UserChangeContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'phone_number', 'email', 'home_phone'


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('real_photo', 'email', 'id')


class UserTalentSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTalent
        fields = "__all__"


class NormalRegiseterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "phone_number", "email", "password", "username"

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()
        request = self.context['request']
        request.data['user'] = instance.id
        request.data['action_status'] = UserInfo.APPROVED
        request.data['action_status_type'] = UserInfo.ACTION_TYPE_ALL
        serializer_userinfo = NormalRegiseterUserInfoSerializer(data=request.data)
        encrypted_mail =  encrypt(request.data['email'])

        send_mail(
            subject='Майлээ баталгаажуулах!',
            message="",
            from_email=request.data['email'],
            recipient_list=[request.data['email']],
            html_message=verifyMail(encrypted_mail, request.data['last_name'], request.data['first_name'], request.build_absolute_uri('/')[:-1])
        )
        if serializer_userinfo.is_valid():
            serializer_userinfo.save()

        return instance


class NormalRegiseterUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "last_name", "first_name", "action_status", "action_status_type", "user"


class NormalRegisterMailVerifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("mail_verified",)


class UserEducationInfoSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserEducationInfo
        exclude = "user_education",

    def create(self, validated_data):
        user_education = self.context.get("user_education")
        validated_data.update({ "user_education": user_education })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserEducationInfo.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserEducationDoctorSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserEducationDoctor
        exclude = "user_education",

    def create(self, validated_data):
        user_education = self.context.get("user_education")
        validated_data.update({ "user_education": user_education })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserEducationDoctor.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserEducationSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)

    class Meta:
        model = UserEducation
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        usereducationinfo = self.context.get("usereducationinfo")
        usereducationdoctor = self.context.get("usereducationdoctor")
        if validated_data.get("id"):
            validated_data.pop("id")

        obj, created = UserEducation.objects.update_or_create(
            user_id=request.user.id,
            defaults=validated_data
        )

        if usereducationinfo:
            education_serializer = UserEducationInfoSerializer(data=usereducationinfo, many=True, context={ "user_education": obj })
            if education_serializer.is_valid(raise_exception=True):
                education_serializer.save()

        if usereducationdoctor:
            education_dr_serializer = UserEducationDoctorSerializer(data=usereducationdoctor, many=True, context={ "user_education": obj })
            if education_dr_serializer.is_valid(raise_exception=True):
                education_dr_serializer.save()

        return obj


class UserFamilyMemberSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)

    class Meta:
        model = UserFamilyMember
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        obj, created = UserFamilyMember.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return obj


class UserHamaatanSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)

    class Meta:
        model = UserHamaatan
        exclude = "user",

    def create(self, validated_data):
        if not validated_data['birthday']:
            validated_data['birthday'] = None
        if not validated_data.get("id"):
            validated_data['id'] = None

        request = self.context.get("request")
        validated_data.update({ "user": request.user })

        instance, created = UserHamaatan.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserEmergencyCallSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)

    class Meta:
        model = UserEmergencyCall
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserEmergencyCall.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance

class UserProfessionInfoSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)

    class Meta:
        model = UserProfessionInfo
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserProfessionInfo.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserWorkExperienceSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserWorkExperience
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserWorkExperience.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserErdmiinTsolSerializer(serializers.ModelSerializer):
    cid = serializers.CharField(source="id", required=False, allow_blank=True)

    class Meta:
        model = UserErdmiinTsol
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserErdmiinTsol.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserLanguageSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserLanguage
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserLanguage.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserOfficeKnowledgeSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserOfficeKnowledge
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        if validated_data.get("id"):
            validated_data.pop("id")
        instance, created = UserOfficeKnowledge.objects.update_or_create(
            user=request.user,
            defaults=validated_data
        )
        return instance


class UserProgrammKnowledgeSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserProgrammKnowledge
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserProgrammKnowledge.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class ExtraSkillsDefinationsSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = ExtraSkillsDefinations
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = ExtraSkillsDefinations.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserExperienceSerializer(serializers.ModelSerializer):

    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = UserExperience
        exclude = "user",

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update({ "user": request.user })
        if not validated_data.get("id"):
            validated_data['id'] = None

        instance, created = UserExperience.objects.update_or_create(
            id=validated_data.get("id"),
            defaults=validated_data
        )
        return instance


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = "__all__"


class UserAllInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserInfoSerializer2(serializers.ModelSerializer):
    gender = serializers.CharField(source="get_gender_display")
    unit1 = serializers.CharField(source="unit1.name", default="")
    unit2 = serializers.CharField(source="unit2.name", default="")
    class Meta:
        model = UserInfo
        fields = "__all__"


class OrgVacationTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgVacationTypes
        fields = "__all__"


class OrgVacationTypesBranchTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgVacationTypesBranchTypes
        fields = "__all__"


class UserCholooSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTimeVacationRegister
        fields = "__all__"


class UserSanalHvseltSerializer(serializers.ModelSerializer):
    kind = serializers.SerializerMethodField()
    state = serializers.CharField(source='get_state_display')
    class Meta:
        model = Feedback
        fields = "__all__"

    def get_kind(self, obj):
        return obj.kind.title


class AccessHistorySerializer(serializers.ModelSerializer):

    state_display =serializers.CharField(source="get_state_display", read_only=True)
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"), read_only=True)

    class Meta:
        model = AccessHistory
        fields = '__all__'


class UserShagnalGETSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShagnalEmployee
        fields = 'id', 'desc', 'what_year', 'static_shagnal', 'kind', 'user'
        extra_kwargs = {
            'kind': {'write_only': True},
            'user': {'write_only': True},
        }


class UserShagnalSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    what_year = serializers.DateTimeField(format=("%Y-%m-%d"), read_only=True)

    class Meta:
        model = ShagnalEmployee
        fields = "name", 'id', 'desc', 'what_year'

    def get_name(self, obj):
        return obj.name
