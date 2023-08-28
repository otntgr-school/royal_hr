from datetime import datetime as dt
import json

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction
from django.db.models import F

from rest_framework import mixins
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import (
    Attachments,
    Employee,
    Feedback,
    FeedbackKind,
    OrgPosition,
    Notification
)

from .serializer import FeedBackDecideGETSerializer
from .serializer import FeedbackGETAttachSerializer
from .serializer import FeedbackKindFormSerializer
from .serializer import FeedbackKindListSerializer
from .serializer import FeedbackDTSerializer
from .serializer import FeedbackFormSerializer
from .serializer import AttachmentsFormSerializer
from .serializer import FeedBackDecideListSerializer
from .serializer import FeedbackGETSerializer
from core.serializer import OrgToEmployeeOrgPositionJsonSerializer
from .serializer import FeedbackUPDATESerializer
from .serializer import FeedbackGETCommandshSerializer

from main.utils.datatable import data_table
from main.utils.file import remove_file
from main.decorators import login_required
from main.decorators import has_permission

from core.fns import WithChoices


class IndexAPIView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/sanal-gomdol/index.html'

    @login_required()
    def get(self, request):
        from_kinds = Feedback.FROM_KIND
        feedback_kinds = FeedbackKind.objects.filter(**request.exactly_org_filter).order_by('rank')

        employee_ids = list(Employee.objects.filter(**request.exactly_org_filter).values_list("id", flat=True))
        employees = OrgToEmployeeOrgPositionJsonSerializer(
            OrgPosition.objects.filter(org=request.org_filter.get("org")),
            many=True,
            context={
                "employee_ids": employee_ids
            }
        ).data

        return Response(
            {
                "from_kinds": from_kinds,
                "feedback_kinds": feedback_kinds,
                "to_employees": employees
            }
        )


class FeedbackKindApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/sanal-gomdol/kinds/index.html'

    queryset = FeedbackKind.objects
    serializer_class = FeedbackKindFormSerializer

    def get_response(self, serializer, pk=None):
        return Response(
            {
                "serializer": serializer,
                "pk": pk
            }
        )

    def get(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs)
            return self.get_response(serializer, pk)

        serializer = self.serializer_class()

        return self.get_response(serializer)

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


class FeedbackKindListApiView(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):

    queryset = FeedbackKind.objects
    serializer_class = FeedbackKindListSerializer

    def get(self, request):
        self.queryset = self.queryset \
                            .filter(**request.exactly_org_filter) \

        rsp = self.list(request)
        rsp.data.append(
            {
                "text": "Шинээр үүсгэх",
                "a_attr": {
                    "href": reverse("sanal-gomdol-turul")
                },
                "icon": 'fa fa-folder-plus'
            }
        )
        return rsp


class FeedbackKindDeleteApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = FeedbackKind.objects
    serializer_class = FeedbackKindListSerializer

    def get(self, request, pk):

        self.destroy(request)
        request.send_message("success", 'INF_003')

        return redirect("sanal-gomdol-turul")


class FeedBackDatatableAPIView(APIView):

    @login_required()
    def get(self, request, pk=None):

        qs = Feedback \
            .objects \
            .annotate(
                kind_name=F("kind__title"),
                state_name=WithChoices(Feedback.STATE_CHOICES, 'state')
            ) \
            .filter(from_employee=request.employee)

        if pk:
            obj = qs.get(pk=pk)
            data = FeedbackGETSerializer(obj, many=False).data
            return request.send_data(data)

        paginated = data_table(qs, request)
        paginated['data'] = FeedbackDTSerializer(paginated['data'], many=True).data
        return Response(paginated)


