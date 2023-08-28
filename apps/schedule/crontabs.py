
import datetime

from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import Q

from core.models import TimeScheduleRegister
from core.models import WorkingTimeSchedule
from core.models import WorkingTimeScheduleType
from core.models import XyTimeScheduleValues
from core.models import HolidayDayInYear

# Одоогийн цаг
now_time = datetime.datetime.now()


def successRequestAndVacation():
    ''' Амралтын өдөр тооцох
    '''

    with transaction.atomic():

        # одоогын цаг хугацаа realtime
        today_weekday = now_time.strftime('%a').lower() + '_work'
        xy_time_schedule__isnull = 'xy_time_schedule__isnull'

        # ----------- 7 ХОНОГ -----------

        # 7 хоногийн өдрүүдээр хайж өнөөдөр ажиллах эсэхийг шийднэ
        all_working_time_schedules_seven = WorkingTimeSchedule.objects.filter(
            **{ today_weekday: False },
            type = WorkingTimeScheduleType.TYPE_CODE.get('seven_days')
        )

        # цагийн хуваарийн төрөл болгоноор давтаж тухайн ажилчин болгонд шинээр үүсгэж өгнө
        for all_working_time_schedule_seven in all_working_time_schedules_seven:
            for employee in all_working_time_schedule_seven.employees.all():

                # Энэ өдөр шалтгаантай бол шалтгаантай амралт болгоно
                check_shaltgaan = TimeScheduleRegister.objects.filter(
                    date=now_time.date(),
                    employee=employee.id,
                    kind=TimeScheduleRegister.KIND_SHALTGAAN
                ).last()

                if check_shaltgaan:
                    check_shaltgaan.kind = TimeScheduleRegister.KIND_AMRALT_SHALTGAAN
                    check_shaltgaan.save()

                # Байхгүй бол шинээр амралтын өдөр гэж үүсгэнэ
                else:
                    TimeScheduleRegister.objects.create(
                        employee = employee,
                        kind = TimeScheduleRegister.KIND_AMRALT,
                        date = datetime.datetime.now().date()
                    )

        # ----------- XY ажлын хоног -----------

        # # XY ажлын өдөртэй ажил байгаа эсэхийг шалгана
        # all_working_time_schedules_xy = WorkingTimeSchedule.objects.filter(type = WorkingTimeScheduleType.TYPE_CODE.get('xy_days'))
        # yesterday = now_time.date() - datetime.timedelta(days=1)

        # # XY ажлын хуваарьтай бүх хуваариудыг олж давтана
        # for all_working_time_schedule_xy in all_working_time_schedules_xy:

        #     # Ажиллах болон амрах хоног
        #     ajillah_days = all_working_time_schedule_xy.ajillah_day
        #     amrah_days = all_working_time_schedule_xy.amrah_day

        #     # Тухайн газрын ажилчин болгоноор нь давтана
        #     for employee in all_working_time_schedule_xy.employees.all():

        #         # Өчигдрөөс өмнөх бүх утгуудыг татаж авна
        #         all_working_time_schedules_xy = TimeScheduleRegister.objects.filter(employee=employee.id, date__lte=yesterday).order_by('id')

        #         # Ямар ч цагаа бүртгүүлж байгаагүй бол шууд дуусгана
        #         if (not all_working_time_schedules_xy):
        #             continue

        #         # Сүүлийн утгыг барьж авна
        #         all_working_time_schedules_xy_last = all_working_time_schedules_xy.last()

        #         # Хамгийн сүүлд ажилласан байвал
        #         if (all_working_time_schedules_xy_last.kind in [TimeScheduleRegister.KIND_WORKING, TimeScheduleRegister.KIND_TAS, TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN]):

        #             # 1-л хоног ажиллах бол алдаа дараачийн өдөр амралтын өдөр болохоор шууд дуусгана
        #             if (ajillah_days == 1):

        #                 check_shaltgaan = TimeScheduleRegister.objects.filter(
        #                     date=now_time.date(),
        #                     employee=employee.id,
        #                     kind=TimeScheduleRegister.KIND_SHALTGAAN
        #                 ).last()

        #                 if check_shaltgaan:
        #                     check_shaltgaan.kind = TimeScheduleRegister.KIND_AMRALT_SHALTGAAN
        #                     check_shaltgaan.save()
        #                 else:
        #                     TimeScheduleRegister.objects.create(employee=employee, date=datetime.datetime.now().date(), kind=TimeScheduleRegister.KIND_AMRALT)

        #                 continue
        #             else:
        #                 count = 0
        #                 # ажиллах хоног болгоноор нь давтаж
        #                 for ajillah_day in range(int(ajillah_days) - 1):

        #                     # Өмнөх өдрийн ажилласан г барьж авна
        #                     all_working_time_schedules_xy_last = prev_in_order(all_working_time_schedules_xy_last, qs=all_working_time_schedules_xy)

        #                     # Өмнө нь утга байхгүй бол дуусгана
        #                     if not all_working_time_schedules_xy_last:
        #                         continue

        #                     # Харин тоолуур тоолж сүүлийн ажиллах ёстой хоногуудад ажилласан бол амралтын өдөр гэдгийг мэдэж баазад хадгална
        #                     if (all_working_time_schedules_xy_last.kind in [TimeScheduleRegister.KIND_WORKING, TimeScheduleRegister.KIND_TAS, TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN]):
        #                     # TODO:  if all_working_time_schedules_xy_last.kind in [WORK, TAS, SHALTGAAN]:
        #                         count += 1

        #                 if (int(ajillah_days) - 1) == count:
        #                     check_shaltgaan = TimeScheduleRegister.objects.filter(
        #                         date=now_time.date(),
        #                         employee=employee.id,
        #                         kind=TimeScheduleRegister.KIND_SHALTGAAN
        #                     ).last()

        #                     if check_shaltgaan:
        #                         check_shaltgaan.kind = TimeScheduleRegister.KIND_AMRALT_SHALTGAAN
        #                         check_shaltgaan.save()
        #                     else:
        #                         TimeScheduleRegister.objects.create(employee=employee, date=datetime.datetime.now().date(), kind=TimeScheduleRegister.KIND_AMRALT)

        #                     continue

        #         # Хамгийн сүүлд амарсан байвал
        #         if (all_working_time_schedules_xy_last.kind in [TimeScheduleRegister.KIND_AMRALT, TimeScheduleRegister.KIND_AMRALT_SHALTGAAN]):

        #             if (int(amrah_days) != 1):

        #                 count = 0
        #                 # Амрах хоног болгоноор нь давтаж
        #                 for amrah_day in range(int(amrah_days) - 1):

        #                     # Өмнөх өдрийн ажилласан г барьж авна
        #                     all_working_time_schedules_xy_last = prev_in_order(all_working_time_schedules_xy_last, qs=all_working_time_schedules_xy)

        #                     # Өмнө нь утга байхгүй бол дуусгана
        #                     if not all_working_time_schedules_xy_last:
        #                         continue

        #                     # Харин тоолуур тоолж сүүлийн ажиллах ёстой хоногуудад амарсан бол амраагүй өдөр гэдгийг мэдэж баазад хадгална
        #                     if (all_working_time_schedules_xy_last.kind in [TimeScheduleRegister.KIND_AMRALT, TimeScheduleRegister.KIND_AMRALT_SHALTGAAN]):
        #                         count += 1

        #                 # Хэввээ таарахгүй бол амралтын өдөр гэж хадгална
        #                 if (int(amrah_days) - 1) != count:
        #                     check_shaltgaan = TimeScheduleRegister.objects.filter(
        #                         date=now_time.date(),
        #                         employee=employee.id,
        #                         kind=TimeScheduleRegister.KIND_SHALTGAAN
        #                     ).last()

        #                     if check_shaltgaan:
        #                         check_shaltgaan.kind = TimeScheduleRegister.KIND_AMRALT_SHALTGAAN
        #                         check_shaltgaan.save()
        #                     else:
        #                         TimeScheduleRegister.objects.create(employee=employee, date=datetime.datetime.now().date(), kind=TimeScheduleRegister.KIND_AMRALT)

        #                     continue


