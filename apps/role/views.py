from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import F
from django.db.models import CharField
from django.db.models.functions import Cast
from django.db import transaction

from rest_framework.views import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins

from core.models import AlbanTushaalBatalgaajuulalt
from core.models import AlbanTushaalShaardlaga
from core.models import AlbanTushaalSubject
from core.models import AlbanTushaaliinTodGeneral
from core.models import AlbanTushaaliinTodZorilgo
from core.models import AlbanTushaaliinTodorhoilolt
from core.models import AlbanTushaaliinZorilt
from core.models import AlbanTushaaliinZoriltiinVvreg
from core.models import Roles
from core.models import User
from core.models import Permissions
from core.models import OrgPosition
from core.models import Employee
from core.models import MainPosition

from .serializer import AlbanTushaalBatalgaajuulaltSerializer
from .serializer import AlbanTushaalShaardlagaSerializer
from .serializer import AlbanTushaalTodorhoiloltGetSerializer
from .serializer import AlbanTushaalTodorhoiloltSerializer
from .serializer import AlbanTushaalYeronhiiMedeelelSerializer
from .serializer import AlbanTushaaliinChigVvergSerializer
from .serializer import AlbanTushaaliinSubjectSerializer
from .serializer import AlbanTushaaliinZorilgoSerializer
from .serializer import AlbanTushaaliinZorilgoZoriltSerializer
from .serializer import RoleSerializer
from .serializer import PermissionsActionSerializer
from .serializer import OrgPositionSerializer
from .serializer import PositionsTreeSerializer
from .serializer import RolePaginationSerializer
from .serializer import PermPaginationSerializer

from main.utils.datatable import data_table
from main.decorators import login_required
from main.decorators import has_permission


class RoleListApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/role/index.html'

    queryset = Roles.objects
    serializer_class = RoleSerializer

    @login_required(is_superuser=True)
    def get(self, request):
        return Response({
            "serializer": self.serializer_class
        })


class RolePaginationApiView(APIView):

    @login_required(is_superuser=True)
    def get(self, request):
        qs = Roles.objects.all()
        paginated = data_table(qs, request)
        paginated['data'] = RolePaginationSerializer(paginated['data'], many=True).data
        return Response(paginated)


class PermPaginationApiView(APIView):

    @login_required(is_superuser=True)
    def get(self, request):
        qs = Permissions.objects.all()
        paginated = data_table(qs, request)
        paginated['data'] = PermPaginationSerializer(paginated['data'], many=True).data
        return Response(paginated)


# Create your views here.
class HomeApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/role/form.html'

    queryset = Roles.objects
    serializer_class = RoleSerializer

    @login_required(is_superuser=True)
    def get(self, request, pk=None):

        if pk:
            self.queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=self.queryset, many=False)
            return Response({ 'serializer': serializer, "pk": pk })

        serializer = self.serializer_class()

        return Response({
            'serializer': serializer,
        })

    @login_required(is_superuser=True)
    def post(self, request, pk=None):

        if pk:
            instance = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=instance, data=request.data)
            if not serializer.is_valid():
                return Response({ 'serializer': serializer, 'pk': pk })

        else:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response({ 'serializer': serializer })

        serializer.save()
        return redirect('role')


class PermissionApiView(APIView):
    """ Эрхүүдийн жагсаалт """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/role/permission/index.html'

    @login_required(is_superuser=True)
    def get(self, request):
        return Response()


class PermissionActionApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/role/permission/form.html'

    queryset = Permissions.objects
    serializer_class = PermissionsActionSerializer

    redirect_name = "permission-list"

    @login_required(is_superuser=True)
    def get(self, request, pk=None):
        if pk:
            self.queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=self.queryset, many=False)
            return Response({ 'serializer': serializer, "pk": pk })

        serializer = self.serializer_class()
        return Response({ 'serializer': serializer })

    @login_required(is_superuser=True)
    def post(self, request, pk=None):

        if pk:
            instance = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=instance, data=request.data)
            if not serializer.is_valid():
                return Response({ 'serializer': serializer, 'pk': pk })

        else:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response({ 'serializer': serializer })

        serializer.save()
        return redirect(self.redirect_name)


class PositionDeleteApiView(APIView):

    def get(self, request, pk):
        OrgPosition.objects.filter(pk=pk).delete()
        request.send_message("success", "INF_003")
        return redirect("position-action")


