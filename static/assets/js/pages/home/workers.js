let homeEmpList = $(".home-emp-list")

cloneFooter(
    ".home-emp-list",
    [
        1, 2, 3, 4,
        5, 6, 7, 8,
        9, 10, 11, 12,
        13, 14, 15, 16,
        17, 18, 19, 20,
    ]
)
const dt = homeEmpList.DataTable({
    processing: false,
    dom: 'lBfrtip',
    serverSide: true,
    fixedColumns: {
        left: _isMobile ? 0 : 3,
        right: 0,
    },
    pageLength: 10,
    scrollCollapse: true,
    scrollX: true,
    scrollY: "400px",
    "ordering": true,
    ajax: { url: "/worker/pagination/all/" }, // JSON file to add data
    columns: [
        // columns according to JSON
        { data: null },
        { data: "clast_name" },
        { data: "cfirst_name" },
        { data: "sub_org__name" },
        { data: "salbar__name" },
        { data: "org_position__name" },
        { data: "cemail" },
        { data: "sub_org_id" },
        { data: "salbar_id" },
        { data: "id" },
        { data: "position_id" },
        { data: "cphone_number" },
        { data: "gender_name" },
        { data: "cregister" },
        { data: "cemdd_number" },
        { data: "cndd_number" },
        { data: "caddress" },
        { data: "unit1_name" },
        { data: "unit2_name" },
    ],
    columnDefs: [
        {
            targets: 0,
            title: "#",
            orderable: false,
            render: function (data, type, full, meta) {
                return (
                    meta.settings._iDisplayStart + meta.row + 1
                );
            },
        },
        {
            targets: 1,
            orderable: false,
            render: function (data, type, full, meta) {
                return `
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
            },
        },
        {
            targets: 2,
            orderable: false,
            render: function (data, type, full, meta) {
                return (`<a class="text-decoration-underline text-dark" href="/account/worker/${full.id}">${full.cfirst_name}</a>`);
            },
        },
        {
            targets: [7, 8, 9, 10], // sub_org_id, salbar_id, id, position_id гэсэн баганыг нууж байна
            visible: false,
        },
        {
            targets: [
                1, 2, 3, 4,
                5, 6, 7, 8,
                9, 10, 11, 12,
                13, 14, 15, 16,
                17, 18
            ],
            orderable: false
        }
    ],
    order: [[2, "asc"]],
    lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, 'Бүгд'],
    ],
    dom: `
        t
        <"mx-2 d-flex mt-1 flex-wrap flex-lg-nowrap mb-1"
            <"col-sm-12 col-md-6" i>
            '<"col-sm-12 col-md-6"p>' +
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
searchFooter(dt)
