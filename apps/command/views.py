
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from rest_framework import mixins
from rest_framework import generics

from django.db import transaction
from django.db.models import F, Value, CharField, Func ,Q
from django.conf import settings

from core.models import Command, EmployeeMigrations
from core.models import Employee
from core.models import Attachments
from core.fns import WithChoices

from .serializer import CommandSerializer
from .serializer import AttachmentSerializer
from .serializer import CommandDisplaySerializer
from .serializer import CommandAttachsSerializer
from .serializer import CommandPaginationSerializer

from main.decorators import login_required
from main.utils.datatable import data_table
from main.decorators import has_permission
from main.utils.file import remove_file


class CommandPaginationViews(APIView):

    @login_required()
    @has_permission(must_permissions=['command-read'])
    def get(self, request, types):

        filters = Q(**request.org_filter) & Q(Q(employees=request.employee.id) | Q(unit=Command.UNIT_ALL) | Q(unit=Command.UNIT_SELF))

        if types == 'all':
            filters = Q(**request.org_filter) | Q(org=request.org_filter['org'].id, sub_org=None, salbar=None)

        qs = Command.objects\
            .filter(
                filters
            )\
            .annotate(
                unit_name=WithChoices(Command.UNIT_CHOICES, 'unit'),
                formated_created_at=Func(
                    F('created_at'),
                    Value('YYYY-MM-DD'),
                    function='to_char',
                    output_field=CharField()
                )
            )

        paginated = data_table(qs, request)
        paginated['data'] = CommandPaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class CommandPageAPIView(APIView):
    """ Ажилчидын жагсаалт хуудас """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/command/command-page.html'

    @login_required()
    @has_permission(must_permissions=['command-read'])
    def get(self, request):

        employees = Employee.objects.filter(**request.org_filter, state=Employee.STATE_WORKING).order_by("user__userinfo__first_name")
        commanders = Employee.exactly_our_employees(request).filter(org_position__is_director=True)

        return Response({
            "units": Command.UNIT_CHOICES,
            "employees": employees,
            "commanders": commanders
        })


class CommandCreateEditApiView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):

    queryset = Command.objects
    serializer_class = CommandSerializer

    def get(self, request, pk):

        command = self.queryset.get(pk=pk)
        data = CommandDisplaySerializer(command, many=False).data

        return request.send_data(data)

    def get_add_attachments(self, request, files):
        attachment_ids = list()

        for _file in request.FILES.getlist('attachments'):
            attachemnt = AttachmentSerializer(data={ "file": _file, "org": request.exactly_org_filter.get("org").id }, many=False)
            attachemnt.is_valid()
            attachemnt.save()
            files.append(attachemnt.data)
            attachment_ids.append(str(attachemnt.data.get("id")))

        return attachment_ids

    def set_orgs_and_more(self, request):
        if "org" in request.org_filter:
            request.data['org'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter and request.data['unit'] != Command.UNIT_ALL:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter and request.data['unit'] != Command.UNIT_ALL:
            request.data['salbar'] = request.org_filter['salbar'].id

        request.data['created_by'] = request.employee.id


    @login_required()
    @has_permission(must_permissions=['command-create'])
    def post(self, request):

        command = Command.objects.filter( **request.org_filter, command_number=request.data['command_number'])

        if command:
            return request.send_warning("WRN_009", [], "тушаалын дугаар")

        with transaction.atomic():
            request.data._mutable = True

            files = []
            try:
                attachment_ids = self.get_add_attachments(request, files)
                request.data.setlist('attachments', attachment_ids)

                self.set_orgs_and_more(request=request)

                self.create(request).data

            except ValidationError as e:
                return request.send_error_valid(dict(e.__dict__['detail']))

            except Exception as e:
                for _file in files:
                    zam = str(settings.BASE_DIR) + _file.get('file')
                    remove_file(zam)
                raise e
            request.data._mutable = False

            return request.send_info("INF_001")

    # @login_required()
    # @has_permission(must_permissions=['command-update'])
    # def put(self, request, pk):

    #     with transaction.atomic():
    #         files = []

    #         try:
    #             request.data._mutable = True
    #             remove_attachment_ids = list(json.loads(request.data.get("removed_attachments")))
    #             remove_att_qs = Attachments.objects.filter(id__in=remove_attachment_ids)

    #             cart = Command.objects.get(pk=pk)
    #             objects = list(cart.attachments.all().values_list("id", flat=True))

    #             attachment_ids = self.get_add_attachments(request, files)
    #             request.data.setlist("attachments", [])

    #             self.set_orgs_and_more(request=request)

    #             self.update(request, pk).data

    #             obj = self.queryset.get(pk=pk)
    #             obj.attachments.set(attachment_ids + list(objects))

    #             for obj in remove_att_qs:
    #                 remove_file(obj.file.path)
    #                 obj.delete()

    #             request.data._mutable = False

    #         except Exception as e:
    #             for _file in files:
    #                 zam = str(settings.BASE_DIR) + _file.get('file')
    #                 remove_file(zam)
    #                 obj.delete()
    #             raise request.send_error("ERR_004")

    #         return request.send_info("INF_002")


class CommandDeleteApiView(APIView):

    @login_required()
    @has_permission(must_permissions=['command-delete'])
    def delete(self,request, pk):

        command = Command.objects.filter(pk=pk).first()

        employee_migrations = EmployeeMigrations.objects.filter(command_id=command.id)
        if employee_migrations:
            return request.send_warning("WRN_011")

        command.delete()
        return request.send_info("INF_003")


class CommandAttachMents(APIView):
    def get(self, request, pk):
        obj = Command.objects.get(id=pk)
        serializer = CommandAttachsSerializer(instance=obj)
        return request.send_data(serializer.data)
