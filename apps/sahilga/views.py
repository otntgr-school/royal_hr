from datetime import datetime as datet

from django.db import transaction
from django.conf import settings
from django.db.models import Count
from django.db.models import F
from django.db.models import Q

from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from core.models import (
    Employee,
    Sahilga,
    UserInfo,
)

from .serializer import SahilgaActionSerializer, SahilgaReadOneEmpSerializer
from .serializer import EmployeeSahilgaSerializer
from .serializer import SahilgaGETSerializer
from worker.serializer import AttachmentSerializer

from main.decorators import login_required
from main.decorators import has_permission
from main.utils.file import remove_file
from main.utils.datatable import data_table


class SahilgaApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/sahilga/index.html'

    def get(self, request):
        return Response({
            "states": Sahilga.STATE_CHOICES
        })


class SahilgaListApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin
):

    @login_required()
    @has_permission(allowed_permissions=['sahilga-read'])
    def get(self, request, pk=None):
        """ Сахилга ажилчидыг хэдэн удаа авснаар нь буцаана """
        if pk:
            sahilga = Sahilga \
                .objects \
                .filter(pk=pk) \
                .first()

            if not sahilga:
                raise request.send_error("ERR_013")

            data = SahilgaGETSerializer(sahilga, many=False).data
            return request.send_data(data)

        filters = {
            **request.org_filter,
            "employee__user__userinfo__action_status": UserInfo.APPROVED,
            "employee__user__userinfo__action_status_type": UserInfo.ACTION_TYPE_ALL
        }


        if not request.employee.is_hr:
            filters.update(
                {
                    "employee": request.employee,
                }
            )

        qs = Sahilga \
                .objects \
                .filter(**filters) \
                .values("employee") \
                .annotate(
                    first_name=F("employee__user__userinfo__first_name"),
                    last_name=F("employee__user__userinfo__last_name"),
                    count=Count("employee", filter=Q(state=Sahilga.STATE_ACTIVE)),
                ) \
                .values("employee", 'count', 'first_name', 'last_name', 'employee_id')
        paginated = data_table(qs, request)
        return Response(paginated)


class SahilgaActionApiView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
):

    queryset = Sahilga.objects
    serializer_class = SahilgaActionSerializer

    def get_add_attachments(self, request, files):
        attachment_ids = list()

        for _file in request.FILES.getlist('attachments'):
            attachemnt = AttachmentSerializer(data={ "file": _file, "org": request.exactly_org_filter.get("org").id }, many=False)
            attachemnt.is_valid()
            attachemnt.save()
            files.append(attachemnt.data)
            attachment_ids.append(str(attachemnt.data.get("id")))

        return attachment_ids

    @login_required()
    @has_permission(allowed_permissions=['sahilga-create'])
    def post(self, request):
        with transaction.atomic():

            files = []
            try:
                ##  Өргөдөл гомдол учраас дандаа ажилтнаас ирнэ гэж үзсэн
                request.data._mutable = True
                attachment_ids = self.get_add_attachments(request, files)

                request.data['org'] = request.exactly_org_filter.get('org').pk if request.exactly_org_filter.get('org') else None
                request.data['sub_org'] = request.exactly_org_filter.get('sub_org').pk if request.exactly_org_filter.get('sub_org') else None
                request.data['salbar'] = request.exactly_org_filter.get('salbar').pk if request.exactly_org_filter.get('salbar') else None
                request.data['created_by'] = request.employee.pk

                request.data.setlist('attachments', attachment_ids)
                request.data._mutable = False

                self.create(request)
            except Exception as e:
                for _file in files:
                    zam = str(settings.BASE_DIR) + _file.get('file')
                    remove_file(zam)

                raise e

        return request.send_info("INF_001")


class SahilgaEmployeeApiView(APIView):

    @login_required()
    @has_permission(allowed_permissions=['sahilga-read'])
    def get(self, request, employee_id):

        state = request.GET.get("state")
        if not state:
            state = Sahilga.STATE_ACTIVE

        if employee_id == 0:
            return Response([])

        filters = {
            **request.org_filter,
            "employee_id": employee_id,
            "state": state,
        }

        qs = Sahilga.objects.filter(**filters)
        paginated = data_table(qs, request)
        paginated['data'] = EmployeeSahilgaSerializer(paginated['data'], many=True).data
        return Response(paginated)

    @login_required()
    @has_permission(allowed_permissions=['sahilga-refuse', 'sahilga-reset', 'sahilga-update'])
    @transaction.atomic()
    def delete(self, request, pk, state):

        if state not in ['refuse', 'reset']:
            raise request.send_error("ERR_013")
        if not pk:
            raise request.send_error("ERR_013")

        sahilga = Sahilga.objects.filter(pk=pk).first()
        if not sahilga:
            raise request.send_error("ERR_013")

        #  Цуцлах үед
        if state == 'refuse':
            sahilga.deleted_at = datet.now()
            sahilga.deleted_by = request.employee
            sahilga.state = Sahilga.STATE_REFUSED
        #  Сэргээх үед
        if state == 'reset':
            sahilga.deleted_at = None
            sahilga.deleted_by = None
            sahilga.state = Sahilga.STATE_ACTIVE

        sahilga.save()

        return request.send_info("INF_003")


class SahilgaOneApiView(APIView):
    def get(self, request):
        emp = request.employee
        user_id = request.GET.get("userId")

        if user_id:
            emp = Employee.objects.filter(user_id=user_id, **request.org_filter).order_by('date_joined').last()

        qs = Sahilga.objects.filter(employee_id=emp.id)
        paginated = data_table(qs, request)
        paginated['data'] = SahilgaReadOneEmpSerializer(paginated['data'], many=True).data
        return Response(paginated)
