let comingEmps = $(".home-coming-emps")

cloneFooter(
    ".home-coming-emps",
    [
        2, 3, 4,
    ]
)
const comingDt = comingEmps.DataTable({
    processing: false,
    dom: 'lBfrtip',
    serverSide: true,
    "pageLength": 10,
    scrollX: true,
    scrollY: "350px",
    ajax: { url: "/coming-employees/" }, // JSON file to add data
    columns: [
        // columns according to JSON
        { data: null },
        { data: null },
        { data: "full_name" },
        { data: "pos_name" },
        { data: "f_in_dt" },
        { data: "f_out_dt" },
    ],
    columnDefs: [
        {
            orderable: false,
            className: "control",
            responsivePriority: 2,
            targets: 0,
            render: function (data, type, full, meta) {
                return "";
            },
        },
        {
            targets: 1,
            title: "#",
            orderable: false,
            render: function (data, type, full, meta) {
                return (
                    meta.settings._iDisplayStart + meta.row + 1
                );
            },
        },
        {
            targets: 2,
            orderable: false,
            render: function (data, type, full, meta) {
                return (
                    `
                        <div class="d-flex align-items-center">
                            ${
                                full.has_img
                                ?
                                    `
                                        <img
                                            src="${full.profile_img}"
                                            alt="img"
                                            style="border-radius: 50%; margin-right: 5px"
                                            width="20"
                                            height="20"
                                            onerror="this.onerror=null; this.src='/media/53x53.jpg'"
                                        />
                                    `
                                :   ""
                            }
                            ${data}
                        </div>
                    `
                );
            },
        },
        {
            targets: [1, 2, 3, 5, 4],
            orderable: false,
        }
    ],
    order: [[4, "asc"]],
    lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, 'Бүгд'],
    ],
    dom: `
        t
        <"mx-2 mt-1 row mb-1"
            <"col-sm-12 col-md-12 mb-1" i>
            '<"col-sm-12 col-md-12 justify-content-center" p>' +
        ">
    `,
    oLanguage: {
        sProcessing: "Ачааллаж байна. ",
        sSearch: "Хайх: ",
        sEmptyTable: "Бичлэг байхгүй",
        sInfoEmpty: "Нийт 0 бичлэг",
        sInfo: "Дэлгэцэнд: _START_ - _END_ Нийт: _TOTAL_ бичлэг",
        sInfoFiltered: " - _MAX_ бичлэгээс",
        sLengthMenu: "_MENU_",
        oPaginate: {
            sFirst: "Эхэнд",
            sLast: "Төгсгөлд",
            sNext: "Дараах",
            sPrevious: "Өмнөх",
        },
    },
});
searchFooter(comingDt)
