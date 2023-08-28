from django.http import HttpResponseRedirect


def login_required(
    f=None, login_url=None, is_superuser=False
):
    """
        Нэвтэрсэн хэрэглэгч мөн эсэхийг шалгах decorator
        WARNING: зөвхөн class view дээр л ажиллана
    """

    def decorator(func):

        def wrap(self, request, *args, **kwargs):

            # If the user is authenticated, return the view right away
            if request.user.is_authenticated:
                if is_superuser:
                    if request.user.is_superuser:
                        return func(self, request, *args, **kwargs)
                else:
                    return func(self, request, *args, **kwargs)

            #  login required биш байх юм бол үсэргэх url нь
            if login_url:
                return HttpResponseRedirect(login_url)
            else:
                if request.META.get('HTTP_REFERER'):
                    request.send_message("warning", "ERR_006")
                return HttpResponseRedirect("/account/user-login/")

        return wrap

    return decorator


def has_permission(allowed_permissions=[], must_permissions=[], back_url=None):
    """ Хэрэглэгчийн эрх дунд зөвшөөрөгдсөн эрх байгаа эсэхийг шалгах нь
        allowed_permissions = аль нэг эрх нь байхад л зөвшөөрнө гэж үзнэ
        must_permissions = бүх эрх нь байж байж л зөвшөөрөгдөнө
    """
    def decorator(view_func):

        def wrap(self, request, *args, **kwargs):

            permissions = request.permissions

            def check_allowed_perm():
                """ Аль нэг эрх нь байгааг шалгах """
                check = any(item in permissions for item in allowed_permissions)
                return check

            def check_must_perm():
                """ Бүх эрх нь байгааг шалгах """
                check = all(item in permissions for item in must_permissions)
                return check

            has_perm = False
            permissions = request.permissions

            if allowed_permissions:
                has_perm = check_allowed_perm()

            if must_permissions:
                has_perm = check_must_perm()

            if not has_perm:
                request.send_message("warning", "ERR_011")
                return HttpResponseRedirect(back_url if back_url else "/")

            return view_func(self, request, *args, **kwargs)

        return wrap

    return decorator
