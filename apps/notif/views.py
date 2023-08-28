import uuid

from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework import mixins
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import (
    NotificationState,
    Notification,
    NotificationType,
    Orgs,
    SubOrgs,
    OrgPosition,
)

from core.managers import SalbarManager

from .serializer import (
    SubOrgJsonSerializer,
    OrgPositionJsonSerializer,
    OrgSerializer,
    UserSerializer,
    User,
    NotificationListSerializer,
    NotifTypeListSerializer,
    NotifTypeFormSerializer,
)

from core.serializer import OrgToEmployeeSerializer
from main.decorators import has_permission, login_required


class NotifListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/notif/index.html'

    @login_required()
    def get(self, request):
        return Response({})


class NotifCreteView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/notif/create.html'

    @login_required()
    def get(self, request):
        ntypes = NotificationType.objects.all().order_by("level")
        from_kind_choices = Notification.FROM_KIND_CHOICES
        scope_kind_choices = Notification.SCOPE_KIND_CHOICES
        return Response(
            {
                "ntypes": ntypes,
                "from_kind_choices": from_kind_choices,
                "scope_kind_choices": scope_kind_choices,
            }
        )


class NotificationAPIView(APIView):

    @login_required()
    def get(self, request):

        count = int(request.GET.get('count'))

        skip = 0 + (count * 6)
        limit = 6 * (count + 1)

        filters = Notification.get_filters(request)
        qs = Notification.objects.filter(filters).order_by("-created_at")[skip: limit]
        notifs = NotificationListSerializer(instance=qs, many=True, context={ "request": request }).data

        notif_state_qs = NotificationState.objects.filter(user=request.user, notif_id__in=qs.values_list('id'))

        data = {
            "notifs": notifs,
            "read_notifs": notif_state_qs.values_list("notif_id", flat=True)
        }

        return request.send_data(data)

    @login_required()
    @has_permission(allowed_permissions=['notif-action-create'])
    def post(self, request):

        body = request.data

        Notification.objects.create_notif(request, **body)

        return request.send_info("INF_001")


class NotifInfoApiView(APIView):
    def get(self, request):
        filters = Notification.get_filters(request)

        qs = Notification.objects.filter(filters)
        notif_state_qs = NotificationState.objects.filter(user=request.user, notif_id__in=qs.values_list('id'))

        all_count = qs.count()
        read_count = notif_state_qs.count()

        new_count = all_count - read_count

        data = {
            "new_count": new_count,
        }

        return request.send_data(data)


class NotifKindsApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
):

    queryset = SubOrgs.objects
    serializer_class = SubOrgJsonSerializer

    @login_required()
    def get(self, request, kind):
        """ Зөвхөн байгууллага доторх media файлуудаа харж болно """

        filters = dict()

        if kind == Notification.SCOPE_KIND_SUBORG:
            if request.user.is_superuser:
                self.queryset = Orgs.objects.all()
                self.serializer_class = OrgSerializer
            elif request.exactly_org_filter.get("sub_org"):
                filters['id'] = request.exactly_org_filter.get("sub_org").pk
                self.queryset = self.queryset.filter(**filters)

        elif kind == Notification.SCOPE_KIND_SALBAR:
            _filters = SalbarManager.get_filters(request)
            if _filters.get("sub_orgs"):
                self.queryset = self.queryset.filter(id=_filters.get("sub_orgs").pk)
            else:
                self.queryset = SubOrgs.objects.filter(org=request.org_filter.get("org"))
                self.serializer_class = SubOrgJsonSerializer

        elif kind == Notification.SCOPE_KIND_POS:
            self.queryset = OrgPosition.objects.filter(org=request.exactly_org_filter.get("org"))
            self.serializer_class = OrgPositionJsonSerializer

        elif kind == Notification.SCOPE_KIND_EMPLOYEE:
            self.serializer_class = OrgToEmployeeSerializer
            self.queryset = Orgs.objects.filter(id=request.org_filter.get("org").id)

        elif kind == Notification.SCOPE_KIND_USER:
            self.serializer_class = UserSerializer
            self.queryset = User.objects.all()

        elif kind == Notification.SCOPE_KIND_ORG:
            self.serializer_class = OrgSerializer
            if request.user.is_superuser:
                self.queryset = Orgs.objects.all()
            else:
                self.queryset = Orgs.objects.filter(id=request.org_filter.get("org").id)

        data = self.list(request).data
        return request.send_data(data)


class NotifChangeStateApiView(APIView):

    @login_required()
    def get(self, request, pk):

        if pk == "all":

            filters = Notification.get_filters(request)
            not_read_notif_ids = Notification.objects.filter(filters).exclude(notificationstate__user=request.user).values_list("id", flat=True)

            states = list()
            for not_id in not_read_notif_ids:
                states.append(
                    NotificationState(
                        notif_id=not_id,
                        user=request.user
                    )
                )

            if states:
                NotificationState.objects.bulk_create(states)
            return request.send_data(True)

        else:
            NotificationState.objects.create(user=request.user, notif_id=pk)
            return request.send_data(True)


class NotifTypeView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/notif/type/index.html'

    queryset = NotificationType.objects
    serializer_class = NotifTypeFormSerializer

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


class NotifTypeListApiView(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):

    queryset = NotificationType.objects
    serializer_class = NotifTypeListSerializer

    @login_required(is_superuser=True)
    def get(self, request):
        self.queryset = self.queryset.order_by("level")

        rsp = self.list(request)
        rsp.data.append(
            {
                "text": "Шинээр үүсгэх",
                "a_attr": {
                    "href": reverse("notif-type")
                },
                "icon": 'fa fa-folder-plus'
            }
        )
        return rsp


class NotifTypeDeleteApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = NotificationType.objects
    serializer_class = NotifTypeListSerializer

    @login_required(is_superuser=True)
    def get(self, request, pk):

        self.destroy(request)
        request.send_message("success", 'INF_003')

        return redirect("notif-type")
