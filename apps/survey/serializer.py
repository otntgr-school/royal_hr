from datetime import datetime as dt
from rest_framework import serializers

from django.db.models import Count
from django.db.models import Q
from django.db.models import F
from django.db.models import Case
from django.db.models import When
from django.db.models import Value

from core.models import (
    QuestionChoices,
    Survey,
    SurveyQuestions,
    SubOrgs,
    Salbars,
    OrgPosition,
    Employee,
    Pollee,
    User
)

from main.utils.file import get_name_from_path


class SurveyActionSerializer(serializers.ModelSerializer):

    sub_org = serializers.PrimaryKeyRelatedField(label='Харьяалагдах алба нэгж', many=True, queryset=SubOrgs.objects.all(), required=False)
    salbar = serializers.PrimaryKeyRelatedField(label='Салбар', many=True, queryset=Salbars.objects.all(), required=False)
    org_positions = serializers.PrimaryKeyRelatedField(label='Албан тушаал', many=True, queryset=OrgPosition.objects.all(), required=False)
    employees = serializers.PrimaryKeyRelatedField(label='Албан хаагч', many=True, queryset=Employee.objects.all(), required=False)

    class Meta:
        model = Survey
        exclude = "questions",

    def create(self, validated_data):
        request = self.context.get("request")
        questions = self.context["questions"]
        hamrah_huree_choices = self.context.get("hamrah_huree_choices")

        kind = validated_data.get("kind")
        created_by = request.employee

        if kind == Survey.KIND_ALL:
            validated_data['is_all'] = True
        elif kind == Survey.KIND_ORG:
            validated_data['org'] = request.org_filter.get("org")

        created_orgs = Survey.get_filter(request)
        validated_data.update(created_orgs)

        survey = Survey.objects.create(**validated_data)
        if kind == Survey.KIND_EMPLOYEES:
           survey.employees.set(hamrah_huree_choices)

        elif kind == Survey.KIND_SUB_ORG:
           survey.sub_org.set(hamrah_huree_choices)

        elif kind == Survey.KIND_POSITIONS:
           survey.org_positions.set(hamrah_huree_choices)

        elif kind == Survey.KIND_SALBAR:
           survey.salbar.set(hamrah_huree_choices)

        question_ids = list()

        for question in questions:
            choices = question.pop("choices")
            question['is_required'] = len(question['is_required']) > 0
            qkind = question.get("kind")
            question['created_by'] = created_by

            if not question.get('max_choice_count'):
                question['max_choice_count'] = 0

            if not question.get('rating_max_count'):
                question['rating_max_count'] = 0
            else:
                question['rating_max_count'] = 5

            if "cid" in question:
                del question['cid']
            if "id" in question:
                del question['id']

            question_obj = SurveyQuestions.objects.create(**question)

            choice_ids = list()

            #  асуултын сонголтуудыг үүсгэх нь
            if int(qkind) in [SurveyQuestions.KIND_MULTI_CHOICE, SurveyQuestions.KIND_ONE_CHOICE]:
                for choice in choices:
                    choice['created_by'] = created_by
                    obj = QuestionChoices.objects.create(**choice)
                    choice_ids.append(obj.id)

            question_obj.choices.set(choice_ids)
            question_ids.append(question_obj.id)

        survey.questions.set(question_ids)
        return survey

    def update(self, instance, validated_data):
        request = self.context.get("request")
        questions = self.context["questions"]
        hamrah_huree_choices = self.context.get("hamrah_huree_choices")

        kind = validated_data.get("kind")
        created_by = request.employee

        if kind == Survey.KIND_ALL:
            validated_data['is_all'] = True
        elif kind == Survey.KIND_ORG:
            validated_data['org'] = request.org_filter.get("org")

        created_orgs = Survey.get_filter(request)
        validated_data.update(created_orgs)

        is_updated = Survey.objects.filter(pk=instance.id).update(**validated_data)
        survey = Survey.objects.get(pk=instance.id)
        if instance.kind != kind:
            if instance.kind == Survey.KIND_EMPLOYEES:
                survey.employees.set([])

            elif instance.kind == Survey.KIND_SUB_ORG:
                survey.sub_org.set([])

            elif instance.kind == Survey.KIND_POSITIONS:
                survey.org_positions.set([])

            elif instance.kind == Survey.KIND_SALBAR:
                survey.salbar.set([])

        if kind == Survey.KIND_EMPLOYEES:
            survey.employees.set(hamrah_huree_choices)

        elif kind == Survey.KIND_SUB_ORG:
            survey.sub_org.set(hamrah_huree_choices)

        elif kind == Survey.KIND_POSITIONS:
            survey.org_positions.set(hamrah_huree_choices)

        elif kind == Survey.KIND_SALBAR:
            survey.salbar.set(hamrah_huree_choices)

        question_ids = list()

        for question in questions:
            choices = question.pop("choices") if "choices" in question else []
            question['is_required'] = len(question['is_required']) > 0
            qkind = question.get("kind")
            question['created_by'] = created_by

            if not question.get('max_choice_count'):
                question['max_choice_count'] = 0

            if not question.get('rating_max_count'):
                question['rating_max_count'] = 0
            else:
                question['rating_max_count'] = 5

            if not question.get('id'):
                question['id'] = None

            question.pop("cid")

            question_obj, iscreated = SurveyQuestions.objects.update_or_create(
                id=question['id'],
                defaults=question
            )

            choice_ids = list()

            #  асуултын сонголтуудыг үүсгэх нь
            if int(qkind) in [SurveyQuestions.KIND_MULTI_CHOICE, SurveyQuestions.KIND_ONE_CHOICE]:
                for choice in choices:
                    choice['created_by'] = created_by

                    if not choice.get('id'):
                        choice['id'] = None
                    choice.pop("cid")

                    obj, iscreated = QuestionChoices.objects.update_or_create(
                        id=choice['id'],
                        defaults=choice
                    )
                    choice_ids.append(obj.id)

            question_obj.choices.set(choice_ids)
            question_ids.append(question_obj.id)

        survey.questions.set(question_ids)
        return survey


