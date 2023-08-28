from django.shortcuts import redirect
from django.db.models import Max
from django.db.models import Q
from django.db import transaction
from django.db.models import Value, IntegerField

from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from core.models import (
    Employee,
    ShagnalEmployee,
    StaticShagnal,
    Shagnal,
)

from .serializer import ShagnalTailanSerializer, StaticShagnalFormSerializer
from .serializer import DynamicShagnalFormSerializer
from .serializer import ShagnalEmployeeFormSerializer
from .serializer import ShagnalEmployeeListSerializer

from main.decorators import login_required
from main.decorators import has_permission


class StaticShagnalApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/shagnal/system/index.html'

    queryset = StaticShagnal.objects
    serializer_class = StaticShagnalFormSerializer

    def get_response(self, serializer, pk=None):
        return Response(
            {
                "serializer": serializer,
                "pk": pk
            }
        )

    @login_required(is_superuser=True)
    def get(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs)
            return self.get_response(serializer, pk)

        serializer = self.serializer_class()

        return self.get_response(serializer)

    @login_required(is_superuser=True)
    def post(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs, data=request.data)
            if serializer.is_valid():
                serializer.save()
                request.send_message("success", 'INF_001')
            return redirect("static-shagnal")

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            request.send_message("success", 'INF_002')
        return redirect("static-shagnal")


class StaticShagnalListApiView(APIView):

    @login_required(is_superuser=True)
    def get(self, request):
        static_shagnals = StaticShagnal.objects.all().values("id", 'name', 'order').order_by("order")
        return request.send_data(static_shagnals)


class StaticShagnalDeleteApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = StaticShagnal.objects
    serializer_class = StaticShagnalFormSerializer

    @login_required(is_superuser=True)
    def get(self, request, pk):

        self.destroy(request)
        request.send_message("success", 'INF_003')

        return redirect("static-shagnal")


class StaticShagnalChangeOrder(APIView):

    @login_required(is_superuser=True)
    @transaction.atomic()
    def put(self, request):

        from_id = request.data.get("from_id")
        to_id = request.data.get("to_id")

        if not from_id:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from_qs = StaticShagnal.objects.filter(id=from_id)
        #  фронтоос хамгийн доор байрлуулахад id ирэхгүй байгаа учраас түүнийг хайж олох нь
        if not to_id:
            _to = StaticShagnal.objects.aggregate(most_max=Max("order"))['most_max']
        else:
            _to_qs = StaticShagnal.objects.filter(id=to_id)
            if not _to_qs:
                ## warning bolgoh
                raise request.send_error("ERR_013")
            _to = _to_qs.first().order

        if not _from_qs:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from = _from_qs.first().order

        is_down = _from < _to
        _range = [_from, _to] if is_down else [_to, _from]

        changes = []

        qs = StaticShagnal.objects.filter(id=from_id, order=_from)
        if qs:
            qs.update(order=_to)
            changes.append([_from, _to, from_id])
            datas = StaticShagnal.objects.filter(order__range=_range).exclude(id=from_id).order_by('order')
            for item in datas:
                start = item.order
                item.order = item.order - 1 if is_down else item.order + 1
                end = item.order
                changes.append([start, end, item.id])
                item.save()
        else:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        return request.send_rsp("INF_002", changes)


class DynamicShagnalApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/shagnal/org/index.html'

    queryset = Shagnal.objects
    serializer_class = DynamicShagnalFormSerializer

    def get_response(self, serializer, pk=None):
        return Response(
            {
                "serializer": serializer,
                "pk": pk
            }
        )

    @login_required()
    @has_permission(allowed_permissions=['dynamic-shagnal-read'])
    def get(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk, **Shagnal.get_filter(request))
            serializer = self.serializer_class(instance=qs)
            return self.get_response(serializer, pk)

        serializer = self.serializer_class()

        return self.get_response(serializer)

    @login_required(is_superuser=False)
    @has_permission(allowed_permissions=['dynamic-shagnal-create', 'dynamic-shagnal-edit'])
    def post(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk, **Shagnal.get_filter(request))
            serializer = self.serializer_class(instance=qs, data=request.data, context={ "filters": Shagnal.get_filter(request) })
            if serializer.is_valid():
                serializer.save()
                request.send_message("success", 'INF_001')
            return redirect("dynamic-shagnal")

        serializer = self.serializer_class(data=request.data, context={ "filters": Shagnal.get_filter(request), "request": request })
        if serializer.is_valid():
            serializer.save()
            request.send_message("success", 'INF_002')
        return redirect("dynamic-shagnal")


class DynamicShagnalListApiView(APIView):

    @login_required()
    @has_permission(allowed_permissions=['dynamic-shagnal-read'])
    def get(self, request):
        static_shagnals = Shagnal.objects.filter(**Shagnal.get_filter(request)).values("id", 'name', 'order').order_by("order")
        return request.send_data(static_shagnals)


class DynamicShagnalDeleteApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = Shagnal.objects
    serializer_class = DynamicShagnalFormSerializer

    @login_required()
    @has_permission(allowed_permissions=['dynamic-shagnal-delete'])
    def get(self, request, pk):

        self.queryset = self.queryset.filter(**Shagnal.get_filter(request))
        self.destroy(request)
        request.send_message("success", 'INF_003')

        return redirect("dynamic-shagnal")