class PositionsTreeApiView(
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
        rsp.data.append(
            {
                "text": "Шинээр үүсгэх",
                "a_attr": {
                    "href": reverse("position-action")
                },
                "icon": 'fa fa-folder-plus'
            }
        )
        return rsp


class PositionActionApiView(APIView):
    """ Байгууллагадаа албан тушаал үүсгэх """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/position/index.html'

    queryset = OrgPosition.objects
    serializer_class = OrgPositionSerializer

    redirect_name = "position-action"

    @login_required()
    @has_permission(must_permissions=['appointment-read'])
    def get(self, request, pk=None):
        employees = Employee.objects.filter(**request.org_filter, state = Employee.STATE_WORKING).order_by("id")

        main_positions = MainPosition.objects.all().values('name', 'id')

        if pk:
            self.queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=self.queryset, many=False)

            # has_pos_employees = list(employees.filter(org_position_id=pk).values_list("id", flat=True))

            return Response({
                    'serializer': serializer,
                    "pk": pk,
                    "employees": employees,
                    'main_positions': main_positions
                    # "has_pos_employee": has_pos_employees,
                })

        serializer = self.serializer_class()
        return Response({
            'serializer': serializer,
            "employees": employees,
            'main_positions': main_positions
        })

    def set_pos_to_employee(self, request, pos_id):
        """ Тухайн албан тушаалыг хүмүүсд оноож өгөх нь """

        old_pos_employees = set(
            Employee
                .objects
                .filter(**request.org_filter, org_position_id=pos_id)
                .annotate(sid=Cast("id", CharField()))
                .values_list("sid", flat=True)
        )
        employees = set(request.data.getlist("employee"))
        removed_emps = list(old_pos_employees.difference(employees))
        new_emps = list(employees.difference(old_pos_employees))

        if new_emps:
            Employee \
                .objects \
                .filter(id__in=new_emps) \
                .update(
                    org_position_id=pos_id
                )

        if removed_emps:
            Employee \
                .objects \
                .filter(id__in=removed_emps) \
                .update(
                    org_position_id=None
                )

    @login_required()
    @has_permission(allowed_permissions=['appointment-create', 'appointment-update'])
    def post(self, request, pk=None):

        if pk:
            instance = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=instance, data=request.data, context={ "org": request.org_filter['org'], "main_position": request.data['main_position'], "removed_perms": request.data.getlist("removed_perms") })
            if not serializer.is_valid():
                return Response({ 'serializer': serializer, 'pk': pk })

        else:
            serializer = self.serializer_class(data=request.data, context={ "org": request.org_filter['org'], "main_position": request.data['main_position'] })
            if not serializer.is_valid():
                return Response({ 'serializer': serializer })

        position = serializer.save()

        if not pk:
            self.set_pos_to_employee(request, pos_id=position.id)
        return redirect(self.redirect_name)


class GETRolePermsApiView(APIView):
    def post(self, request):
        role_ids = request.data.get("role_ids")
        pos_id = request.data.get("pos_id")
        perms = Roles.objects.filter(id__in=role_ids).values(cid=F("permissions__id"), cname=F('permissions__name'), cdesc=F('permissions__description'))

        removed_pos = list()
        if pos_id:
            pos = OrgPosition.objects.get(id=pos_id)
            removed_pos = pos.removed_perms.values_list('id', flat=True)

        return request.send_data({
            "perms": perms,
            "removed_pos": removed_pos
        })