def absentismTimeRegister():
    ''' Тас болон цагаа бүртгүүлчээд дуусгаагүй бол шууд дуусгаж торгууль бодно
    '''

    with transaction.atomic():

        # Бүх цагийн хуваарийн төрөлийг нь авна
        all_working_time_schedules_seven = WorkingTimeSchedule.objects.all()

        # цагийн хуваарийн төрөл болгон болон түүний ажилчин болгоноор нь давтана
        for all_working_time_schedule_seven in all_working_time_schedules_seven:

            # # Торгууль
            # end_time_penalty = all_working_time_schedule_seven.end_time_penalty

            #  ---------- 7 хоног бол ------------
            if int(all_working_time_schedule_seven.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days'):

                # одоогын цаг хугацаа realtime
                today_weekday = datetime.datetime.now().strftime('%a').lower() + '_work'

                # Өнөөдөр ажлын өдөр биш бол давталтыг дуусгана
                if not getattr(all_working_time_schedule_seven, today_weekday):
                    continue

                # Ажлын цаг дуусах хугацаа
                today_time_schedule = datetime.datetime.now().strftime('%a').lower() + '_time_schedule'
                end_time = (getattr(all_working_time_schedule_seven, today_time_schedule)).end_time

                # Ажлын цаг дуусах хугацаа нь одоогийнхоос хэтрээгүй бол цааш явуулахгүй
                if end_time >= now_time.time():
                    continue

                # Ажилчин болгоноор нь давтана
                for employee in all_working_time_schedule_seven.employees.all():

                    check_time_schedule = TimeScheduleRegister \
                        .objects \
                        .filter(
                            employee_id=employee.id
                        )

                    # Ядаж нэг удаа ажилсныг шалгаж ажилаагүй бол шууд дуусгана
                    if not check_time_schedule:
                        continue

                    # Өнөөдөр ажилласан үгүйг шалгана
                    time_schedule = check_time_schedule \
                        .filter(
                            date=datetime.datetime.now().date(),
                        ).last()

                    # Байсан ч чөлөөтэй бол Ажлын өдөр чөлөөтэй гэж хадгална
                    if time_schedule and time_schedule.kind == TimeScheduleRegister.KIND_SHALTGAAN:
                        time_schedule.kind = TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN
                        time_schedule.save()

                    qs_holiday = HolidayDayInYear.objects.filter(
                        (Q(every_year=True) & Q(date__month=now_time.month) & Q(date__day=now_time.day)) | (Q(every_year=False) & Q(date__year=now_time.year) & Q(date__month=now_time.month) & Q(date__month=now_time.day))
                    )

                    kind_custom = TimeScheduleRegister.KIND_TAS

                    if qs_holiday:
                        kind_custom = TimeScheduleRegister.KIND_AMRALT_AJLIIN

                    # Байхгүй бол тасалсан гэж хадгална
                    if (not time_schedule):
                        TimeScheduleRegister \
                            .objects \
                            .create(
                                employee=employee,
                                date=datetime.datetime.now().date(),
                                kind=kind_custom
                            )
                        continue

                    # # ирсэн байсанч ирсэнээ явуулаад явсан аа явуулаагүй бол явсаныг бөглөж торгууль ноогдуулна
                    # if (time_schedule.in_dt and not time_schedule.out_dt):

                    #     # Өнөөдөрийн date-г Явсан цаг бүртгэж дуусах цагтай холбож он сарыг үүсгэж
                    #     # Түүнээс ажилд ирсэн цагаа хасна
                    #     value = datetime.datetime.combine(now_time.date(), end_time) - time_schedule.in_dt

                    #     # Ажилласан цагыг бодож олно
                    #     s = int(value.total_seconds())
                    #     hours = s // 3600
                    #     s = s - (hours * 3600)
                    #     minutes = s // 60
                    #     seconds = s - (minutes * 60)
                    #     worked_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                    #     # Тэр өдөр торгуультай бол торгууль дээр нь нэмэгдэнэ
                    #     final_fine_value = time_schedule.fine + end_time_penalty

                    #     # Баазад хадгална
                    #     time_schedule.out_dt = datetime.datetime.combine(now_time.date(), end_time)
                    #     time_schedule.worked_time = worked_time
                    #     # time_schedule.fine = final_fine_value
                    #     time_schedule.save()
                    #     continue


            # -------------------- XY хоног бол -------------------
            if int(all_working_time_schedule_seven.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):

                # Ажилчин болгоноор нь давтана
                for employee in all_working_time_schedule_seven.employees.all():

                    qs_registration_end_time = all_working_time_schedule_seven.registration_end_time
                    ps_xytimeschedulevalues = XyTimeScheduleValues.objects.filter(employee=employee.id).last()
                    start_next_job_date = ps_xytimeschedulevalues.start_next_job_date
                    job_end_date = start_next_job_date + relativedelta(hours=all_working_time_schedule_seven.ajillah_time)

                    # Ажлын цагааа явуулах сүүлийн хугацаа
                    registration_end_time = start_next_job_date + relativedelta(hours=qs_registration_end_time.hour, minutes=qs_registration_end_time.minute, seconds=qs_registration_end_time.second) + relativedelta(hours=all_working_time_schedule_seven.ajillah_time)

                    # Явсан цагаа бүртгүүлэх цаг нь одоогийнхоос хэтрээгүй бол цааш явуулахгүй
                    if registration_end_time >= now_time:
                        continue

                    # Ажилласан үгүйг шалгана
                    time_schedule = TimeScheduleRegister.objects.filter(
                        employee_id=employee.id,
                        in_dt__lte=registration_end_time,
                        in_dt__gte=start_next_job_date,
                        for_shaltgaan__isnull=True
                    ).last()

                    # # Хэрвээ тэр өдөр цагаа явуулсан мөртлөө явсан цагаа явуулаагүй бол явсан болгож торгууль бодно
                    # if (time_schedule):
                    #     if (time_schedule.in_dt and not time_schedule.out_dt):

                    #         # Өнөөдөрийн date-г Явсан цаг бүртгэж дуусах цагтай холбож он сарыг үүсгэж
                    #         # Түүнээс ажилд ирсэн цагаа хасна
                    #         value = registration_end_time - time_schedule.in_dt

                    #         # Ажилласан цагыг бодож олно
                    #         s = int(value.total_seconds())
                    #         hours = s // 3600
                    #         s = s - (hours * 3600)
                    #         minutes = s // 60
                    #         seconds = s - (minutes * 60)
                    #         worked_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

                    #         # # Тэр өдөр торгуультай бол торгууль дээр нь нэмэгдэнэ
                    #         # final_fine_value = time_schedule.fine + end_time_penalty

                    #         # Баазад хадгална
                    #         time_schedule.out_dt = registration_end_time
                    #         time_schedule.worked_time = worked_time
                    #         # time_schedule.fine = final_fine_value
                    #         time_schedule.save()
                    #         continue

                    if (time_schedule):
                        # Хэрвээ тэр өдөр цагаа явуулсан мөртлөө явсан цагаа явуулаагүй зүгээр л үргэлжлүүлнэ
                        if (time_schedule.in_dt and not time_schedule.out_dt):
                            continue

                        # Цагаа явуулзан бол шууд дуусгана
                        if (time_schedule.in_dt and time_schedule.out_dt):
                            continue

                    # Тэр өдөр чөлөө аваад чөлөөний хугацаа нь цагаа явуулах хугацаанд байвал цагаа явуулахгүй байж болно
                    time_schedule_shaltgaans = TimeScheduleRegister.objects.filter(
                        Q(employee_id=employee.id),
                        Q(for_shaltgaan__isnull=False),
                        Q(for_shaltgaan__end_day__isnull=True),
                        (
                            Q(for_shaltgaan__start_day=registration_end_time.date()) | Q(for_shaltgaan__start_day=start_next_job_date.date())
                        ),
                        Q(for_shaltgaan__start_time__isnull=False)
                    )

                    # Хэрвээ шалтгаантай байвал шууд дуусгана
                    if time_schedule_shaltgaans:
                        # Шалтгаан болгоноор нь давтаж
                        for time_schedule_shaltgaan in time_schedule_shaltgaans:

                            # Эхлэх өдөр болон цагийг холбоно
                            shaltgaan_check_date = datetime.datetime.combine(time_schedule_shaltgaan.for_shaltgaan.start_day, time_schedule_shaltgaan.for_shaltgaan.start_time)

                            # Эхлэх өдөр болон цагаас өмнө чөлөө авзан бол чөлөөтэй гэж үзнэ
                            if shaltgaan_check_date <= start_next_job_date:
                                continue

                    time_schedule_shaltgaans_date = TimeScheduleRegister.objects.filter(
                        Q(employee_id=employee.id),
                        Q(for_shaltgaan__isnull=False),
                        Q(for_shaltgaan__end_day__isnull=False),
                        (
                            Q(for_shaltgaan__start_day__gte=registration_end_time.date()) & Q(for_shaltgaan__end_day__lte=registration_end_time.date())
                            |
                            Q(for_shaltgaan__start_day__gte=start_next_job_date.date()) & Q(for_shaltgaan__end_day__lte=start_next_job_date.date())
                        ),
                        Q(for_shaltgaan__start_time__isnull=True)
                    )

                    # Өдрөөр чөлөө авсан бол чөлөөтэй гэж үзнэ
                    if time_schedule_shaltgaans_date:
                        continue

                    qs_holiday = HolidayDayInYear.objects.filter(
                        (Q(every_year=True) & Q(date__month=now_time.month) & Q(date__day=now_time.day)) | (Q(every_year=False) & Q(date__year=now_time.year) & Q(date__month=now_time.month) & Q(date__month=now_time.day))
                    )

                    kind_custom = TimeScheduleRegister.KIND_TAS

                    if qs_holiday:
                        kind_custom = TimeScheduleRegister.KIND_AMRALT_AJLIIN

                    # ТАС-г хадгална
                    TimeScheduleRegister.objects.create(
                        employee=employee,
                        date=now_time.date(),
                        kind=kind_custom,
                        in_dt=start_next_job_date,
                        out_dt=job_end_date
                    )


def changeXyStartNextJobAndVacationDate():
    ''' 1 цаг болгон XY ажилчны ажлын, амралтын эхлэх цагийг шинэчлэх
    '''

    # Бүх XY-ээр ажилж байгаа хүмүүсээр давтах
    xy_start_job_values = XyTimeScheduleValues.objects.filter(start_next_job_date__lt=now_time)

    for xy_start_job_value in xy_start_job_values:

        start_next_job_date = xy_start_job_value.start_next_job_date        # Дараачийн ажиллах цаг
        employee_id = xy_start_job_value.employee.id                        # Employee ID

        workingTimeSchedule = WorkingTimeSchedule.objects \
            .filter(employees=employee_id) \
            .values('ajillah_time', 'amrah_time') \
            .last()

        if not workingTimeSchedule:
            continue

        ajillah_time = workingTimeSchedule.get('ajillah_time')              # Ажиллах цаг
        amrah_time = workingTimeSchedule.get('amrah_time')                  # Амрах цаг

        # Дараагийн ажиллах цагийг бодож олно
        start_next_job_date_new = start_next_job_date + relativedelta(hours=ajillah_time) + relativedelta(hours=amrah_time)

        xy_start_job_value.start_next_job_date = start_next_job_date_new
        xy_start_job_value.save()

    xy_start_vac_values = XyTimeScheduleValues.objects.filter(start_next_vacation_date__lt=now_time)

    for xy_start_vac_value in xy_start_vac_values:

        start_next_vac_date = xy_start_vac_value.start_next_vacation_date   # Дараачийн ажиллах цаг
        employee_id = xy_start_vac_value.employee.id                        # Employee ID

        workingTimeSchedule = WorkingTimeSchedule.objects \
            .filter(employees=employee_id) \
            .values('ajillah_time', 'amrah_time') \
            .last()

        if not workingTimeSchedule:
            continue

        ajillah_time = workingTimeSchedule.get('ajillah_time')              # Ажиллах цаг
        amrah_time = workingTimeSchedule.get('amrah_time')                  # Амрах цаг

        # Дараагийн амральын цагийг бодож олно
        start_next_vac_date_new = start_next_vac_date + relativedelta(hours=ajillah_time) + relativedelta(hours=amrah_time)

        xy_start_vac_value.start_next_vacation_date = start_next_vac_date_new
        xy_start_vac_value.save()
