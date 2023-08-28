from django.shortcuts import redirect
from rest_framework import generics
from rest_framework import mixins
from rest_framework.views import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from core.models import Salbars, SubOrgs

from .serializer import SalbarSerializer
from .serializer import SubOrgsSalbarSerializer
from .serializer import Salbar0Serializer

from main.decorators import has_permission
from main.decorators import login_required

# Create your views here.
class HomeApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/salbar/index.html'

    queryset = Salbars.objects
    serializer_class = SalbarSerializer

    @login_required()
    @has_permission(must_permissions=['salbar-read'])
    def get(self, request, sub_org_id=None, pk=None, action=None):

        #  хамгийн том салбар үүсгэх нь
        if action == "create" and pk == None:
            serializer = Salbar0Serializer()
            suborg = SubOrgs.objects.get(pk=sub_org_id)
            return Response({ 'serializer': serializer, "sub_org_id": sub_org_id, "action": action, "name": suborg.name })

        #  салбарийг засах нь
        if action == "update":
            self.queryset = self.queryset.get(pk=pk)
            serializer = Salbar0Serializer(instance=self.queryset, many=False)
            name = self.queryset.name
            return Response({ 'serializer': serializer, "pk": pk, "action": action, "name": name })

        #  салбарыг үүсгэх нь
        if action == "create":
            queryset = self.queryset.get(pk=pk)
            name = queryset.name
            serializer = Salbar0Serializer()
            return Response({ 'serializer': serializer, "pk": pk, "action": action, "name": name })

        #  хуудас руу хамгийн анх ороход харагдах form
        serializer = self.serializer_class(context={ "request": request })
        return Response({ 'serializer': serializer, "action": "create" })

    @login_required()
    @has_permission(allowed_permissions=['salbar-create', 'salbar-update'])
    def post(self, request, sub_org_id=None, pk=None, action=None):

        #  хамгийн том бранчийг үүсгэх нь
        if sub_org_id:
            request.data._mutable = True
            request.data['sub_orgs'] = sub_org_id
            request.data._mutable = False
            name = SubOrgs.objects.get(pk=sub_org_id).name
            serializer = self.serializer_class(data=request.data, context={ "request": request, "org": request.org_filter.get("org"), })
            if not serializer.is_valid():
                return Response({ 'serializer': Salbar0Serializer, "sub_org_id": sub_org_id, "action": action, "name": name })

        if pk and action == 'update':
            if not request.data['logo']:
                request.data._mutable = True
                request.data.pop('logo')
                request.data._mutable = False

            instance = self.queryset.get(pk=pk)
            name = instance.name
            serializer = Salbar0Serializer(instance=instance, data=request.data, context={ "request": request, "org": request.org_filter.get("org"), })
            if not serializer.is_valid():
                serializer = Salbar0Serializer(instance=instance)
                return Response({ 'serializer': serializer, 'pk': pk, "action": action, "name": name })
            try:
                request.data['logo']
                if instance.logo:
                    instance.logo.delete()
            except:
                None

        if pk and action == 'create':

            parent = self.queryset.get(pk=pk)

            request.data._mutable = True
            request.data['sub_orgs'] = parent.sub_orgs_id
            request.data._mutable = False

            serializer = self.serializer_class(
                data=request.data,
                context={
                    "request": request,
                    "org": request.org_filter.get("org"),
                    "parent": parent
                }
            )

            name = parent.name

            if not serializer.is_valid():
                serializer = Salbar0Serializer()
                return Response({ 'serializer': serializer, 'pk': pk, "action": action, "name": name })

        if action == None and pk == None and sub_org_id == None:
            #  анх ороход байсан формын дагуу үүсгэх нь
            serializer = self.serializer_class(data=request.data, context={ "org": request.org_filter.get("org"), "request": request })
            if not serializer.is_valid():
                return Response({ 'serializer': serializer, "action": "create" })

        serializer.save()
        request.send_message('success', 'INF_015')
        return redirect('salbar-register')


class SubOrgSalbarApiView(
    generics.GenericAPIView,
    mixins.ListModelMixin
):

    queryset = SubOrgs.objects
    serializer_class = SubOrgsSalbarSerializer

    def get(self, request):
        filters = SalbarSerializer.get_filters(request)
        self.queryset = self.queryset.filter(**filters)
        data = self.list(request)
        return data


class SalbarApiView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin
):
    queryset = Salbars.objects
    serializer_class = SalbarSerializer

    def get(self, request, pk):

        return self.retrieve(request, pk)


class SalbarDelete(APIView):

    @login_required()
    @has_permission(must_permissions=['salbar-delete'])
    def get(self, request, pk):

        Salbars.objects.filter(pk=pk).delete()
        request.send_message("success", 'INF_003')
        return redirect("salbar-register")
