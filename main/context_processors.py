from django.apps import apps


def context_config(request):

    Config = apps.get_model("core", "Config")
    configs = Config.objects.all()

    context = {
        'CONFIGS': {
            conf.name: conf.value
            for conf in configs
        }
    }

    return context


def context_page_bookmarks(request):

    context = {
        "BOOKMARKS": {
            "PAGES": []
        }
    }
    if request.user.is_authenticated:
        if hasattr(request.user, 'userbookmarkpages'):
            bookmark = request.user.userbookmarkpages
            context["BOOKMARKS"]['PAGES'] = bookmark.pages

    return context
