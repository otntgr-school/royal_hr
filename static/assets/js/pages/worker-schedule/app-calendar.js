/**
 * App Calendar
 */

/**
 * ! If both start and end dates are same Full calendar will nullify the end date value.
 * ! Full calendar will end the event on a day before at 12:00:00AM thus, event won't extend to the end date.
 * ! We are getting events from a separate file named app-calendar-events.js. You can add or remove events from there.
 **/

//  responsive дэлгэц багасах үед хажуу шүүлтүүрийн хэсгийг нээх нь
$(document).on('click', '.fc-sidebarToggle-button', function (e) {
    $('.app-calendar-sidebar, .body-content-overlay').addClass('show');
});

//  responsive дэлгэц багасах үед хажуу шүүлтүүрийн хэсгийг хаах нь
$(document).on('click', '.body-content-overlay', function (e) {
    $('.app-calendar-sidebar, .body-content-overlay').removeClass('show');
});

var calendarEl = document.getElementById('calendar'),
    eventToUpdate,
    sidebar = $('.event-sidebar'),
    eventForm = $('.event-form'),
    addEventBtn = $('.add-event-btn'),
    cancelBtn = $('.btn-cancel'),
    updateEventBtn = $('.update-event-btn'),
    toggleSidebarBtn = $('.btn-toggle-sidebar'),

    eventTitle = $('#title'),
    eventLabel = $('.select-label'),
    startDate = $('#start-date'),
    endDate = $('#end-date'),
    eventUrl = $('#event-url'),
    eventGuests = $('#event-guests'),
    eventLocation = $('#event-location'),
    allDaySwitch = $('.allDay-switch'),
    wholeSwitch = $(".whole-switch"),
    eventEmployees = $("#employees"),
    calendarEditor = $('#event-description-editor');

    selectAll = $('.select-all'),
    calEventFilter = $('.calendar-events-filter'),

    filterInput = $('.input-filter'),
    btnDeleteEvent = $('.btn-delete-event'),
    filterPrefix = 'kind-filter-',

    warningModal = $('#warning-modal'),
    updateWarningModal = $('#warning-update-modal')

// ------------------------------------------------
// addEvent
// ------------------------------------------------
function addEvent(eventData)
{
    calendar.removeAllEvents();
    calendar.addEvent(eventData);
    calendar.refetchEvents();
}

// --------------------------------------------
// On add new item, clear sidebar-right field fields
// --------------------------------------------
$('.add-event button').on('click', function (e) {
    $('.event-sidebar').addClass('show');
    $('.sidebar-left').removeClass('show');
    $('.app-calendar .body-content-overlay').addClass('show');
});

// Start date picker
if (startDate.length) {
    var start = startDate.flatpickr({
        enableTime: true,
        altFormat: 'Y-m-dTH:i:S',
        onReady: function (selectedDates, dateStr, instance) {
            if (instance.isMobile) {
                $(instance.mobileInput).attr('step', null);
            }
        }
    });
}

// End date picker
if (endDate.length) {
    var end = endDate.flatpickr({
        enableTime: true,
        altFormat: 'Y-m-dTH:i:S',
        onReady: function (selectedDates, dateStr, instance) {
            if (instance.isMobile) {
                $(instance.mobileInput).attr('step', null);
            }
        }
    });
}

/** Формын утгыг оноож өгөх нь */
function setValues(eventToUpdate)
{
    const extendedProps = eventToUpdate.extendedProps

    eventTitle.val(extendedProps.work_title);
    eventLabel.val(extendedProps.kind).change()
    startDate.val(moment(extendedProps.start_date).format('YYYY-MM-DD HH:mm'));
    endDate.val(moment(extendedProps.end_date).format('YYYY-MM-DD HH:mm'));
    start.setDate(extendedProps.start_date)
    end.setDate(extendedProps.end_date)
    allDaySwitch.prop('checked', extendedProps.is_all_day)
    wholeSwitch.prop('checked', extendedProps.for_type === WHOLE).change()
    extendedProps.employees !== undefined
        ? eventEmployees.val(extendedProps.employees).change()
        : null;
    eventLocation.val(extendedProps.location)
    calendarEditor.val(extendedProps.description)

    selectedData = extendedProps
}

// Event click function
function eventClick(info) {
    eventToUpdate = info.event;
    if (eventToUpdate.url && eventToUpdate.url !== 'null') {
        info.jsEvent.preventDefault();
        let extendedProps = eventToUpdate.extendedProps
        window.open(eventToUpdate.url, '_blank');

        //  нэмэлтээр нэмэгдсэн төрөл гэдгийг id нь text бол гэж үзсэн
        if (isNaN(parseInt(extendedProps.kind)))
        {
            return
        }
    }

    sidebar.modal('show');
    addEventBtn.addClass('d-none');
    cancelBtn.addClass('d-none');
    updateEventBtn.removeClass('d-none');
    btnDeleteEvent.removeClass('d-none');

    setValues(eventToUpdate)
}

