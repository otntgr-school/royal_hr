
from django.db.models import Q

EXACTLY_FILTER = "ex_"

def data_table(queryset, request):
    ''' Data Table дэх утгуудын FILTER
        - ``qs`` = Моделийн queryset
        - ``request`` = request.GET утгаа татна
    '''

    # Бүх ирж байгаа утгуудыг хувьсагчид хадгална
    draw = int(request.GET['draw'])                     # Хэд дэх удаагаа filter хийж байгаа нийлбэр
    length = request.GET['length']                      # Нийт урт
    start = int(request.GET['start'])                   # Эхлэх утга
    search_value = request.GET['search[value]']         # Хайсан утга

    # Бүх Field-үүдийн утгыг хадгална
    column_datas = []
    # order_by шүүх утгуудаа хадгална
    order_columns = []

    # field тус бүрийн хайх утга
    extra_filters = Q()

    # Бүх Field-үүдийн утгыг хадгалж байна
    for index in request.GET:
        if index[-6:] == '[data]':
            value = request.GET.get(f"{index[:-6]}[search][value]")

            if value:
                if request.GET[index][0:3] == EXACTLY_FILTER:
                    extra_filters.add(Q(**{f"{request.GET[index]}": value.strip() }), Q.AND)
                else:
                    extra_filters.add(Q(**{f"{request.GET[index]}__icontains": value.strip() }), Q.AND)

            column_datas.append(request.GET[index])
            continue

    # Хэрвээ хуудас луу анх орж эхний хүсэлт ирвэл олон order_by утгыг
    # хадгалж шүүнэ
    if draw == 1:
        order_columns_number = 0
        for index in request.GET:
            if index[-8:] == '[column]':

                order_column = column_datas[int(request.GET[index])]
                if request.GET['order['+str(order_columns_number)+'][dir]'] == 'desc':
                    order_column = '-' + order_column

                order_columns.append(order_column)
                order_columns_number = order_columns_number + 1
                continue

    # Анхных бши дараа дараачийн filter бол нэг л утга байгаа тул давталт гүйлгэх шаардлагагүй
    else:
        order_column = request.GET.get('order[0][column]')      # tuple-ээс аль дугаартай field гэдгийг заана
        order = request.GET.get('order[0][dir]')                # (ASC or DESC)

        if order_column and order:
            # column_datas key-ээр хайж аль field-ээр хайхыг олж авна
            order_column = column_datas[int(order_column)]

            # ASC, DESC-ийг шүүнэ
            if order == 'desc':
                order_columns.append('-' + order_column)
            else:
                order_columns.append(order_column)

    # Хэрвээ үг хайлт хийсэн бол filter-дээрээ нэмнэ
    if extra_filters:
        queryset = queryset.filter(extra_filters)

    # Нийт хэдэн value байгааг тоолно
    total = queryset.count()

    # Filter дээрээ олж авсан мэдээллүүдээрээ шүүнэ
    limit = (
        start + int(length)
        if length != "-1"
        else
        None
    )
    queryset = queryset.order_by(*order_columns)[start:limit]

    # Бүх утгуудаа буцаана
    return {
        'data': queryset,
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered':total,
    }