class FeedBackFormAPIView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):

    queryset = Feedback.objects
    serializer_class = FeedbackFormSerializer

    def get_add_attachments(self, request, files):
        attachment_ids = list()

        for _file in request.FILES.getlist('attachments'):
            attachemnt = AttachmentsFormSerializer(data={ "file": _file, "org": request.exactly_org_filter.get("org").id }, many=False)
            attachemnt.is_valid()
            attachemnt.save()
            files.append(attachemnt.data)
            attachment_ids.append(str(attachemnt.data.get("id")))

        return attachment_ids

    @login_required()
    def post(self, request):

        with transaction.atomic():

            files = []

            try:
                request.data._mutable = True

                # Хэрвээ хүний нөөцийн мэргэжилтэнг сонговол хүний нөөцийн ID-г хайж олно
                if request.data['to_employee_radio'] == 'for_hr':
                    employee_hr = Employee.objects.filter(
                        org__id=request.exactly_org_filter.get('org').pk if request.exactly_org_filter.get('org') else None,
                        sub_org__id=request.exactly_org_filter.get('sub_org').pk if request.exactly_org_filter.get('sub_org') else None,
                        salbar__id=request.exactly_org_filter.get('salbar').pk if request.exactly_org_filter.get('salbar') else None,
                        org_position__is_hr=True,
                        state=Employee.STATE_WORKING
                    ).first()

                    if not employee_hr:
                        return request.send_error("ERR_021")

                    request.data['to_employees'] = employee_hr.id

                ##  Өргөдөл гомдол учраас дандаа ажилтнаас ирнэ гэж үзсэн
                attachment_ids = self.get_add_attachments(request, files)

                request.data['from_employee_kind'] = Feedback.FROM_KIND_EMPLOYEE
                request.data['from_employee'] = request.employee.pk

                request.data['org'] = request.exactly_org_filter.get('org').pk if request.exactly_org_filter.get('org') else None
                request.data['sub_org'] = request.exactly_org_filter.get('sub_org').pk if request.exactly_org_filter.get('sub_org') else None
                request.data['salbar'] = request.exactly_org_filter.get('salbar').pk if request.exactly_org_filter.get('salbar') else None

                if request.data.get('up_org_checkbox'):

                    up_org = request.data['up_orgs']
                    if up_org:
                        _id, _lvl = up_org.split("-")

                        if _lvl == 'org':
                            request.data['org'] = _id
                            request.data['sub_org'] = None
                            request.data['salbar'] = None

                        elif _lvl == 'sub_org':
                            request.data['sub_org'] = _id
                            request.data['salbar'] = None

                        elif _lvl == 'salbar':
                            request.data['salbar'] = _id


                request.data.setlist('attachments', attachment_ids)
                request.data._mutable = False

                data = self.create(request).data

                if data.get('to_employees'):
                    notification_body = {
                        'title': f'Танд {data.get("kind_name").lower()} {data.get("state_name").lower()}.',
                        'content': f'Танд {data.get("kind_name").lower()} {data.get("state_name").lower()}.',
                        'ntype': 'normal',
                        'url': reverse("my-feedback-decide"),
                        'scope_kind': Notification.SCOPE_KIND_EMPLOYEE,
                        'from_kind': Notification.FROM_KIND_EMPLOYEE,
                        'scope_ids': [ data['to_employees'] ]
                    }

                else:
                    notification_body = {
                        'title': f'Танд {data.get("kind_name").lower()} {data.get("state_name").lower()}.',
                        'content': f'Танд {data.get("kind_name").lower()} {data.get("state_name").lower()}.',
                        'ntype': 'normal',
                        'url': reverse("sanal-gomdol-decide"),
                        'scope_kind': Notification.SCOPE_KIND_POS,
                        'from_kind': Notification.FROM_KIND_EMPLOYEE,
                        'scope_ids': list(OrgPosition.objects.filter(org=request.data['org'], is_hr=True).values_list("id", flat=True))
                    }
                Notification.objects.create_notif(request, **notification_body)

            except Exception as e:
                for _file in files:
                    zam = str(settings.BASE_DIR) + _file.get('file')
                    remove_file(zam)
                raise e

        return request.send_rsp("INF_001", data)

    @login_required()
    def put(self, request, pk):

        with transaction.atomic():

            files = []

            try:
                ##  Өргөдөл гомдол учраас дандаа ажилтнаас ирнэ гэж үзсэн
                request.data._mutable = True
                remove_attachment_ids = list(json.loads(request.data.get("removed_attachments")))
                remove_att_qs = Attachments.objects.filter(id__in=remove_attachment_ids)

                obj = Feedback.objects.filter(pk=pk).first()
                if obj:
                    raise request.send_error("INF_013")
                old_att_ids = list(obj.attachments.values_list("id", flat=True))

                attachment_ids = self.get_add_attachments(request, files)
                request.data.setlist("attachments", [])
                request.data._mutable = False

                data = self.update(request, pk).data
                obj = self.queryset.get(pk=pk)

                obj.attachments.set(attachment_ids + old_att_ids)
                for obj in remove_att_qs:
                    remove_file(obj.file.path)
                    obj.delete()

            except Exception as e:
                for _file in files:
                    zam = str(settings.BASE_DIR) + _file.get('file')
                    remove_file(zam)
                raise e

        return request.send_rsp("INF_002", data)

    @login_required()
    def delete(self, request, pk):
        """ Өөрийн өргөдөл гомдлоо цуцлах нь """

        is_updated = self.queryset \
            .filter(
                pk=pk,
                state=Feedback.STATE_NEW,
            ) \
            .update(
                state=Feedback.STATE_CANCELED,
                decided_employee=request.employee,
                decided_at=dt.now()
            )

        if not is_updated:
            return request.send_error("ERR_013")

        return request.send_info("INF_003")