class AlbaTushaalCRUDApiView(APIView):

    def get(self, request, pk):
        obj = AlbanTushaaliinTodorhoilolt.objects.filter(org_position_id=pk).first()
        serializer = AlbanTushaalTodorhoiloltGetSerializer(instance=obj)
        return request.send_data(serializer.data)

    def post(self, request, pk=None, format=None):
        with transaction.atomic():
            serializer_yeronhii = AlbanTushaalYeronhiiMedeelelSerializer(data=request.data)
            if serializer_yeronhii.is_valid():
                serializer_yeronhii.save()
            else:
                return request.send_error_valid(serializer_yeronhii.errors)

            serializer_zorilgo = AlbanTushaaliinZorilgoSerializer(data=request.data)
            if serializer_zorilgo.is_valid():
                serializer_zorilgo.save()
            else:
                return request.send_error_valid(serializer_zorilgo.errors)

            for zorilt in request.data['zorilt']:
                zorilt['zorilgo'] = serializer_zorilgo.data['id']
                serializer_zorilt = AlbanTushaaliinZorilgoZoriltSerializer(data=zorilt, context={'zorilt': zorilt})
                if serializer_zorilt.is_valid():
                    serializer_zorilt.save()
                else:
                    return request.send_error_valid(serializer_zorilt.errors)

            serializer_shaardlaga = AlbanTushaalShaardlagaSerializer(data=request.data)
            if serializer_shaardlaga.is_valid():
                serializer_shaardlaga.save()
            else:
                return request.send_error_valid(serializer_shaardlaga.errors)

            serializer_subject = AlbanTushaaliinSubjectSerializer(data=request.data)
            if serializer_subject.is_valid():
                serializer_subject.save()
            else:
                return request.send_error_valid(serializer_subject.errors)

            serializer_batalgaajuulalt = AlbanTushaalBatalgaajuulaltSerializer(data=request.data)
            if serializer_batalgaajuulalt.is_valid():
                serializer_batalgaajuulalt.save()
            else:
                return request.send_error_valid(serializer_batalgaajuulalt.errors)

            request.data['general'] = serializer_yeronhii.data['id']
            request.data['zorilgo_zorilt'] = serializer_zorilgo.data['id']
            request.data['shaardlaga'] = serializer_shaardlaga.data['id']
            request.data['subject'] = serializer_subject.data['id']
            request.data['batalgaajuulalt'] = serializer_batalgaajuulalt.data['id']

            if "org" in request.org_filter:
                request.data['org'] = request.org_filter['org'].id
                request.data['org_name'] = request.org_filter['org'].name
            if "sub_org" in request.org_filter:
                request.data['sub_org'] = request.org_filter['sub_org'].id
            if "salbar" in request.org_filter:
                request.data['salbar'] = request.org_filter['salbar'].id

            serializer = AlbanTushaalTodorhoiloltSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                request.send_message('success', 'INF_001')
                return request.send_info("INF_001")

            return request.send_error_valid(serializer.errors)

    def put(self, request, pk):
        with transaction.atomic():
            object_yeronhii = AlbanTushaaliinTodGeneral.objects.get(id=request.data['general_id'])
            serializer_yeronhii = AlbanTushaalYeronhiiMedeelelSerializer(instance=object_yeronhii, data=request.data)
            if serializer_yeronhii.is_valid():
                serializer_yeronhii.save()
            else:
                return request.send_error_valid(serializer_yeronhii.errors)

            object_zorilgo = AlbanTushaaliinTodZorilgo.objects.get(id=request.data['zorilgo_zorilt_id'])
            serializer_zorilgo = AlbanTushaaliinZorilgoSerializer(instance=object_zorilgo, data=request.data)
            if serializer_zorilgo.is_valid():
                serializer_zorilgo.save()
            else:
                return request.send_error_valid(serializer_zorilgo.errors)

            for zorilt in request.data['zorilt']:
                zorilt['zorilgo'] = serializer_zorilgo.data['id']
                if 'id' in zorilt:
                    object_zorilt = AlbanTushaaliinZorilt.objects.get(id=zorilt['id'])
                    serializer_zorilt = AlbanTushaaliinZorilgoZoriltSerializer(instance=object_zorilt, data=zorilt, context={'zorilt': zorilt})
                    if serializer_zorilt.is_valid():
                        serializer_zorilt.save()
                    else:
                        return request.send_error_valid(serializer_zorilt.errors)
                else:
                    serializer_zorilt = AlbanTushaaliinZorilgoZoriltSerializer(data=zorilt, context={'zorilt': zorilt})
                    if serializer_zorilt.is_valid():
                        serializer_zorilt.save()
                    else:
                        return request.send_error_valid(serializer_zorilt.errors)

            object_shaardlaga = AlbanTushaalShaardlaga(id=request.data['shaardlaga_id'])
            serializer_shaardlaga = AlbanTushaalShaardlagaSerializer(instance=object_shaardlaga, data=request.data)
            if serializer_shaardlaga.is_valid():
                serializer_shaardlaga.save()
            else:
                return request.send_error_valid(serializer_shaardlaga.errors)

            object_subject = AlbanTushaalSubject(id=request.data['subject_id'])
            serializer_subject = AlbanTushaaliinSubjectSerializer(instance=object_subject, data=request.data)
            if serializer_subject.is_valid():
                serializer_subject.save()
            else:
                return request.send_error_valid(serializer_subject.errors)

            object_batalgaajuulalt = AlbanTushaalBatalgaajuulalt(id=request.data['batalgaajuulalt_id'])
            serializer_batalgaajuulalt = AlbanTushaalBatalgaajuulaltSerializer(instance=object_batalgaajuulalt, data=request.data)
            if serializer_batalgaajuulalt.is_valid():
                serializer_batalgaajuulalt.save()
            else:
                return request.send_error_valid(serializer_batalgaajuulalt.errors)

            for deleted_chig_id in request.data['deleteList']['chig_vvreg']:
                object_chig = AlbanTushaaliinZoriltiinVvreg.objects.get(id=deleted_chig_id)
                object_chig.delete()

            for deleted_zorilt_id in request.data['deleteList']['zorilt']:
                object_zorilt = AlbanTushaaliinZorilt.objects.get(id=deleted_zorilt_id)
                object_zorilt.delete()

            request.data['general'] = serializer_yeronhii.data['id']
            request.data['zorilgo_zorilt'] = serializer_zorilgo.data['id']
            request.data['shaardlaga'] = serializer_shaardlaga.data['id']
            request.data['subject'] = serializer_subject.data['id']
            request.data['batalgaajuulalt'] = serializer_batalgaajuulalt.data['id']

            if "org" in request.org_filter:
                request.data['org'] = request.org_filter['org'].id
                request.data['org_name'] = request.org_filter['org'].name
            if "sub_org" in request.org_filter:
                request.data['sub_org'] = request.org_filter['sub_org'].id
            if "salbar" in request.org_filter:
                request.data['salbar'] = request.org_filter['salbar'].id

            object_todorhoilolt = AlbanTushaaliinTodorhoilolt.objects.get(org_position_id=pk)
            serializer = AlbanTushaalTodorhoiloltSerializer(instance=object_todorhoilolt, data=request.data)

            if serializer.is_valid():
                serializer.save()
                request.send_message('success', 'INF_002')
                return request.send_info("INF_002")

            return request.send_error_valid(serializer.errors)
