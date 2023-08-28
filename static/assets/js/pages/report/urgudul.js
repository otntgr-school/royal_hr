let reportTable = $(".report-table")
let mainUrl = "/report/urgudul/dt/?"
let filterModal = $("#filter-modal")

let shiidehInput = $(".shiideh-input")
let ilgeehInput = $(".ilgeeh-input")

let shiidehFlat = shiidehInput[0]._flatpickr
let ilgeehFlat = ilgeehInput[0]._flatpickr

ilgeehInput = ilgeehInput.find("[data-input]")

let minusMonth = 1

let todayDate = new Date();
let __yaer = todayDate.getFullYear()
let __month = todayDate.getMonth() + 1
let __date = `${__yaer}-${fullZero(__month)}`

let __startDate = `${__date}-01`

let __endDate = new Date(__yaer, __month, 0);
__endDate = timeZoneToDateString(__endDate, false)

let url = mainUrl + `ilgeeh=${__startDate},${__endDate}`

cloneFooter(
    ".report-table",
    [
        1, 2, 3, 4, 5, 8, 9
    ],
    {
        5: {
            type: "select",
            options: KINDS,
        },
        8: {
            type: "select",
            options: STATES,
        }
    }
)
const reportDT = reportTable.DataTable({
    processing: false,
    dom: 'Bfrtip',
    serverSide: true,
    scrollX: true,
    lengthMenu: [
        [10, 25, 50, 75, 100, 200, -1],
        [10, 25, 50, 75, 100, 200, "Бүгд"]
    ],
    iDisplayLength: -1,
    ajax: { url: url }, // JSON file to add data
    columns: [
        // columns according to JSON
        { data: null },
        { data: "from_employee_name" },
        { data: "to_employee_name" },
        { data: "title" },
        { data: "main_content" },
        { data: "kind_name" },
        { data: "created_at" },
        { data: "decided_at" },
        { data: "state_name" },
        { data: "decided_content" },
        { data: null },
    ],
    columnDefs: [
        {
            targets: 0,
            title: "#",
            orderable: false,
            render: function (data, type, full, meta) {
                return (
                    `
                    <span>
                        ${meta.settings._iDisplayStart + meta.row + 1}
                    </span>
                    `
                );
            },
        },
        {
            targets: -1,
            orderable: false,
            render: function (data, type, full, meta) {
                return (
                    `
                    `
                );
            },
        },
        {
            targets: [0, 1, 2, 3, 4, 5, 8],
            orderable: false,
        }
    ],
    order: [[6, "asc"]],
    lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, 'Бүгд'],
    ],
    dom: `
        <"d-flex justify-content-between align-items-center header-actions mx-2 row pt-0"
            <"col-sm-12 col-lg-4 d-flex justify-content-center justify-content-lg-start"
                l
            >
            <"col-sm-12 col-lg-8 ps-xl-75 ps-0"
                <"dt-action-buttons d-flex align-items-center justify-content-center justify-content-lg-end flex-lg-nowrap flex-wrap ccustom-search"
                    <"me-1">
                    B
                >
            >
        >
        t
        <"mx-2 mt-1 row mb-1"
            <"col-sm-12 col-md-6" i>
            <"col-sm-12 col-md-6"p>
        ">
    `,
    oLanguage: {
        sProcessing: "Ачааллаж байна. ",
        sSearch: "Хайх: ",
        sEmptyTable: "Бичлэг байхгүй",
        sInfoEmpty: "Нийт 0 бичлэг",
        sInfo: `
            <p>
                Нийт: _TOTAL_ бичлэг
            </p>
        `,
        sInfoFiltered: " - _MAX_ бичлэгээс",
        sLengthMenu: "_MENU_",
        oPaginate: {
            sFirst: "Эхэнд",
            sLast: "Төгсгөлд",
            sNext: "Дараах",
            sPrevious: "Өмнөх",
        },
    },
    // Buttons with Dropdown
    buttons: [
        {
            text: "Шүүлтүүр",
            className: "btn btn-primary btn-sm",
            attr: {
                "data-bs-toggle": "modal",
                "data-bs-target": "#filter-modal",
            },
        },
        {
            extend: "collection",
            className: "btn btn-outline-secondary dropdown-toggle me-2",
            text:
                feather.icons["external-link"].toSvg({
                    class: "font-small-4 me-50",
                }) + "Export",
            buttons: [
                {
                    extend: "print",
                    text:
                        feather.icons["printer"].toSvg({
                            class: "font-small-4 me-50",
                        }) + "Print",
                    className: "dropdown-item",
                    exportOptions: {
                        columns: ':visible'
                    }
                },
                {
                    extend: "csv",
                    text:
                        feather.icons["file-text"].toSvg({
                            class: "font-small-4 me-50",
                        }) + "Csv",
                    className: "dropdown-item",
                    exportOptions: {
                        columns: ':visible'
                    }
                },
                {
                    extend: "excel",
                    text:
                        feather.icons["file"].toSvg({
                            class: "font-small-4 me-50",
                        }) + "Excel",
                    className: "dropdown-item",
                    exportOptions: {
                        columns: ':visible'
                    }
                },
                {
                    extend: "pdf",
                    text:
                        feather.icons["clipboard"].toSvg({
                            class: "font-small-4 me-50",
                        }) + "Pdf",
                    className: "dropdown-item",
                    exportOptions: {
                        columns: ':visible'
                    }
                },
                {
                    extend: "copy",
                    text:
                        feather.icons["copy"].toSvg({
                            class: "font-small-4 me-50",
                        }) + "Copy",
                    className: "dropdown-item",
                    exportOptions: {
                        columns: ':visible'
                    }
                },
            ],
            init: function (api, node, config) {
                $(node).removeClass("btn-secondary");
                $(node).parent().removeClass("btn-group");
                setTimeout(function () {
                    $(node)
                        .removeClass("btn-group")
                        .addClass("d-inline-flex mt-50");
                }, 50);
            },
        },
        {
            extend: "collection",
            className: "btn btn-outline-secondary dropdown-toggle me-2 btn-change-to",
            text: "Бүгд",
            buttons: [
                {
                    extend: "",
                    text: "Бүгд",
                    className: "dropdown-item",
                    action: (...args) => handleAction(...args, '')
                },
                {
                    extend: "",
                    text: "Хүний нөөц",
                    className: "dropdown-item",
                    action: (...args) => handleAction(...args, 'hr')
                },
                {
                    extend: "",
                    text: "Хүнд очсон",
                    className: "dropdown-item",
                    action: (...args) => handleAction(...args, 'to_emp')
                },
            ],
            init: function (api, node, config) {
                $(node).removeClass("btn-secondary");
                $(node).parent().removeClass("btn-group");
                setTimeout(function () {
                    $(node)
                        .removeClass("btn-group")
                        .addClass("d-inline-flex mt-50");
                }, 50);
            },
        },
    ],
});
searchFooter(reportDT)
toggleColumns(reportDT)