class SurveryListSerializer(serializers.ModelSerializer):

    question_count = serializers.IntegerField(source="questions.count")
    state = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = "title", 'description', 'start_date', 'end_date', 'question_count', 'state', 'id'

    def get_state(self, obj):
        dn = dt.now()
        start_date = obj.start_date
        end_date = obj.end_date
        if dn > start_date and dn < end_date:
            return "PROGRESSING"
        if dn <= start_date:
            return "WAITING"
        if dn > end_date:
            return "FINISH"


class SurveyEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = "__all__"


class BoglohListSerializer(serializers.ModelSerializer):

    question_count = serializers.IntegerField(source="questions.count")
    created_by = serializers.CharField(source="created_by.user.info.full_name")
    state = serializers.SerializerMethodField()
    submitted = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = "title", 'description', 'start_date', 'end_date', 'question_count', 'state', 'id', 'created_by', 'submitted', 'has_shuffle', 'is_required'

    def get_state(self, obj):
        dn = dt.now()
        start_date = obj.start_date
        end_date = obj.end_date
        if dn > start_date and dn < end_date:
            return "PROGRESSING"
        if dn <= start_date:
            return "WAITING"
        if dn > end_date:
            return "FINISH"

    def get_submitted(self, obj):
        pollee = Pollee.objects.filter(Q(user=self.context['request'].user.pk) | Q(employee=self.context['request'].employee.pk), survey=obj.id).first()
        if pollee:
            return True
        else:
            return False


class QuestionChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoices
        fields = '__all__'


class BoglohQuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoicesSerializer(many=True)
    class Meta:
        model = SurveyQuestions
        fields = "__all__"


class PolleeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pollee
        exclude = "user", "employee"

    def create(self, validated_data):

        validated_data['user'] = self.context['request'].user
        validated_data['employee'] = self.context['request'].employee

        return super().create(validated_data)


class EditQuestionChoicesSerializer(serializers.ModelSerializer):
    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    class Meta:
        model = QuestionChoices
        fields = '__all__'


