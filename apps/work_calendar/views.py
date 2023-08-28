from datetime import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q

from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from core.models import (
    Employee,
    WorkCalendar,
    WorkCalendarKind
)

from .serializer import WorkCalendarKindFormSerializer
from .serializer import WorkCalendarKindListSerializer
from .serializer import WorkCalendarFormSerializer
from .serializer import WorkCalendarListSerializer

from main.decorators import login_required
from main.decorators import has_permission


class IndexApiView(APIView):
    """ Ажлын календарь хуудас """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/work-calendar/index.html'

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-read'])
    def get(self, request):
        is_hr = request.employee.is_hr

        kinds = list(
            WorkCalendarKind
                .objects
                .filter(**request.exactly_org_filter)
        )

        #  нэмэлтээр харуулах төрлийг гаргасан нь
        extra_kinds = WorkCalendarKind.get_extra_kinds()
        kinds = kinds + extra_kinds

        employees = Employee.exactly_our_employees(request)
        #  хэрвээ hr ийн ажилтан биш ганц өөрийнх нь мэдээллийг буцаах

        if is_hr:
            employees = employees.filter(pk=request.employee.pk)

        return Response({
            "kinds": kinds,
            "employees": employees
        })


class WorkCalendarFormAPIView(
    mixins.CreateModelMixin,
    generics.GenericAPIView,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):

    queryset = WorkCalendar.objects
    serializer_class = WorkCalendarFormSerializer

    def get_data(self, pk):
        qs = self.queryset.get(id=pk)
        rsp_data = WorkCalendarListSerializer(instance=qs, many=False).data
        return rsp_data

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-read'])
    def get(self, request):
        #  Үйл ажиллагааг эхлээд байгууллага даяар үүссэн ү.а -г шүүх
        self.queryset = self.queryset.filter(**request.exactly_org_filter, for_type=WorkCalendar.FOR_WHOLE)
        self.serializer_class = WorkCalendarListSerializer

        extra_data = WorkCalendar.get_surgalt(request, [], is_all=True)

        data = self.list(request).data
        data = data + extra_data
        return request.send_data(data)

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-create'])
    def post(self, request):

        if request.data.get("for_type") == WorkCalendar.FOR_WHOLE:
            request.data['employees'] = list()

        data = self.create(request).data
        return request.send_rsp("INF_001", self.get_data(data.get("id")))

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-update'])
    def put(self, request, pk):
        data = self.update(request, pk).data
        return request.send_rsp("INF_002", self.get_data(data.get("id")))

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-delete'])
    def delete(self, request, pk):
        self.destroy(request, pk)
        return request.send_info("INF_003")


class WorkCalendarKindsApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/work-calendar/kinds/index.html'

    queryset = WorkCalendarKind.objects
    serializer_class = WorkCalendarKindFormSerializer

    def get_response(self, serializer, pk=None):
        return Response(
            {
                "serializer": serializer,
                "pk": pk
            }
        )

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-kind-read'])
    def get(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs)
            return self.get_response(serializer, pk)

        serializer = self.serializer_class()

        return self.get_response(serializer)

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-kind-update', 'work-calendar-kind-create'])
    def post(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs, data=request.data, context={ "request": request })
            if serializer.is_valid():
                serializer.save()
                request.send_message("success", 'INF_001')
            return self.get_response(serializer, pk)

        serializer = self.serializer_class(data=request.data, context={ "request": request })
        if serializer.is_valid():
            serializer.save()
            request.send_message("success", 'INF_002')
        return self.get_response(serializer, pk)


class WorkCalendarKindListApiView(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):

    queryset = WorkCalendarKind.objects
    serializer_class = WorkCalendarKindListSerializer

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-kind-read'])
    def get(self, request):
        self.queryset = self.queryset \
                            .filter(**request.exactly_org_filter) \
                            .order_by('title')

        rsp = self.list(request)
        rsp.data.append(
            {
                "text": "Шинээр үүсгэх",
                "a_attr": {
                    "href": reverse("work-calendar-kinds")
                },
                "icon": 'fa fa-folder-plus'
            }
        )
        return rsp


class WorkCalendarKindDeleteApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = WorkCalendarKind.objects
    serializer_class = WorkCalendarKindListSerializer

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-kind-delete'])
    def get(self, request, pk):

        self.destroy(request)
        request.send_message("success", 'INF_003')

        return redirect("work-calendar-kinds")


class WorkCalendarEmployeeAPIView(
    mixins.ListModelMixin,
    generics.GenericAPIView
):

    queryset = WorkCalendar.objects
    serializer_class = WorkCalendarListSerializer

    @login_required()
    @has_permission(allowed_permissions=['work-calendar-read'])
    def get(self, request, pk):

        self.queryset = self.queryset.filter(employees=pk)
        data = self.list(request).data

        extra_datas = WorkCalendar.get_extra_kind_datas(request, employee_ids=pk)
        data = data + extra_datas

        return request.send_data(data)


class WorkTodayApiView(
    mixins.ListModelMixin,
    generics.GenericAPIView
):

    @login_required()
    def get(self, request):

        filters = Q()
        filters.add(Q(for_type=WorkCalendar.FOR_WHOLE), Q.OR)
        filters.add(Q(employees=request.employee), Q.OR)

        now = datetime.now().date()

        filters.add(Q(start_date__date__lte=now), Q.AND)
        filters.add(Q(end_date__date__gte=now), Q.AND)

        filters.add(Q(org=request.exactly_org_filter.get("org")), Q.AND)
        filters.add(Q(sub_org=request.exactly_org_filter.get("sub_org")), Q.AND)
        filters.add(Q(salbar=request.exactly_org_filter.get("salbar")), Q.AND)

        date_filters = {
            "start_date__date__lte": now,
            "end_date__date__gte": now,
        }

        surgalt_filter = {
            "start_date__lte": now,
            "end_date__gte": now,
        }

        tomilolt = WorkCalendar.get_tomilolt(request, [request.employee], extra_filter=date_filters)
        surgalt_all = WorkCalendar.get_surgalt(request, [], is_all=True, extra_filter=surgalt_filter)
        surgalt = WorkCalendar.get_surgalt(request, [request.employee], is_all=False, extra_filter=surgalt_filter)

        qs = WorkCalendar.objects.filter(filters).order_by('start_date')
        data = WorkCalendarListSerializer(qs, many=True).data

        data = tomilolt + data + surgalt + surgalt_all

        return request.send_data(data)
