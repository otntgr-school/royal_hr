from django.apps import apps

def check_org(get_response):
    """ Ямар түвшиний байгууллагын хүн нэвтэрч орсоныг шалгах нь """

    def find_child_salbar_ids(salbar):
        ids = [salbar.id]
        Salbars = apps.get_model("core", 'Salbars')

        finish = True
        last_ids = [salbar.id]
        while finish:
            branch_ids = list(Salbars.objects.filter(parent_id__in=last_ids).values_list("id", flat=True))
            if not branch_ids:
                finish = False
            else:
                last_ids = branch_ids
                ids = ids + last_ids

        return ids

    class DefaultHr:
        def __init__(self):
            self.is_hr = False #  employee байхгүй байх үеийн false hr
            return None

        def __bool__(self):
            return False

    def middleware(request):

        #  Байгууллагын мэдээллээр шүүхэд хэрэгтэй
        #  filter ийг энэчээ оруулах
        org_filter = {}
        exactly_org_filter = {} #  бүх түвшин нь яг өөрийнхөө мэдээллийг авах бол
        org_lvl = 0 # ямар түвшиний байгууллага эсэх нь
        salbar_pos = -1  #  салбар нь хэддэх бранч
        salbar_child_ids = {}
        request.employee = None # хэрэглэгчийн байгуулгын эрх
        request.have_org = True

        Employee = apps.get_model("core", 'Employee')
        Orgs = apps.get_model("core", 'Orgs')

        # Хэрвээ super_user ороход ORG ядаж нэг байгаа үгүй г шалгана
        if request.user.is_superuser and Orgs.objects.last():
            request.have_org = True

        if request.user.is_authenticated:

            employee = Employee.objects.filter(user=request.user, state=Employee.STATE_WORKING, check_super=request.user.is_superuser).first()
            is_employee = True

            if not employee:
                is_employee = False
                employee = DefaultHr()

            request.employee = employee
            request.user.is_employee = is_employee

        # Нэвтэрсэн хэрэглэгч нь ямар нэг байгуулгын ажилтан биш бол defualt эрхүүдийг онооно
        if request.user.is_authenticated and not request.employee:

            request.org_filter = org_filter
            request.org_lvl = org_lvl
            request.salbar_pos = salbar_pos
            request.salbar_child_ids = salbar_child_ids
            request.exactly_org_filter = exactly_org_filter
            if request.user.is_superuser:
                request.org_lvl = 3

        # Нэвтэрсэн хэрэглэгч нь ямар нэг байгуулгын ажилтан бол байгуулгын эрхүүдийг онооно
        elif request.employee:

            if request.employee.org:
                org_filter.update({ "org": request.employee.org })
                exactly_org_filter.update({ "org": request.employee.org })
                org_lvl = 3

            if request.employee.sub_org:
                org_filter.update({ "sub_org": request.employee.sub_org })
                exactly_org_filter.update({ "sub_org": request.employee.sub_org })
                org_lvl = 2
            else:
                exactly_org_filter.update({ "sub_org": None })

            if request.employee.salbar:
                org_filter.update({ "salbar": request.employee.salbar })
                exactly_org_filter.update({ "salbar": request.employee.salbar })
                salbar_child_ids = find_child_salbar_ids(request.employee.salbar)
                salbar_pos = request.employee.salbar.branch_pos
                org_lvl = 1
            else:
                exactly_org_filter.update({ "salbar": None })

            if request.user.is_superuser:
                org_filter.update({ "org": request.employee.org })
                exactly_org_filter.update({ "org": request.employee.org })
                org_lvl = 3

            #  салбар нь exactly өөрөө бол ашиглана
            request.org_filter = org_filter
            request.exactly_org_filter = exactly_org_filter

            request.org_lvl = org_lvl
            request.salbar_pos = salbar_pos
            request.salbar_child_ids = salbar_child_ids

            org_salbar_filter = {**request.org_filter}
            if request.salbar_child_ids:
                org_salbar_filter['salbar__in'] = request.salbar_child_ids
                del org_salbar_filter['salbar']

            #  салбар нь өөрөө болон өөрөөсөө доошоо салбаруудыг хайх хэрэгтэй бол ашиглана
            request.org_salbar_filter = org_salbar_filter

        response = get_response(request)
        return response

    return middleware
