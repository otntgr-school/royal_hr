from django.db.models.functions import Concat, Upper, Substr
from django.db.models import F, Value, Q, Case, When
from django.http import JsonResponse
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from core.models import Feedback, FeedbackKind, UserInfo
from core.models import HrOrderFormEmployee
from core.models import ViolationRegistrationPage

from core.fns import WithChoices

from .serializer import ReportUrgudulDTSerializer
from .serializer import HrOrderFormEmployeeSerializer
from .serializer import HrOrderFormEmployeeJsonSerializer
from .serializer import HrOrderFormEmployeeAnswerJsonSerializer
from .serializer import ViolationRegistrationPageJsonSerializer
from .serializer import ViolationRegistrationPageSerializer

from main.decorators import has_permission, login_required
from main.utils.datatable import data_table
from main.utils.date import date_str_to_datetime


class ReportUrgudulApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/urgudul-report/index.html'

    @login_required()
    @has_permission(must_permissions=['urgudul-report-read'])
    def get(self, request):
        states = Feedback.STATE_CHOICES
        kinds = FeedbackKind.objects.filter(**request.exactly_org_filter)
        return Response(
            {
                "states": states,
                "kinds": kinds
            }
        )


class ReportUrgudulDTApiView(APIView):

    @login_required()
    @has_permission(must_permissions=['urgudul-report-read'])
    def get(self, request):

        turul = request.GET.get("turul")
        ilgeeh = request.GET.get("ilgeeh")
        shiideh = request.GET.get("shiideh")

        extra_filters = dict()

        if ilgeeh:
            ilgeeh_start, ilgeeh_end = ilgeeh.split(",")
            if ilgeeh_start and ilgeeh_end:
                ilgeeh_start = date_str_to_datetime(ilgeeh_start)
                ilgeeh_end = date_str_to_datetime(ilgeeh_end)
                extra_filters['created_at__date__gte'] = ilgeeh_start
                extra_filters['created_at__date__lte'] = ilgeeh_end
        if shiideh:
            shiideh_start, shiideh_end = shiideh.split(",")
            if shiideh_start and shiideh_end:
                shiideh_start = date_str_to_datetime(shiideh_start)
                shiideh_end = date_str_to_datetime(shiideh_end)
                extra_filters['decided_at__date__gte'] = shiideh_start
                extra_filters['decided_at__date__lte'] = shiideh_end

        if turul == 'to_emp':
            qs = Feedback \
                    .objects \
                    .filter(
                        **request.exactly_org_filter,
                        from_employee__user__userinfo__action_status=UserInfo.APPROVED,
                        from_employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                        to_employees__user__userinfo__action_status=UserInfo.APPROVED,
                        to_employees__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                        **extra_filters,
                    ) \
                    .annotate(
                        from_employee_name=Concat(Upper(Substr("from_employee__user__userinfo__last_name", 1, 1)), Value(". "), "from_employee__user__userinfo__first_name"),
                        to_employee_name=Concat(Upper(Substr("to_employees__user__userinfo__last_name", 1, 1)), Value(". "), "to_employees__user__userinfo__first_name"),
                        state_name=WithChoices(Feedback.STATE_CHOICES, 'state'),
                        kind_name=F("kind__title"),
                    )

        elif turul == 'hr':
            qs = Feedback \
                    .objects \
                    .filter(
                        **request.exactly_org_filter,
                        from_employee__user__userinfo__action_status=UserInfo.APPROVED,
                        from_employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                        **extra_filters,
                    ) \
                    .annotate(
                        from_employee_name=Concat(Upper(Substr("from_employee__user__userinfo__last_name", 1, 1)), Value(". "), "from_employee__user__userinfo__first_name"),
                        to_employee_name=Value("Хүний нөөц"),
                        state_name=WithChoices(Feedback.STATE_CHOICES, 'state'),
                        kind_name=F("kind__title"),
                    )

        else:
            qs = Feedback \
                    .objects \
                    .filter(
                        Q(
                            **request.exactly_org_filter,
                            from_employee__user__userinfo__action_status=UserInfo.APPROVED,
                            from_employee__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                            **extra_filters
                        )
                        &
                        Q(
                            **extra_filters,
                            to_employees__user__userinfo__action_status=UserInfo.APPROVED,
                            to_employees__user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                        )
                        |
                        Q(
                            **request.exactly_org_filter,
                            to_employees__isnull=True,
                            **extra_filters,
                        )
                    ) \
                    .annotate(
                        from_employee_name=Concat(Upper(Substr("from_employee__user__userinfo__last_name", 1, 1)), Value(". "), "from_employee__user__userinfo__first_name"),
                        to_employee_name=Case(
                            When(to_employees__isnull=True, then=Value("Хүний нөөц")),
                            default=Concat(Upper(Substr("to_employees__user__userinfo__last_name", 1, 1)), Value(". "), "to_employees__user__userinfo__first_name"),
                        ),
                        state_name=WithChoices(Feedback.STATE_CHOICES, 'state'),
                        kind_name=F("kind__title"),
                    )

        paginated = data_table(qs, request)
        paginated['data'] = ReportUrgudulDTSerializer(paginated['data'], many=True).data
        return Response(paginated)


class HrOrderFormApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/hr-order-form/answer/index.html'

    @login_required()
    # @has_permission(must_permissions=['urgudul-report-read'])
    def get(self, request):
        return Response(
            {
            }
        )


class HrOrderFormCreateApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/hr-order-form/create/index.html'

    @login_required()
    # @has_permission(must_permissions=['urgudul-report-read'])
    def get(self, request):
        return Response(
            {
            }
        )


class HrOrderFormCreateActionApiView(APIView):

    @login_required()
    def post(self, request):

        request.data._mutable = True
        request.data['employee']= request.employee.id
        request.data._mutable = False

        serializer = HrOrderFormEmployeeSerializer(data=request.data)

        if not serializer.is_valid():
            raise request.send_error("ERR_023")

        serializer.save()
        return request.send_info("INF_001")


    @login_required()
    def put(self, request, pk=None):

        snippet = HrOrderFormEmployee.objects.filter(id=pk)
        snippet.update(**request.data)

        return request.send_info("INF_002")


class HrOrderFormCreateJsonApiView(APIView):

    @login_required()
    def get(self, request):
        ''' Хүний нөөцийн захиалгын хуудасны хүсэлтүүдийн datatable-ийн утгыг авна
        '''

        qs = HrOrderFormEmployee.objects.filter(employee=request.employee)
        paginated = data_table(qs, request)
        paginated['data'] = HrOrderFormEmployeeJsonSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class HrOrderFormAnswerJsonApiView(APIView):

    @login_required()
    def get(self, request):
        ''' Хүний нөөцийн захиалгын хуудасны хүсэлтүүдийн datatable-ийн утгыг авна
        '''

        qs = HrOrderFormEmployee.objects.all()
        paginated = data_table(qs, request)
        paginated['data'] = HrOrderFormEmployeeAnswerJsonSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class ViolationRegistrationApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/violation-registration/registration/index.html'

    @login_required()
    def get(self, request):
        return Response()


class ViolationRegistrationListApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/violation-registration/list/index.html'

    @login_required()
    def get(self, request):
        return Response()


class ViolationRegistrationJsonApiView(APIView):

    @login_required()
    def get(self, request):
        ''' Зөрчил бүртгэх хуудас бүртгэлүүд хуудасны datatable-ийн утгыг авна
        '''

        qs = ViolationRegistrationPage.objects.filter()
        paginated = data_table(qs, request)
        paginated['data'] = ViolationRegistrationPageJsonSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class ViolationRegistrationListJsonApiView(APIView):

    @login_required()
    def get(self, request):
        ''' Зөрчил бүртгэх хуудас хуудасны datatable-ийн утгыг авна
        '''

        qs = ViolationRegistrationPage.objects.filter(employee=request.employee)
        paginated = data_table(qs, request)
        paginated['data'] = ViolationRegistrationPageJsonSerializer(paginated['data'], many=True).data

        return JsonResponse(paginated, safe=False)


class ViolationRegistrationActionApiView(APIView):

    @login_required()
    def post(self, request):

        request.data._mutable = True
        request.data['employee']= request.employee.id
        request.data._mutable = False

        serializer = ViolationRegistrationPageSerializer(data=request.data)

        if not serializer.is_valid():
            raise request.send_error("ERR_023")

        serializer.save()
        return request.send_info("INF_001")


    @login_required()
    def delete(self, request, pk=None):

        ViolationRegistrationPage.objects.filter(id=pk).delete()

        return request.send_info("INF_003")


class NoteOnDisciplinaryApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/disciplinary/index.html'

    @login_required()
    def get(self, request):
        return Response()
