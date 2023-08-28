from rest_framework import serializers

from core.models import Salbars, SubOrgs


class SalbarSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name", label="Нэр", style={ "placeholder": "Нэр оруулна уу" })
    sub_orgs = serializers.PrimaryKeyRelatedField(label='Дэд байгууллага', queryset=SubOrgs.objects.all())

    def __init__(self, *args, **kwargs):
        self.filter_sub_orgs_queryset(self.fields['sub_orgs'], *args, **kwargs)
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_filters(request):
        """ Дэд байгууллагын filter хийх нь """
        filters = {
            "org": request.org_filter.get("org")
        }

        if request.org_filter.get("salbar"):
            filters['salbars'] = request.org_filter.get("salbar").id

        if request.org_filter.get("sub_org"):
            filters['id'] = request.org_filter.get("sub_org").id

        return filters

    def filter_sub_orgs_queryset(self, field, *args, **kwargs):
        """
            Дэд байгууллагын сонголтыг нэтвэрсэн хэрэглэгчийн
            байгууллагын дэд байгууллагууд аар шүүж харуулна
        """

        request = kwargs.get("context").get("request")
        filters = self.get_filters(request)
        field.queryset = field.queryset.filter(**filters)

    class Meta:
        model = Salbars
        exclude = "name", 'branch_pos', 'parent', 'org'

    def save(self, **kwargs):
        kwargs['org'] = self.context.get("org")
        if self.context.get("parent"):
            kwargs['parent'] = self.context.get("parent")
        instance = super().save(**kwargs)
        return instance


class Salbar0Serializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name", label="Нэр", style={ "placeholder": "Нэр оруулна уу" })

    class Meta:
        model = Salbars
        exclude = "name", 'sub_orgs', 'parent', 'org', 'branch_pos'


class SalbarListSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name")
    a_attr = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Salbars
        exclude = "name",

    def get_children(self, obj):
        childs = Salbars.objects.filter(parent=obj)
        request = self.context.get("request")
        salbar_pos = request.salbar_pos
        children = SalbarListSerializer(childs, many=True, context={ "request": request }).data

        ## шинээр үүсгэх товч, тэгэхдээ өөрийнхөөсоо доош салбаруудыг үүсгэж болохоор байх
        if salbar_pos <= obj.branch_pos:
            children.append(
                {
                    "text": "шинээр үүсгэх",
                    "a_attr": {
                        "href": f"/salbar/salbar-list/{str(obj.sub_orgs_id)}/{str(obj.id)}/create/"
                    },
                    "icon": 'fa fa-folder-plus'
                }
            )
        return children

    def get_a_attr(self, obj):
        ## датаг засах нь
        return {
            "href": f"/salbar/salbar-list/{str(obj.sub_orgs_id)}/{str(obj.id)}/update/"
        }


class SubOrgsSalbarSerializer(serializers.ModelSerializer):

    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")
    children = serializers.SerializerMethodField()
    a_attr = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubOrgs
        exclude = "name", "id",

    def get_children(self, obj):
        request = self.context.get("request")
        salbar_pos = 0

        filters = {}

        if request.org_filter.get('salbar'):
            salbar_pos = request.salbar_pos
            filters['id'] = request.org_filter.get('salbar').id

        childs = obj.salbars_set.filter(**filters, branch_pos=salbar_pos)
        children = SalbarListSerializer(childs, many=True, context={ "request": request }).data

        #  ямар нэгэн салбарт харьялалгүй бол шинээр үүсгэх товч харагдана
        if "salbar" not in request.org_filter:
            children.append(
                {
                    "text": "шинээр үүсгэх",
                    "a_attr": {
                        "href": f"/salbar/salbar-list/{str(obj.id)}/create/"
                    },
                    "icon": 'fa fa-folder-plus'
                }
            )

        return children

    def get_a_attr(self, obj):

        return {
            "href": "/salbar/salbar-list/" + str(obj.id) + "/create/"
        }


class SalbarTreeSerializer(serializers.ModelSerializer):
    """ Салбарыг мод хэлбэртэйгээр авах нь """

    inc = serializers.SerializerMethodField()
    text = serializers.CharField(source="name", default="")

    class Meta:
        model = Salbars
        fields = "id", 'text', 'inc'

    def get_inc(self, obj):
        childs = Salbars.objects.filter(parent=obj)
        children = SalbarTreeSerializer(childs, many=True).data
        return children