class EditBoglohQuestionSerializer(serializers.ModelSerializer):
    cid = serializers.CharField(source="id", required=False, allow_blank=True)
    choices = EditQuestionChoicesSerializer(many=True)
    is_required = serializers.SerializerMethodField()
    class Meta:
        model = SurveyQuestions
        fields = "__all__"

    def get_is_required(self, obj):
        return ['yes'] if obj.is_required else []


class SurveyGETSerializer(serializers.ModelSerializer):

    questions = EditBoglohQuestionSerializer(many=True)
    image_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    has_pollee = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = "__all__"

    def get_has_pollee(self, obj):
        """ Тухайн судалгааг шинэчлэх засах эсэх """
        has_pollee = obj.pollee_set.exists()

        #  хугацаа нь дууссан байвал бас засахгүй
        dn = dt.now()
        end_date = obj.end_date
        if dn > end_date:
            return True

        return has_pollee

    def get_image_name(self, obj):
        return get_name_from_path(obj.image.path) if obj.image else ""

    def get_image_url(self, obj):
        return obj.image.url if obj.image else ""


class SurvetImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = "id", 'image'


has_choice_kinds = [SurveyQuestions.KIND_MULTI_CHOICE, SurveyQuestions.KIND_ONE_CHOICE]
class SurveyBoglohQuestionSerializer(serializers.ModelSerializer):

    pollees = serializers.SerializerMethodField()
    rsp_count = serializers.IntegerField(source="pollee_set.count")

    class Meta:
        model = SurveyQuestions
        fields = "pollees", 'question', 'id', 'rsp_count', 'kind'

    def get_pollees(self, obj):
        if obj.kind in has_choice_kinds:
            return obj \
                    .choices \
                    .annotate(count=Count("pollee")) \
                    .values("count", name=F('choices')) \
                    .order_by("id")

        elif obj.kind in [SurveyQuestions.KIND_BOOLEAN]:
            return Pollee \
                    .objects \
                    .filter(question=obj) \
                    .values("answer") \
                    .annotate(count=Count("answer")) \
                    .values(
                        "count",
                        name=Case(
                            When(answer="1", then=Value('Тийм')),
                            When(answer="0", then=Value('Үгүй')),
                            default=Value('')
                        )
                    ) \
                    .order_by("-count")

        elif SurveyQuestions.KIND_RATING == obj.kind:
            polls = list(
                    Pollee
                        .objects
                        .filter(question=obj)
                        .values("answer")
                        .annotate(count=Count("answer"))
                        .values("count", name=F('answer'))
                        .order_by("answer")
            )

            has_count = [
                poll["name"]
                for poll in polls
            ]
            rates = list(range(1, obj.rating_max_count + 1))
            for remove_rate in has_count:
                rates.remove(int(remove_rate))

            for empty_rate in rates:
                polls.append(
                    {
                        "name": empty_rate,
                        "count": 0
                    }
                )

            polls.sort(key=lambda x: int(x['name']))
            return polls

        elif SurveyQuestions.KIND_TEXT == obj.kind:
            return Pollee.objects.filter(question=obj).values("answer").annotate(count=Count("answer")).values("count", name=F('answer')).order_by("-count")


class SurveyPolleesQuestionSerializer(serializers.ModelSerializer):

    questions = SurveyBoglohQuestionSerializer(many=True)

    class Meta:
        model = Survey
        fields = "id", 'questions'


class SurveyOroltsogchidNerSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Pollee
        fields = "user", 'count'

    def get_user(self, obj):
        group_field = self.context.get('group_field')
        id = obj.get("name")
        name = ""
        img = ""
        if group_field == "user":
            user = User.objects.get(id=id)
            name = user.full_name
            img = user.real_photo.url if user.real_photo else ""
        else:
            employee = Employee.objects.get(id=id)
            name = employee.full_name
            img = employee.user.real_photo.url if employee.user.real_photo else ""

        return {
            "name": name,
            "img": img
        }

    def get_count(self, obj):
        return obj.get("count")
