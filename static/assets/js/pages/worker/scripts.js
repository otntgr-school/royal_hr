const CIRCLE_FORM = 0
const PAGE_WAIT_FORM = 1
const COMMAND_FORM = 2

var stepperEl = document.querySelector('.bs-stepper'), // form step хийх element
    numberedStepper = new Stepper(stepperEl), //  bs stepper library
    // currentIndex = numberedStepper._currentIndex,
    $form = $('.routing-slip'), // formууд
    contentSection = $('.content'),
    modal = $(".new-slup-modal"),

    // step1
    positionKind = $(".position-kind"),
    slipRepeater = $('.positions'),
    positions = [],
    // step2
    is_valid_page = false
    test_count = 0
    // table
    slipInfoTable = null
    isConfirm = true

let repeatOption = {
    initEmpty: true,
    show: function () {
        const _this = $(this)
        _this.slideDown();

        //  асуултын хэддэх гэсэн тоог харуулах нь
        let index = _this.closest("[data-repeater-item]").index()
        _this.find(".qst-index").text(`${index + 1})`)

        // Feather Icons
        if (feather) {
            feather.replace({ width: 14, height: 14 });
        }
    },
    hide: function (deleteElement) {
        if (confirm('Та устгахдаа итгэлтэй байна уу')) {
            $(this).slideUp(deleteElement);
        }
        else
        {
            deleteSlip.pop()
        }
    },
}

let slipRepeaterRef = slipRepeater.repeater(repeatOption);

stepperEl.addEventListener('show.bs-stepper', function (event) {
    var index = event.detail.indexStep;
    var numberOfSteps = $(event.target).find('.step').length - 1;
    var line = $(event.target).find('.step');

    for (var i = 0; i < index; i++) {
        line[i].classList.add('crossed');

        for (var j = index; j < numberOfSteps; j++) {
            line[j].classList.remove('crossed');
        }
    }
    if (event.detail.to == 0) {
        for (var k = index; k < numberOfSteps; k++) {
            line[k].classList.remove('crossed');
        }
        line[0].classList.remove('crossed');
    }
    changeForm(index)
});

