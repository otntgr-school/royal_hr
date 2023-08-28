
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import mixins

from django.db.models import Q
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect

from core.models import KpiIndicator
from core.models import OrgPosition
from core.models import KpiIndicatorAssessment
from core.models import Employee
from core.models import UserInfo

from .serializer import KpiIndicatorSerializer
from .serializer import PositionsTreeSerializer
from .serializer import KpiIndicatorJsonSerializer
from .serializer import KpiIndicatorAssessmentSerializer
from .serializer import EmployeeKpiReportJson

from main.decorators import login_required
from main.decorators import has_permission
from main.utils.datatable import data_table


class KpiRegisterApiView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    ''' Ажлын цагийн төрөл CRUD үйлдэл
    '''

    serializer_class = KpiIndicatorSerializer
    queryset = KpiIndicator.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/kpi/kpi-register/index.html'

    @login_required()
    # @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk=None):

        if pk:
            snippet = self.queryset.filter(org_position=pk)
            org_position_name = OrgPosition.objects.get(pk=pk)
            serializer = self.serializer_class(snippet)
            return Response({
                'serializer': serializer,
                'org_position': pk,
                'org_position_name': org_position_name
            })

        return Response({
            'serializer': self.serializer_class
        })

    def post(self, request, pk=None):
        ''' Шинээр үүсгэх
        '''
        request_data = request.data

        serializer = self.serializer_class(data=request_data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('kpi-register', pk=request.data.get('org_position'))


class KpiRegisterOrgPositionApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
):
    """ Тухайн нэвтэрсэн хүний байгууллагын албан тушаал мод хэлбэрээр дата авах """
    queryset = OrgPosition.objects
    serializer_class = PositionsTreeSerializer

    @login_required()
    def get(self, request):
        self.queryset = self.queryset.filter(org=request.org_filter.get("org")).order_by("id")
        rsp = self.list(request)
        return rsp


class RegisterJsonApiView(APIView):
    def get(self, request, pk=None):
        ''' Ажлын цагийн төрөлийн datatable-ийн утгыг авна
        '''

        if not pk:
            return
        org_position_id = pk

        qs = KpiIndicator.objects.filter(org_position=org_position_id)
        paginated = data_table(qs, request)
        paginated['data'] = KpiIndicatorJsonSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class KpiRegisterAjaxAPIView(APIView):
    ''' Ажлын цагийн төрөл ajax үйлдлүүд
    '''

    def get_object(self, pk, request):
        try:
            return KpiIndicator.objects.get(pk=pk)
        except KpiIndicator.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = KpiIndicatorSerializer(snippet)
        return request.send_data(serializer.data)

    @login_required()
    @has_permission(allowed_permissions=['work-time-type-update'])
    def put(self, request, pk=None):
        snippet = KpiIndicator.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")


class KpiAssessmentApiView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    ''' Ажлын цагийн төрөл CRUD үйлдэл
    '''

    serializer_class = KpiIndicatorAssessmentSerializer
    queryset = KpiIndicatorAssessment.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/kpi/give-an-assessment/index.html'

    @login_required()
    # @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk=None):

        employee_id = request.employee.id
        employee_full_name = request.employee.full_name

        if pk:
            serializer = self.serializer_class

            return Response({
                'serializer': serializer,
                'employee_id': employee_id,
                'employee_full_name': employee_full_name
            })

        return Response({
            'serializer': self.serializer_class,
            'employee_id': employee_id,
            'employee_full_name': employee_full_name
        })

    def post(self, request):
        request_data = request.data

        serializer = self.serializer_class(data=request_data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('kpi-assessment')


class KpiAssessmentEmployeeJsonApiView(generics.GenericAPIView):
    def get(self, request, pk=None):
        ''' Ажлын цагийн төрөлийн datatable-ийн утгыг авна
        '''

        if not pk:
            return

        date = request.GET.get('date')

        year = date[0:4]
        month = date[5:7]

        qs = KpiIndicatorAssessment.objects.filter(
            employee__id=pk,
            created_at__year=year,
            created_at__month=month
        )
        paginated = data_table(qs, request)
        paginated['data'] = KpiIndicatorAssessmentSerializer(paginated['data'], many=True).data
        return JsonResponse(paginated, safe=False)


class KpiAssessmentAjaxAPIView(APIView):
    ''' Ажлын цагийн төрөл ajax үйлдлүүд
    '''

    def get_object(self, pk, request):
        try:
            return KpiIndicatorAssessment.objects.get(pk=pk)
        except KpiIndicatorAssessment.DoesNotExist:
            raise request.send_error("ERR_003")

    @login_required()
    # @has_permission(allowed_permissions=['work-time-type-delete'])
    def delete(self, request, pk=None):
        delete_data = self.get_object(pk, request)
        delete_data.delete()
        return request.send_info("INF_003")

    @login_required()
    # @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk, format=None):
        snippet = self.get_object(pk, request)
        serializer = KpiIndicatorAssessmentSerializer(snippet)
        return request.send_data(serializer.data)

    @login_required()
    # @has_permission(allowed_permissions=['work-time-type-update'])
    def put(self, request, pk=None):
        snippet = KpiIndicatorAssessment.objects.filter(id=pk)
        snippet.update(**request.data)
        return request.send_info("INF_002")

    def post(self, request):
        request_data = request.data

        serializer = KpiIndicatorAssessmentSerializer(data=request_data)
        if not serializer.is_valid():
            return Response({ 'serializer': serializer })

        serializer.save()
        return request.send_info('INF_015')


class EmployeeNameAjaxApiView(APIView):
    def get(self, request, pk=None):
        qs = Employee.objects.get(pk=pk)
        return request.send_data(qs.full_name)


class ReportApiView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    ''' Ажлын цагийн төрөл CRUD үйлдэл
    '''

    serializer_class = KpiIndicatorAssessmentSerializer
    queryset = KpiIndicatorAssessment.objects

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/kpi/report/index.html'

    @login_required()
    # @has_permission(allowed_permissions=['work-time-type-read'])
    def get(self, request, pk=None):

        employee_id = request.employee.id
        employee_full_name = request.employee.full_name

        if pk:
            serializer = self.serializer_class

            return Response({
                'serializer': serializer
            })

        return Response({
            'serializer': self.serializer_class
        })


class KpiReportJsonApiView(generics.GenericAPIView):
    def get(self, request):
        ''' Kpi үнэлгээний бүх ажилтны үнэлгээний тайлан
        '''

        filters = Employee.get_filter(request)

        qs = Employee.objects \
            .filter(
                **filters,
                user__userinfo__action_status=UserInfo.APPROVED,
                user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                state=Employee.STATE_WORKING
            ) \
            .annotate(
                first_name=F("user__userinfo__first_name"),
                last_name=F("user__userinfo__last_name"),
                org_name=F("org__name"),
                sub_org_name=F("sub_org__name"),
                salbar_name=F("salbar__name"),
                org_position_name=F("org_position__name"),
            )

        paginated = data_table(qs, request)
        paginated['data'] = EmployeeKpiReportJson(paginated['data'], many=True, context={ "request": request }).data
        return JsonResponse(paginated, safe=False)