class FeedBackDecideAPIView(APIView):
    """
        Заавал хүний нөөцийн мэргжилтэй хүн биш энэ хуудасны эрх нь байвал
        хүсэлтүүдийг шийдвэрлэдэг маягаар хийлээ
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/sanal-gomdol/decide/index.html'

    @login_required()
    @has_permission(must_permissions=['sanal-gomdol-decide-read'])
    def get(self, request):

        kinds = FeedbackKind.objects.filter(**request.exactly_org_filter)

        return Response(
            {
                "states": Feedback.STATE_CHOICES,
                "kinds": kinds,
                "is_my": ""
            }
        )


class MyFeedBackDecideAPIView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/sanal-gomdol/decide/index.html'

    @login_required()
    def get(self, request):

        kinds = FeedbackKind.objects.filter(**request.exactly_org_filter)

        return Response(
            {
                "states": Feedback.STATE_CHOICES,
                "kinds": kinds,
                "is_my": True
            }
        )


class FeedBackAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """ Шийдвэрлэх хуудсын API """

    queryset = Feedback.objects
    serializer_class = FeedBackDecideListSerializer

    @login_required()
    def get(self, request, pk=None):

        state = request.GET.get("state")
        kind = request.GET.get("kind")
        is_my = request.GET.get("is_my")

        if pk:
            self.serializer_class = FeedBackDecideGETSerializer
            data = self.retrieve(request, pk).data
            return request.send_data(data)

        extra_filters = {}

        if state:
            state = state.split(",")
            extra_filters['state__in'] = state

        if kind:
            kind = kind.split(",")
            extra_filters['kind__in'] = kind

        if is_my:
            extra_filters['to_employees'] = request.employee
        else:
            extra_filters['to_employees'] = None

        self.queryset = self.queryset \
                                .filter(
                                    **request.exactly_org_filter,
                                    **extra_filters,
                                ) \
                                .order_by("-kind__rank", "-created_at")

        data = self.list(request).data
        return request.send_data(data)

    @login_required()
    def put(self, request, pk):
        """ Татгалзах эсвэл зөвшөөрөх нь """

        request.data._mutable = True

        is_my = request.data.get("is_my")
        remove_commands = request.data.getlist("remove_commands")
        if not is_my:
            check = any(
                item in request.permissions
                for item in ['sanal-gomdol-decide-approve', 'sanal-gomdol-decide-refuse']
            )
            if not check:
                return request.send_error("ERR_011")

        whats = {
            "cancel": Feedback.STATE_CANCELED,
            "success": Feedback.STATE_GRANTED
        }

        if request.data.get("what") not in whats.keys():
            return request.send_error("ERR_013")

        state = whats.get(request.data.get("what"))
        request.data['state'] = state
        request.data['decided_employee'] = request.employee.pk
        del request.data["what"]

        with transaction.atomic():

            reqfiles = request.FILES.getlist('commands')
            attachment_ids, files = Attachments.save_attach_get_ids(request, reqfiles)
            request.data['commands'] = attachment_ids
            request.data._mutable = False

            try:
                filters = { 'pk': pk }
                if is_my:
                    filters['to_employees'] = request.employee

                obj = self.queryset.get(**filters)
                if not obj:
                    return request.send_error("ERR_013")

                serializer = FeedbackUPDATESerializer(instance=obj, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                obj = self.queryset.get(pk=pk)
                old_att_ids = list(obj.commands.values_list("id", flat=True))
                obj.commands.set(attachment_ids + old_att_ids)

                qs = Attachments.objects.filter(id__in=remove_commands, org=request.org_filter.get("org"))
                Attachments.remove_obj(qs)

                data = FeedBackDecideGETSerializer(obj, many=False).data
                #  хүсэлт үүсгэсэн хүн рүү хүсэлт явуулах нь
                notification_body = {
                    'title': f'Таны {data.get("kind_name").lower()} {data.get("state_name").lower()}.',
                    'content': f'Таны {data.get("kind_name").lower()} {data.get("state_name").lower()}.',
                    'ntype': 'normal',
                    'url': '',
                    'scope_kind': Notification.SCOPE_KIND_USER,
                    'from_kind': Notification.FROM_KIND_EMPLOYEE,
                    'scope_ids': [ data['user_id'] ]
                }
                Notification.objects.create_notif(request, **notification_body)
                return request.send_rsp("INF_002", data)

            except Exception as e:
                Attachments.remove_files(files)
                raise e


class GetMyFeedBackAttachments(APIView):
    def get(self, request, pk):
        obj = Feedback.objects.get(id=pk)
        serializer = FeedbackGETAttachSerializer(instance=obj)
        return request.send_data(serializer.data)


class GetMyFeedBackCommands(APIView):
    def get(self, request, pk):
        obj = Feedback.objects.get(id=pk)
        serializer = FeedbackGETCommandshSerializer(instance=obj)
        return request.send_data(serializer.data)


class GetUpOrgsApiView(APIView):

    @login_required()
    def get(self, request):

        ## suborg
        if request.org_lvl == 2:
            obj = request.org_filter['suborg']
            return request.send_data([
                {
                    'name': obj.org.name,
                    'id': f'{obj.org.id}-org'
                }
            ])

        ## salbar
        elif request.org_lvl == 1:
            obj = request.org_filter['salbar']
            if request.salbar_pos == 0:
                return request.send_data([
                    {
                        'name': obj.sub_orgs.org.name,
                        'id': f'{obj.sub_orgs.org.id}-org',
                    },
                    {
                        'name': obj.sub_orgs.name,
                        'id': f'{obj.sub_orgs.id}-sub_org',
                    }
                ])
            else:
                extra_data = list()

                salbar = request.org_filter['salbar']

                parent = salbar.parent

                is_touched = True
                while is_touched:

                    if parent:
                        extra_data.append(
                            {
                                "name": parent.name,
                                "id": f'{parent.id}-salbar'
                            }
                        )
                        parent = parent.parent
                    else:
                        is_touched = False

                return request.send_data([
                    {
                        'name': obj.sub_orgs.org.name,
                        'id': f'{obj.sub_orgs.org.id}-org',
                    },
                    {
                        'name': obj.sub_orgs.name,
                        'id': f'{obj.sub_orgs.id}-sub_org',
                    },
                    *extra_data
                ])

        return request.send_data([])


class GetEmployeeLvlApiView(APIView):

    @login_required()
    def get(self, request, pk):

        if pk == 'self':
            # org
            if request.org_lvl == 3:
                pk = f'{request.org_filter["org"].id}-org'
            # sub_org
            elif request.org_lvl == 2:
                pk = f'{request.org_filter["sub_org"].id}-sub_org'
            ## salbar
            elif request.org_lvl == 1:
                pk = f'{request.org_filter["salbar"].id}-salbar'

        filters = {
            "org": request.org_filter['org'].id,
        }
        id, lvl = pk.split("-")
        if lvl == 'sub_org':
            filters.update(
                {
                    lvl: id,
                    'salbar': None
                }
            )
        elif lvl == 'salbar':
            filters.update(
                {
                    lvl: id
                }
            )
        elif lvl == 'org':
            filters.update(
                {
                    'salbar': None,
                    'sub_org': None
                }
            )

        employee_ids = list(Employee.objects.filter(**filters).values_list("id", flat=True))
        employees = OrgToEmployeeOrgPositionJsonSerializer(
            OrgPosition.objects.filter(org=request.org_filter.get("org")),
            many=True,
            context={
                "employee_ids": employee_ids
            }
        ).data

        return request.send_data(employees)