/** Формын step солигдоод анх ороход хийгдэх үйлдүүд */
async function changeForm(index)
{
    if (index === CIRCLE_FORM)
    {
        await checkSlip(clickedEmployeeId)
    }
    if(index === PAGE_WAIT_FORM )
    {
        if (slipInfoTable)
        {
            slipInfoTable.destroy()
        }
        isConfirm = true

        addLoader($('#toiroh_huudas_id'))

        slipInfoTable = $(".slup-info-table").DataTable({
            fixedColumns:   {
                left: 0,
                right: 1
            },
            processing: false,
            dom: 'lBfrtip',
            serverSide: true,
            ajax: { url: `/worker/routing-slip-employee/${clickedEmployeeId}/` }, // JSON file to add data
            columns: [
                // columns according to JSON
                { data: null },
                { data: null },
                { data: "org_position" },
                { data: "full_name" },
                { data: "state" },
            ],
            columnDefs: [
                {
                    // For Responsive
                    className: "control",
                    orderable: false,
                    responsivePriority: 2,
                    targets: 0,
                    render: function (data, type, full, meta) {
                        return "";
                    },
                },
                {
                    targets: 4,
                    render: function (data, type, full, meta) {
                        let className = null
                        if(full.state === 'Хүлээгдэж буй')
                            {
                                isConfirm = false
                                className = 'badge rounded-pill badge-light-warning me-1'
                            }
                        else if(full.state === 'Зөвшөөрсөн')
                            className = 'badge rounded-pill badge-light-success me-1'
                        else
                        {
                            className = 'badge rounded-pill badge-light-danger me-1'
                            isConfirm = false
                            if(full.description)
                            {
                                $(`#slip-description`).text(full.description)
                                return(`<span class="${className}">${full.state}</span>
                                    <span class="cursor-pointer" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-original-title="Тайлбар харах">
                                        <span data-bs-toggle="modal" data-bs-target="#xSmall">
                                            ${feather.icons["message-circle"].toSvg({
                                            class: "text-primary curosr-pointer",
                                        })}
                                        </span>
                                    </span>`);
                            }
                        }
                        return (`<span class="${className}">${full.state}</span>`);
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
            ],
            order: [[2, "asc"]],
            lengthMenu: [
				[10, 25, 50, 100, -1],
				[10, 25, 50, 100, 'Бүгд'],
			],
            dom:
                '<"d-flex justify-content-between align-items-center header-actions mx-2 row mt-75"' +
                '<"col-sm-12 col-lg-4 d-flex justify-content-center justify-content-lg-start" l>' +
                '<"col-sm-12 col-lg-8 ps-xl-75 ps-0"<"dt-action-buttons d-flex align-items-center justify-content-center justify-content-lg-end flex-lg-nowrap flex-wrap"<"me-1">B>>' +
                ">t" +
                '<"d-flex justify-content-between mx-2 row mb-1"' +
                '<"col-sm-12 col-md-6"i>' +
                '<"col-sm-12 col-md-6"p>' +
                ">",
            oLanguage: {
                sProcessing: "Ачааллаж байна. ",
                sSearch: "Хайх: ",
                sEmptyTable: "Бичлэг байхгүй",
                sInfoEmpty: "Нийт 0 бичлэг",
                sInfo: "Дэлгэцэнд: _START_ - _END_ Нийт: _TOTAL_ бичлэг",
                sInfoFiltered: " - _MAX_ бичлэгээс",
                sLengthMenu: "_MENU_ бичлэг",
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
                            exportOptions: { columns: [1, 2, 3, 4] },
                        },
                        {
                            extend: "csv",
                            text:
                                feather.icons["file-text"].toSvg({
                                    class: "font-small-4 me-50",
                                }) + "Csv",
                            className: "dropdown-item",
                            exportOptions: { columns: [1, 2, 3, 4] },
                        },
                        {
                            extend: "excel",
                            text:
                                feather.icons["file"].toSvg({
                                    class: "font-small-4 me-50",
                                }) + "Excel",
                            className: "dropdown-item",
                            exportOptions: { columns: [1, 2, 3, 4] },
                        },
                        {
                            extend: "pdf",
                            text:
                                feather.icons["clipboard"].toSvg({
                                    class: "font-small-4 me-50",
                                }) + "Pdf",
                            className: "dropdown-item",
                            exportOptions: { columns: [1, 2, 3, 4] },
                        },
                        {
                            extend: "copy",
                            text:
                                feather.icons["copy"].toSvg({
                                    class: "font-small-4 me-50",
                                }) + "Copy",
                            className: "dropdown-item",
                            exportOptions: { columns: [1, 2, 3, 4] },
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
            initComplete: (settings, json) =>{
                rmLoader($('#toiroh_huudas_id'))
                if(!isConfirm)
                {
                    let slipBtn = document.getElementById('slipBtn')
                    slipBtn.disabled = true;
                    slipBtn.innerText = 'Хүлээгдэж байна...'
                    document.getElementById("fireBtn").style.display = "none";
                }
                else
                {
                    let slipBtn = document.getElementById('slipBtn')
                    slipBtn.disabled = false;
                    slipBtn.innerText = 'Баталгаажуулах'
                    document.getElementById("fireBtn").style.display = "block";
                }
			}
        });
        document.getElementById('fire_commandInputs').style.display= "none"
        modal.modal('show')
    }
}

$(stepperEl)
    .find('.btn-next')
    .each(function () {
        $(this).on('click', function (e) {
            e.preventDefault();

            currentIndex = numberedStepper._currentIndex
            let formElem = $(this).parents('form')

            //  step1  дараагийн форм руу орохын тулд хамрах хүрээний төрөл сонгосон байх
            if (currentIndex == CIRCLE_FORM)
            {
                try {
                    let positionsValues = $('.positions').repeaterVal()
                    let postionsList = positionsValues.positions
                    let data = {}
                    data['postionsList'] = postionsList
                    data['employee'] = selectedFieldId
                    data['delete'] = deleteSlip
                    fetchData('/worker/routing-slip/create/', data, 'POST')
                        .then(
                            ({ success }) =>
                            {
                                if (success)
                                {
                                    numberedStepper.to(currentIndex + 2)
                                }
                            }
                        )
                } catch(error)
                {
                    toastr['warning']('', "Тойрох хуудас бөглөх албан тушаалтны мэдээллийг оруулна уу.", {
                        timeOut: 2500,
                        closeButton: true,
                        hideDuration: 200,
                        progressBar: true,
                        newestOnTop: true
                    })
                    return
                }
            }

            if (!formElem.length)
            {
                numberedStepper.next();
                return
            }

            var isValid = formElem.valid();
            if (isValid) {
                //  Ерөнхий формын датаг хадгалж авж байна
                if (currentIndex === PAGE_WAIT_FORM)
                {
                    generalData = new FormData(formElem[0])
                    if(is_valid_page || test_count > 0)
                        numberedStepper.next();
                    else
                        test_count = test_count + 1
                }
            }
        });
    });

$(stepperEl)
    .find('.btn-prev')
    .on('click', function () {
        numberedStepper.previous();
    });

// ----------- STEP1 --------------

function getParentSection(event)
{
    const $el = $(event.target)
    const repeatItem = $el.parents("div[data-repeater-item]")
    return repeatItem
}

async function checkSlip(id)
{
    const { success, data, error } = await fetchData(`/worker/routing-slip-list/${id}/`, "", 'GET')

    if(success)
    {
        slipRepeaterRef.setList(data)
        setEmployeeOption(data)
    }
}

async function setDEmployee()
{
    const { success, data, error } = await fetchData(`/worker/routing-slip-demployee/`, "", 'GET')

    if(success)
    {
        slipRepeaterRef.setList(data.employee)
        setDEmployeeOption(data)
    }
}

function setEmployeeOption(data)
{
    data.map(function(eachData, index)
    {
        $(`select[name='positions[${index}][employee]']`).html(defaultOption)
        data.map(employee => {
            const option = new Option(employee.full_name, employee.employee_id)
            $(`select[name='positions[${index}][employee]']`).append(option)
        })

        $(`select[name='positions[${index}][employee]']`).val(eachData.employee_id);
        $(`select[name='positions[${index}][org_position]']`).attr('disabled', 'disabled');
        $(`select[name='positions[${index}][employee]']`).attr('disabled', 'disabled');
        const deleteButton = document.getElementsByClassName('slip-delete')
        deleteButton[index].onclick = function()
        {
            deleteSlip.push(eachData.id)
        }
    })
}

// Дэд албан тушаалтэй ажилтануудыг select-ийн утгад оноох
function setDEmployeeOption(data)
{
    data.employee.map(function(eachData, index)
    {
        $(`select[name='positions[${index}][employee]']`).html(defaultOption)
        data.employee.map(employee => {
            if(eachData.org_position === employee.org_position)
            {
                const option = new Option(employee.full_name, employee.id)
                $(`select[name='positions[${index}][employee]']`).append(option)
            }
        })
        $(`select[name='positions[${index}][employee]']`).val(eachData.id);
    })
}

async function slipSubmit(event)
{
    let command = document.getElementById('fire_command_number').value
    const data =
    {
        employee: clickedEmployeeId,
        command: command,
    }
    const { success, error, errors } = await fetchData('/worker/routing-slip/create/', data, 'PUT')

    if (success)
    {
        $('#circle-page-modal').modal('hide');
    }
}
