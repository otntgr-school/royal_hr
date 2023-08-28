from django.apps import apps

from django.db import models, transaction
from django.db.models.functions import Concat
from django.db.models import Value, CharField
from django.db.models.functions import Substr
from django.db.models.functions import Upper

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def full_name(self):
        UserInfo = apps.get_model("core", "UserInfo")
        return self.filter(
            userinfo__action_status=UserInfo.APPROVED,
            userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
        ).annotate(full_name=Concat(Upper(Substr("userinfo__last_name", 1, 1)), Value(". "), "userinfo__first_name"))

    def create_user(self, email, password=None):

        if not email:
            raise ValueError("Хэрэглэгч заавал и-мэйл байна.")
        if not password:
            raise ValueError("Хэрэглэгч заавал нууц үг байна.")

        user = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = False
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError("Хэрэглэгч заавал и-мэйл байна.")
        if not password:
            raise ValueError("Хэрэглэгч заавал нууц үг байна.")

        user = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Unit2Manager(models.Manager):

    def full_name(self):
        return self.annotate(full_name=Concat("unit1__name", Value(", "), "name"))


class Unit3Manager(models.Manager):

    def full_name(self):
        return self.annotate(full_name=Concat("unit2__unit1__name", Value(", "), "unit2__name", Value(", "), "name"))


class SalbarManager(models.Manager):

    @staticmethod
    def get_filters(request):
        """ Салбарын filter ийг авах нь """

        filters = {**request.org_filter}
        if request.org_filter.get("salbar"):
            filters['id'] = request.org_filter.get("salbar").id
            del filters['salbar']

        if request.org_filter.get("sub_org"):
            filters['sub_orgs'] = request.org_filter.get("sub_org")
            del filters['sub_org']

        return filters

    def get_branches(self, request):
        """ Өөрөөсөө доошоо байгаа salbar уудыг авах нь """

        filters = self.get_filters(request)
        from salbar.serializer import SalbarTreeSerializer

        salbar_pos = 0

        if request.salbar_pos != -1:
            salbar_pos = request.salbar_pos

        qs = self.filter(**filters, branch_pos=salbar_pos)
        branches = SalbarTreeSerializer(instance=qs, many=True, context={ "request": request }).data

        return branches


class NotifManager(models.Manager):

    def create_notif(self, request, scope_ids, title, content, from_kind, scope_kind, ntype, url=""):
        """
            Мэдэгдэл шинээр үүсгэх нь
            request бол request
            scope_ids гэдэг нь хамрах хүрээний id нууд
            title гарчиг
            content бол тайлбар
            from_kind хэнээс мэдэгдэл ирсэн гэдэг төлөв нь
            scope_kind хамрах хүрээний төрөл нь (хамрах хүрээний төрлөөс хамаараад scope_ids ийг тухайн field дээр хадгална)
            url тухайн мэдэгдэл дараад үсрэх хуудасны url
        """

        with transaction.atomic():

            from_kind = int(from_kind)
            scope_kind = int(scope_kind)

            Notification = apps.get_model("core", "Notification")
            NotificationType = apps.get_model("core", "NotificationType")
            ntype_obj = NotificationType.objects.filter(code=ntype).first()

            scope_field = {
                Notification.SCOPE_KIND_ORG: "org",
                Notification.SCOPE_KIND_SUBORG: "sub_org",
                Notification.SCOPE_KIND_SALBAR: "salbar",
                Notification.SCOPE_KIND_POS: "org_position",
                Notification.SCOPE_KIND_EMPLOYEE: "employees",
                Notification.SCOPE_KIND_USER: "users",
                Notification.SCOPE_KIND_ALL: "is_all",
            }.get(scope_kind)

            from_field = {
                Notification.FROM_KIND_ORG: "from_org",
                Notification.FROM_KIND_SUBORG: "from_sub_org",
                Notification.FROM_KIND_SALBAR: "from_salbar",
                Notification.FROM_KIND_POS: "from_org_position",
                Notification.FROM_KIND_EMPLOYEE: "from_employees",
                Notification.FROM_KIND_USER: "from_users",
            }.get(from_kind)

            if not scope_field:
                raise request.send_error("ERR_013")

            # хаанаас гэдэг төрлөөс нь хамаарч тухайн хүний id ийг хадгалах
            from_dict = dict()
            if from_kind == Notification.FROM_KIND_ORG:
                from_dict[from_field] = request.org_filter.get("org")
            elif from_kind == Notification.FROM_KIND_SUBORG:
                from_dict[from_field] = request.org_filter.get("sub_org")
            elif from_kind == Notification.FROM_KIND_SALBAR:
                from_dict[from_field] = request.org_filter.get("salbar")
            elif from_kind == Notification.FROM_KIND_POS:
                from_dict[from_field] = request.employee.org_position
            elif from_kind == Notification.FROM_KIND_EMPLOYEE:
                from_dict[from_field] = request.employee
            elif from_kind == Notification.FROM_KIND_USER:
                from_dict[from_field] = request.user

            payload = {}
            payload.update(from_dict)
            if scope_field == "is_all":
                payload[scope_field] = True

            obj = self.create(
                **payload,
                title=title,
                content=content,
                from_kind=from_kind,
                scope_kind=scope_kind,
                ntype=ntype_obj,
                url=url,
                created_by=request.user,
            )

            attr = getattr(obj, scope_field)
            if scope_field != "is_all":
                attr.set(scope_ids)

            return obj


class EmployeeManager(models.Manager):

    def filter(self, *args, **kwargs):

        value = False

        if 'check_super' in kwargs:
            value = kwargs['check_super']
            del kwargs['check_super']

        kwargs["user__is_superuser"] = value

        return super().filter(*args, **kwargs)

    def get(self, *args, **kwargs):

        value = False

        if 'check_super' in kwargs:
            value = kwargs['check_super']
            del kwargs['check_super']

        kwargs["user__is_superuser"] = value

        return super().get(*args, **kwargs)
