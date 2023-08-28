import json
from django import template

register = template.Library()


@register.filter
def has_perm(permissions, check_perms):

    check_perms = check_perms.split(", ")

    set_permissions = set(permissions)
    set_check_perms = set(check_perms)
    diff = set_check_perms.difference(set_permissions)

    return len(set_check_perms) != len(diff)


@register.filter
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.simple_tag
def jsonloads(value):
    if isinstance(value, str):
        return json.loads(value)
    return value


@register.simple_tag
def get_ys_undes():
    return [
        "Халх",
        "Баяд",
        "Буриад",
        "Барга",
        "Дарьганга",
        "Дархад",
        "Дөрвөд",
        "Мянгад",
        "Захчин",
        "Өөлд",
        "Торгууд",
        "Үзэмчин",
        "Хамниган",
        "Харчин",
        "Хотгойд",
        "Цахар",
        "Казак",
        "Урианхай",
        "Хотон",
        "Сартуул",
        "Элжигэн",
        "Бусад",
    ]


@register.simple_tag
def weekname(week):
    return {
        1: "Даваа",
        2: "Мягмар",
        3: "Лхагва",
        4: "Пүрэв",
        5: "Баасан",
        6: "Хагас сайн",
        0: "Бүтэн сайн",
    }.get(week)