// Modify sidebar toggler
function modifyToggler() {
    $('.fc-sidebarToggle-button')
        .empty()
        .append(feather.icons['menu'].toSvg({ class: 'ficon' }));
}

// Selected Checkboxes
function selectedCalendars() {
    var selected = [];
    $('.calendar-events-filter input:checked').each(function () {
        selected.push($(this).attr('data-value').replace(filterPrefix, ''));
    });
    return selected;
}

// --------------------------------------------------------------------------------------------------
// AXIOS: fetchEvents
// * This will be called by fullCalendar to fetch events.
//   Also this can be used to refetch events.
// --------------------------------------------------------------------------------------------------
function fetchEvents(info, successCallback, failureCallback)
{
    var calendars = selectedCalendars();
    if (wholeEvent.length === 0)
    {
        // Fetch Events from API endpoint reference
        $.ajax(
            {
                url: getUrl,
                type: 'GET',
                success: function (result)
                {
                    // Get requested calendars as Array
                    const selectedEvents = result
                                                .data
                                                .filter(
                                                    event =>
                                                    {
                                                        return calendars.includes(event.kind + "")
                                                    }
                                                )
                    events = selectedEvents //  calendar ийн нийт утгыг хадгалж авч байна
                    wholeEvent = selectedEvents //  байгууллага даяар утгыг хадгалах нь
                    successCallback(selectedEvents)
                },
                error: function (error)
                {
                    failureCallback(error)
                }
            }
        );
    }
    //  татаад авсан утгаасаа харуулах эсэхээ хайж олж байна
    else
    {
        const selectedEvents = events.filter(el => calendars.includes(el.kind + ""))
        successCallback(selectedEvents)
    }
}

// Calendar plugins
var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    events: fetchEvents,
    editable: HASUPDATE,
    dragScroll: HASUPDATE,
    dayMaxEvents: 2,
    eventResizableFromStart: true,
    customButtons: {
        sidebarToggle: {
            text: 'Sidebar'
        }
    },
    headerToolbar: {
        start: 'sidebarToggle, prev,next, title',
        end: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
    },
    initialDate: new Date(),
    navLinks: true, // can click day/week names to navigate views
    dateClick: function (info) {
        if (!HASCREATE) {
            warningModal.modal("show")
            return
        }
        var date = moment(info.date).format('YYYY-MM-DD HH:mm');
        resetValues();
        sidebar.modal('show');
        addEventBtn.removeClass('d-none');
        updateEventBtn.addClass('d-none');
        btnDeleteEvent.addClass('d-none');

        startDate.val(date);
        endDate.val(date);

        start.setDate(date)
        end.setDate(date)
    },
    eventDataTransform: function(event) {
        event.title = `${event.work_title}`;
        return event;
    },
    eventClick: function (info) {
        eventClick(info);
    },
    datesSet: function () {
        modifyToggler();
    },
    viewDidMount: function () {
        modifyToggler();
    },
    eventDrop: eventDrop
});

// Render calendar
calendar.render();
// Modify sidebar toggler
modifyToggler();
// updateEventClass();

// Validate add new and update form
if (eventForm.length) {
    eventForm.validate({
        submitHandler: (form, event) => handleSubmit(form, event, addEvent, updateEvent),
        rules: {
            'start_date': { required: true },
            'end_date': { required: true },
            'title': { required: true },
            'kind': { required: true }
        },
        messages: {
            'start_date': { required: 'Эхлэх хугацааг сонгоно уу' },
            'end_date': { required: 'Дуусах хугацааг сонгоно уу' },
            'title': { required: 'Гарчиг өгнө үү' },
            'kind': { required: 'Заавал нэгийг сонгоно уу' },
        }
    });
}

// Sidebar Toggle Btn
if (toggleSidebarBtn.length) {
    toggleSidebarBtn.on('click', function () {
        cancelBtn.removeClass('d-none');
    });
}