let btnChangeTo = $(".btn-change-to")

function _redrawDT(newUrl)
{
    reportDT.ajax.url(newUrl).load()
}

function queryToObj(query)
{
    const urlParams = new URLSearchParams(query);
    return Object.fromEntries(urlParams);
}

function objToQuery(params)
{
    return new URLSearchParams(params).toString()
}

function handleAction(e, slipTable, node, config, id)
{
    btnChangeTo.text(config.text)

    let params = queryToObj(url.split("?")[1])
    params['turul'] = id
    let query = objToQuery(params)

    url = mainUrl + query
    _redrawDT(url)
}

function handleSearch()
{
    let ilgeeh = $(ilgeehInput).val()
    let shiideh = $(shiidehInput).val()
    let [ilgeehStart, ilgeehEnd] = ilgeeh.split(" - ")
    let [shiidehStart, shiidehEnd] = shiideh.split(" - ")

    let params = queryToObj(url.split("?")[1])
    params['shiideh'] = `${shiidehStart ?? ""},${shiidehEnd ?? ""}`
    params['ilgeeh'] = `${ilgeehStart ?? ""},${ilgeehEnd ?? ""}`
    let query = objToQuery(params)

    url = mainUrl + query
    _redrawDT(url)
}

function initFilterToDisplay()
{
    const params = queryToObj(url.split("?")[1])
    if (params?.ilgeeh)
    {
        const [start, end] = params.ilgeeh.split(",")
        ilgeehFlat.setDate([start, end])
        ilgeehInput.val(`${start} - ${end}`)
    }
    if (params?.shiideh)
    {
        const [start, end] = params.shiideh.split(",")
        shiidehFlat.setDate([start, end])
        shiidehInput.val(`${start} - ${end}`)
    }
}
initFilterToDisplay()
