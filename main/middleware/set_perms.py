from django.apps import apps


def set_perms(get_response):
    """ Хэрэглэгчийн эрхийг хэрэгэлгчид оноох нь (хэрэглэхэд хялбар болгож) """

    def middleware(request):

        if request.user.is_authenticated:

            UserInfo = apps.get_model('core', 'UserInfo')
            Permissions = apps.get_model('core', 'Permissions')
            try:
                snippet = UserInfo.objects.get(user_id=request.user.id, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
            except UserInfo.DoesNotExist:
                snippet = None

            request.user_info = snippet if snippet else snippet

            # super user бол бүх эрхийг ашиглана :P
            if request.user.is_superuser:
                permissions = list(Permissions.objects.all().values_list('name', flat=True))
                request.permissions = permissions
            #  super user биш үед л эрх ашиглана
            elif request.employee:
                permissions = list(request.employee.org_position.roles.values_list("permissions__name", flat=True))
                removed_perms = list(request.employee.org_position.removed_perms.values_list("name", flat=True))
                permissions = permissions + list(request.employee.org_position.permissions.values_list("name", flat=True))

                removed_perms = set(removed_perms)
                permissions = set(permissions)
                permissions = permissions.difference(removed_perms)

                request.permissions = list(permissions)
            else:
                request.permissions = []

        response = get_response(request)
        return response

    return middleware