var eventMovingInfo
// ------------------------------------------------
// Event ийг зөөж байгаад drop лох үед
// ------------------------------------------------
function eventDrop(eventDropInfo)
{
    updateWarningModal.modal("show")
    eventMovingInfo = eventDropInfo
}
/** Тухайн газар зөөхийг нь зөвшөөрсөн үед */
function eventDropSuccess(event)
{
    let dropedEvent = eventMovingInfo.event
    let extentedProps = dropedEvent.extendedProps
    let body = {
        description: extentedProps.description,
        employees: extentedProps.employees,
        for_type: extentedProps.for_type,
        kind: extentedProps.kind,
        title: extentedProps.work_title,
        start_date: moment(dropedEvent.start).format('YYYY-MM-DD HH:mm'),
        end_date: moment(dropedEvent.end).format('YYYY-MM-DD HH:mm'),
    }
    fetchData(extentedProps.formUrl, body, 'PUT')
        .catch(err => err)
        .then(({ success, data, error }) =>
        {
            if (!success)
            {
                eventMovingInfo.revert();
            }
            else {
                const existingEvent = calendar.getEventById(data.id)
                existingEvent.setExtendedProp("start_date", body.start_date);
                existingEvent.setExtendedProp("end_date", body.end_date);
            }
        })
        .finally(() =>
        {
            eventMovingInfo = null
        })
}
/** Тухайн газар зөөхийг нь зөвшөөрөөгүй үед */
function eventDropNo(event)
{
    eventMovingInfo.revert();
    eventMovingInfo = null
}

// ------------------------------------------------
// updateEvent
// ------------------------------------------------
function updateEvent(eventData) {
    var propsToUpdate = ['id', 'title', 'url', 'color', 'textColor'];
    var extendedPropsToUpdate = ['editable', 'cid', 'end_date', 'start_date', 'work_title', 'description', 'employees', 'kind', 'location', 'is_all_day', 'for_type'];

    updateEventInCalendar(eventData, propsToUpdate, extendedPropsToUpdate);
}

// ------------------------------------------------
// removeEvent
// ------------------------------------------------
function removeEvent(eventId) {
    removeEventInCalendar(eventId);
}

// ------------------------------------------------
// (UI) updateEventInCalendar
// ------------------------------------------------
const updateEventInCalendar = (updatedEventData, propsToUpdate, extendedPropsToUpdate) => {
    const existingEvent = calendar.getEventById(updatedEventData.id)

    // --- Set event properties except date related ----- //
    // ? Docs: https://fullcalendar.io/docs/Event-setProp
    // dateRelatedProps => ['start', 'end', 'allDay']
    // eslint-disable-next-line no-plusplus
    for (var index = 0; index < propsToUpdate.length; index++) {
        var propName = propsToUpdate[index];
        existingEvent.setProp(propName, updatedEventData[propName]);
    }

    // --- Set date related props ----- //
    // ? Docs: https://fullcalendar.io/docs/Event-setDates
    existingEvent.setDates(updatedEventData.start, updatedEventData.end, { allDay: updatedEventData.allDay });

    // --- Set event's extendedProps ----- //
    // ? Docs: https://fullcalendar.io/docs/Event-setExtendedProp
    // eslint-disable-next-line no-plusplus
    for (var index = 0; index < extendedPropsToUpdate.length; index++) {
        var propName = extendedPropsToUpdate[index];
        existingEvent.setExtendedProp(propName, updatedEventData[propName]);
    }
};

// ------------------------------------------------
// (UI) removeEventInCalendar
// ------------------------------------------------
function removeEventInCalendar(eventId) {
    calendar.getEventById(eventId).remove();
}

// Reset sidebar input values
function resetValues() {
    eventLabel.val('').change()
    eventTitle.val('');
    startDate.val('');
    endDate.val('');
    allDaySwitch.prop('checked', false);
    wholeSwitch.prop('checked', !selectedEmployee).change()
    eventEmployees.val(selectedEmployee).change();
    eventLocation.val('');
    calendarEditor.val('');
}

// When modal hides reset input values
sidebar.on('hidden.bs.modal', function () {
    resetValues();
});

// Hide left sidebar if the right sidebar is open
$('.btn-toggle-sidebar').on('click', function () {
    btnDeleteEvent.addClass('d-none');
    updateEventBtn.addClass('d-none');
    addEventBtn.removeClass('d-none');

    wholeSwitch.prop('checked', !selectedEmployee).change()
    eventEmployees.val(selectedEmployee).change();
    selectedData = null

    $('.app-calendar-sidebar, .body-content-overlay').removeClass('show');
});

// Select all & filter functionality
if (selectAll.length) {
    selectAll.on('change', function () {
        var $this = $(this);

        if ($this.prop('checked')) {
            calEventFilter.find('input').prop('checked', true);
        } else {
            calEventFilter.find('input').prop('checked', false);
        }
        calendar.refetchEvents();
    });
}

if (filterInput.length) {
    filterInput.on('change', function () {
        $('.input-filter:checked').length < calEventFilter.find('input').length
            ? selectAll.prop('checked', false)
            : selectAll.prop('checked', true);
        calendar.refetchEvents();
    });
}
