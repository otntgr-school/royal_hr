from django.db import transaction
from django.db.models import Count
from django.db.models import F, Func, Value, CharField, Q
from django.db.models.functions import TruncDay

from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from rest_framework import mixins
from rest_framework import generics

from core.models import Pollee, QuestionChoices, Survey, SurveyQuestions

from .serializer import BoglohListSerializer, BoglohQuestionSerializer, PolleeSerializer, SurveyActionSerializer
from .serializer import SurveryListSerializer
from .serializer import SurveyGETSerializer
from .serializer import SurvetImageSerializer
from .serializer import SurveyPolleesQuestionSerializer
from .serializer import SurveyOroltsogchidNerSerializer


class SurveyTemplateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/survey/index.html'

    def get(self, request, pk=None):

        hamrah_huree = Survey.KIND_CHOICES
        question_kinds = SurveyQuestions.KIND_CHOICES

        return Response(
            {
                "hamrah_hurees": hamrah_huree,
                'question_kinds': question_kinds,
            }
        )


class SurveyListApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):

    queryset = Survey.objects
    serializer_class = SurveryListSerializer

    def get(self, request, pk=None):
        state = request.GET.get("state")

        if pk:
            self.serializer_class = SurveyGETSerializer
            data = self.retrieve(request, pk).data
            return request.send_data(data)

        extra_filters = {**Survey.get_filter(request), "deleted_at__isnull": True}
        if state:
            state_filters = Survey.get_state_filter(state)
            if state_filters:
                extra_filters.update(state_filters)

        self.queryset = self.queryset.filter(**extra_filters).order_by("-created_at")
        data = self.list(request).data
        return request.send_data(data)


class PolleeTemplateView(APIView):
    """ Судалгаа бөглөх хуудас """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/survey/bugluh/index.html'

    def get(self, request, pk=None):
        return Response({})


class SurveyActionApiView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin
):

    queryset = Survey.objects
    serializer_class = SurveyActionSerializer

    def post(self, request):
        body = request.data
        hamrah_huree_choices = body.get("hamrah_huree_choices")

        if 'employee' in body:
            del body['employee']
        if 'sub_org' in body:
            del body['sub_org']
        if 'salbar' in body:
            del body['salbar']

        body['created_by'] = request.employee.pk

        with transaction.atomic():
            serializer = self.serializer_class(
                data=body,
                many=False,
                context={
                    'request': request,
                    'questions': body.get("questions"),
                    'hamrah_huree_choices': hamrah_huree_choices
                }
            )
            if serializer.is_valid():
                serializer.save()
                return request.send_rsp("INF_001", serializer.data)
            return request.send_error_valid(serializer.errors)

    def put(self, request, pk):
        body = request.data
        hamrah_huree_choices = body.get("hamrah_huree_choices")

        if 'employee' in body:
            del body['employee']
        if 'sub_org' in body:
            del body['sub_org']
        if 'salbar' in body:
            del body['salbar']

        body['created_by'] = request.employee.pk

        with transaction.atomic():
            obj = self.queryset.get(pk=pk)
            serializer = self.serializer_class(
                instance=obj,
                data=body,
                many=False,
                context={
                    'request': request,
                    'questions': body.get("questions"),
                    'hamrah_huree_choices': hamrah_huree_choices
                }
            )
            if serializer.is_valid():
                serializer.save()
                return request.send_rsp("INF_002", serializer.data)
            return request.send_error_valid(serializer.errors)


class BoglohListApiView(APIView):
    def get(self, request, pk=None):

        state = request.GET.get("state")

        """ Судалгаа авах """
        # Нэг судалгааг авах
        if pk:
            survey_obj = Survey.objects.filter(id=pk).first()
            serializer = BoglohQuestionSerializer(instance=survey_obj.questions.all(), many=True)
            return request.send_data(serializer.data)
        # Бүх судалгааг авах
        else:
            extra_filters = {**Survey.get_filter(request), "deleted_at__isnull": True}
            if state:
                state_filters = Survey.get_state_filter(state)
                if state_filters:
                    extra_filters.update(state_filters)

            snippets = Survey.objects.filter(**extra_filters).order_by("-is_required", '-start_date')
            serializer = BoglohListSerializer(snippets, many=True, context={ 'request': request })
            return request.send_data(serializer.data)

    def post(self, request):
        """ Судалгаа бөглөх """
        with transaction.atomic():
            serializer = PolleeSerializer(data=request.data, many=True, context={ "request": request })

            if serializer.is_valid():
                serializer.save()
                return request.send_info("INF_001")
            return request.send_error_valid(serializer.errors)


class BoglosonApiView(APIView):
    def get(self, request, pk):
        """ Бөглөсөн судалгаа авах """
        pollee_qs = Pollee.objects.filter(survey=pk)
        serializer = PolleeSerializer(pollee_qs, many=True)
        return request.send_data(serializer.data)


class SurveyRejectApiView(APIView):

    def delete(self, request):

        ids = request.GET.get("ids")

        if "," in ids:
            ids = ids.split(",")
        else:
            ids = [ids]

        if not ids:
            return request.send_error("ERR_013")

        is_updated = Survey.objects.filter(pk__in=ids).update(
            deleted_by=request.employee,
            deleted_at=datetime.now(),
        )

        if not is_updated:
            return request.send_error("ERR_013")

        return request.send_info("INF_003")


class SurveyImageApiView(APIView):

    def post(self, request, survey_id):
        survey = Survey.objects.get(id=survey_id)
        data = SurvetImageSerializer(instance=survey, data=request.FILES)
        data.is_valid()
        data.save()
        return request.send_info("INF_002")


class PollesQuestionApiView(APIView):

    def get(self, request, pk):
        survey = Survey.objects.get(id=pk)
        data = SurveyPolleesQuestionSerializer(survey, many=False).data
        pollees = survey.pollee_set \
                .values('created_at') \
                .annotate(name=Func(
                    TruncDay('created_at'),
                    Value('yyyy-MM-dd'),
                    function='to_char',
                    output_field=CharField()
                )) \
                .values("name") \
                .annotate(count=Count("name")) \
                .order_by("name")

        poll_users = list()
        if not survey.is_hide_employees:

            group_field = "employee"
            if Survey.KIND_ALL == survey.kind:
                group_field = "user"

            qs = survey.pollee_set \
                .values(group_field) \
                .annotate(count=Count(group_field)) \
                .values("count", name=F(group_field)) \
                .order_by("-count")

            poll_users = SurveyOroltsogchidNerSerializer(qs, many=True, context={ "group_field": group_field }).data

        return request.send_data(
            {
                "questions": data,
                "pollees": pollees,
                "poll_users": poll_users
            }
        )


class SurveyDeleteQuestion(APIView):
    def delete(self, request, pk):
        survey = Survey.objects.filter(**Survey.get_filter(request), questions__id=pk).first()
        if survey:
            q = SurveyQuestions.objects.get(pk=pk)
            q.delete()
            return request.send_info("INF_003")
        return request.send_error("ERR_013")


class SurveyDeleteChoice(APIView):
    def delete(self, request, pk):
        survey = Survey.objects.filter(**Survey.get_filter(request), questions__choices__id=pk).first()
        if survey:
            q = QuestionChoices.objects.get(pk=pk)
            q.delete()
            return request.send_info("INF_003")
        return request.send_error("ERR_013")