class DynamicShagnalChangeOrder(APIView):

    @login_required()
    @has_permission(allowed_permissions=['dynamic-shagnal-edit'])
    @transaction.atomic()
    def put(self, request):

        from_id = request.data.get("from_id")
        to_id = request.data.get("to_id")

        if not from_id:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from_qs = Shagnal.objects.filter(id=from_id, **Shagnal.get_filter(request))
        #  фронтоос хамгийн доор байрлуулахад id ирэхгүй байгаа учраас түүнийг хайж олох нь
        if not to_id:
            _to = Shagnal.objects.filter(**Shagnal.get_filter(request)).aggregate(most_max=Max("order"))['most_max']
        else:
            _to_qs = Shagnal.objects.filter(id=to_id, **Shagnal.get_filter(request))
            if not _to_qs:
                ## warning bolgoh
                raise request.send_error("ERR_013")
            _to = _to_qs.first().order

        if not _from_qs:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from = _from_qs.first().order

        is_down = _from < _to
        _range = [_from, _to] if is_down else [_to, _from]

        changes = []

        qs = Shagnal.objects.filter(id=from_id, order=_from, **Shagnal.get_filter(request))
        if qs:
            qs.update(order=_to)
            changes.append([_from, _to, from_id])
            datas = Shagnal.objects.filter(order__range=_range, **Shagnal.get_filter(request)).exclude(id=from_id).order_by('order')
            for item in datas:
                if item.id == from_id:
                    continue
                start = item.order
                item.order = item.order - 1 if is_down else item.order + 1
                end = item.order
                changes.append([start, end, item.id])
                item.save()
        else:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        return request.send_rsp("INF_002", changes)


class ShagnalToEmployeeAPiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/shagnal/index.html'

    @login_required()
    @has_permission(allowed_permissions=['shagnal-set-read'])
    def get(self, request):

        shagnals = Shagnal.objects.filter(**Shagnal.get_filter(request)).annotate(kind=Value(ShagnalEmployee.KIND_DYNAMIC, output_field=IntegerField())).order_by("-order")
        static_shagnals = StaticShagnal.objects.annotate(kind=Value(ShagnalEmployee.KIND_STATIC, output_field=IntegerField())).order_by("-order")

        static_data = ShagnalEmployeeListSerializer(static_shagnals, many=True).data
        data = ShagnalEmployeeListSerializer(shagnals, many=True).data

        static_data = data + static_data

        return Response({
            "shagnals": static_data,
        })


class ShagnalToEmployeeFormAPiView(
    generics.GenericAPIView,
    mixins.CreateModelMixin
):

    queryset = ShagnalEmployee
    serializer_class = ShagnalEmployeeFormSerializer

    @login_required()
    @has_permission(allowed_permissions=['shagnal-set-create'])
    @transaction.atomic()
    def post(self, request):

        body = request.data
        shagnal_id = body.get("shagnal_id")
        Model = None
        get_key = None

        if body.get('kind') == ShagnalEmployee.KIND_STATIC:
            body['static_shagnal'] = shagnal_id
            Model = StaticShagnal
            get_key = 'static_shagnal'

        if body.get('kind') == ShagnalEmployee.KIND_DYNAMIC:
            body['shagnal'] = shagnal_id
            Model = Shagnal
            get_key = 'shagnal'

        employee = Employee.objects.get(id=request.data['employee'])
        body['user'] = employee.user.id

        del body["shagnal_id"]
        body['created_by'] = request.employee.pk

        org_filter = dict()
        for _key in request.exactly_org_filter:
            org_filter[_key] = request.exactly_org_filter[_key]
            if request.exactly_org_filter[_key]:
                org_filter[_key] = request.exactly_org_filter[_key].pk

        body.update(org_filter)
        data = self.create(request).data
        obj = Model.objects.get(id=data[get_key])
        setattr(obj, 'kind', body.get('kind'))
        data = ShagnalEmployeeListSerializer(obj, many=False).data
        return request.send_rsp('INF_001', data)


class ShagnalTailanHTML(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/report/shagnal-report.html'
    def get(self, request):
        return Response({})


class ShagnalTailanApiView(APIView):

    def get(self, request):

        employee_user_ids = Employee.objects.filter(**request.exactly_org_filter).values_list("user_id", flat=True)

        filters = Q()
        filters.add(Q(**request.exactly_org_filter, kind=ShagnalEmployee.KIND_DYNAMIC), Q.AND)
        filters.add(Q(kind=ShagnalEmployee.KIND_STATIC, user_id__in=employee_user_ids), Q.OR)

        qs = ShagnalEmployee.objects.filter(filters)
        serializer = ShagnalTailanSerializer(instance=qs, many=True).data
        return request.send_data(serializer)


class ShagnalList(APIView):
    def get(self, request):
        static_shagnals = StaticShagnal.objects.all().values("id", 'name', 'order').order_by("order")
        dynamic_shagnals = Shagnal.objects.filter(**Shagnal.get_filter(request)).values("id", 'name', 'order').order_by("order")
        return request.send_data({"static": static_shagnals, "dynamic": dynamic_shagnals})
