const LIST_FORM = 1
const GENERAL_FORM = 2
const SURVEY_KIND_FORM = 0
const QUESTIONS_FORM = 3
const CONFIRM_FORM = 4
const PROCESS_FORM = 5

const ALL = 1
const ORG = 2
const SUBORG = 3
const SALBAR = 4
const POSITION = 5
const EMPLOYEES = 6

const MAX_RATING_MAX_VALUE = 5

const KIND_ONE_CHOICE = 1 // 'Нэг сонголт'
const KIND_MULTI_CHOICE = 2 // 'Олон сонголт'
const KIND_BOOLEAN = 3 // 'Тийм // Үгүй сонголт'
const KIND_RATING = 4 // 'Үнэлгээ'
const KIND_TEXT = 5 // 'Бичвэр'

var kindChildren = {
    [SUBORG]: "sub_org",
    [SALBAR]: "salbar",
    [POSITION]: "org_positions",
    [EMPLOYEES]: "employees",
}

var surveyDetail = {}

var stepperEl = document.querySelector('.bs-stepper'), // form step хийх element
    numberedStepper = new Stepper(stepperEl), //  bs stepper library
    $form = $('.add-new-user'), // formууд
    contentSection = $('.content'),
    modal = $(".new-user-modal"),

    // step1
    surveyKinds = $('.survey-kind'), // хамрах хүрээний төрлүүд
    selectedSurveyKind = null, // сонгогдсон хамрах хүрээний төрөл

    // step2 - төрлөөс хамаарч хамрах хүрээгээ сонгоно
    selectedList = {},
    songoltSubOrg = $("#songolt-sub-org"), // select container
    songoltSubOrgSelect = songoltSubOrg.find('select'),
    songoltSalbar = $("#songolt-salbar"), // select container
    songoltSalbarSelect = songoltSalbar.find('select'),
    songoltPosition = $("#songolt-position"), // select container
    songoltPositionSelect = songoltPosition.find('select'),
    songoltEmployee = $("#songolt-employee"), // select container
    songoltEmployeeSelect = songoltEmployee.find('select'),
    choicesForKind = {
        [SUBORG]: [songoltSubOrg],
        [SALBAR]: [songoltSubOrg, songoltSalbar],
        [POSITION]: [songoltPosition],
        [EMPLOYEES]: [songoltEmployee]
    },
    employeesTree = $("#employees-tree"),
    beforeCheckedIds = [],
    choicesData = {}, // select хоорондын хамаарлийн утга,
    selectedDatas = [],
    selectedDatasNames = [],
    selectedDataContainer = $(".selected-datas-container"),

    // step3 - ерөнхий форм
    titleInput = $("input[name='title']"),
    startDateInput = $("input[name='start_date']"),
    descriptionInput = $("textarea[name='description']"),
    endDateInput = $("input[name='end_date']"),
    hasShuffleInput = $("input[name='has_shuffle']"),
    isRequiredInput = $("input[name='is_required']"),
    isHideEmployeesInput = $("input[name='is_hide_employees']"),
    logoInput = $("#logoInput"),
    logoImg = $("#logoImg"),
    generalData = {},
    generalDataImg = null,

    // step4 - асуултууд
    questionKind = $(".question-kind"),
    questionsRepeater = $('.questions'),
    questions = [],
    qValid = true,

    // step5 - preview
    previewContainer = $('.preview-survey'),
    btnSubmitC = $("#btn-submit-c")

    // step6 - prcess
    sudalgaaProcessTrigger = $("#sudalgaa-process-trigger")
    sudalgaaProcess = $("#sudalgaa-process"),
    processCharts = $(".process-charts"),
    questionsProcess = processCharts.find("#tab-questions"),
    generalTab = processCharts.find("#tab-general"),

    warningModal = $("#warning-modal"),
    warningModalText = $(".modal-text")

$form.each(function () {
    var $this = $(this);
    $this.validate({
        rules: {
            sub_org: { required: true },
            salbar: { required: true },
            org_position: { required: true },
            employee: { required: true },
            title: { required: true },
            start_date: { required: true },
            description: { required: true },
            end_date: { required: true },
            has_shuffle: { required: false },
            is_required: { required: false },
            is_hide_employees: { required: false },
        }
    });
});

logoImg.on("click", () => logoInput.click())
logoInput.on("change", handleFileInput)
/** Зурган дээр дарах үед input ийг даруулах нь */
function handleFileInput(event)
{
    generalDataImg = window.URL.createObjectURL(event.target.files[0])
    logoImg.attr("src", generalDataImg)
}

/** жагсаалтнаас option үүсгэж select рүү хийнэ */
function optionToSelect(data, $select)
{
    let selectId = $select.attr("id")

    //  хэрвээ data хоосон байвал select ийг хоослоно
    //  хооронодоо хамааралтай select үүддээр хэрэгтэй байна
    if (data.length === 0)
    {
        $select.html("")
    }

    const _selectedKindChildrens = surveyDetail[kindChildren[selectedSurveyKind]] ?? []

    data.map(
        (item, idx) =>
        {
            let html
            //  албан хаагчдыг жагсаалтыг харуулахдаа
            //  албан тушаалаар багцлагдаж ирдэг урчаас багцалж харуулна
            if (selectId === 'songolt-employee-select')
            {
                html = $(`<optgroup label="${item.name}"></optgroup>`);
                item.children.map(
                    (child, idx) =>
                    {
                        let opt = $(`<option value="${child.id}" ${_selectedKindChildrens.includes(child.id) ? "selected" : ""}> ${child.name} </option>`)
                        html.append(opt)
                    }
                )
            }
            else {
                html = `<option value="${item.id}" ${_selectedKindChildrens.includes(item.id) ? "selected" : ""}> ${item.name} </option>`
            }
            $select.append(html)
        }
    )
}

/** Select болгонд утга оруулах нь */
function setOptionsToChoices(data, $select)
{
    let selectId = $select.attr("id")
    choicesData[selectId] = data
    optionToSelect(data, $select)
    $select.change()
}

/** хамгийн сүүлийн choice элем ийг авах нь */
function getLastChoice(getSelect=false)
{
    let choices = choicesForKind[parseInt(selectedSurveyKind)]
    if (!choices)
        return null

    let lastChoice = choices[choices.length - 1]
    if (getSelect)
        return lastChoice.find("select")

    return lastChoice
}

/** сонгогдсон утгаас арилгах нь */
function rmSelectedData(event, id, changeEl)
{
    const isFromEmployee = selectedSurveyKind === EMPLOYEES
    let selectedItems = selectedDataContainer.children()
    selectedItems.each(
        (index, element) =>
        {
            let $el = $(element)
            if ($el.data("cselected-item") + "" === id + "")
            {
                const index = selectedDatas.indexOf(id + "")
                if (index > -1)
                {
                    selectedDatas.splice(index, 1)
                }
                if (!isFromEmployee)
                {
                    $el.remove()
                }
                else {
                    $el.addClass("d-none")
                }
            }
        }
    )
    if (isFromEmployee)
    {
        if (id)
        {
            $("#employees-tree").jstree("uncheck_node", `emp_${id}`);
            const index = beforeCheckedIds.indexOf(`emp_${id}`)
            if (index > -1)
            {
                beforeCheckedIds.splice(index, 1)
            }
        }
    }
    else {
        //  хэрвээ select ээс арилгаж байгаа биш бол
        //  select2 ийн утгаас арилгах
        if (changeEl)
        {
            let lastChoice = getLastChoice()
            let selectEl = lastChoice.find("select")
            selectEl.val(selectedDatas).change()
        }
    }
}

/**Хамрах хүрээнээс хамаараад сонгогдсон утгын дээрх жижиг гарчиг */
function getLabel(data)
{
    if (selectedSurveyKind === EMPLOYEES)
    {
        return data.pos_name
    }
    return data.top_name ? data.top_name : ""
}

/** Сонгогдсон утгуудыг дэлгэц дээр харуулах */
function displaySelectedDatas(data, isDisplay=true)
{
    let html = `
    <div class="d-flex justify-content-between align-items-center ${isDisplay ? '' : "d-none"}" id="item-${data.id}-emp" data-cselected-item="${data.id}">
        <div class="d-flex align-items-center">
            <div class="me-1">
                <img
                    class="rounded"
                    src="${data.avatar ? data.avatar : '/media/53x53.jpg'}"
                    height="38"
                    width="38"
                    alt="avatar"
                    onerror="this.onerror=null; this.src='/media/53x53.jpg'"
                />
            </div>
            <div>
                <label class="fs-12">${getLabel(data)}</label>
                <p class="fw-bold">${data.name}</p>
            </div>
        </div>
        <div onclick="rmSelectedData(event, ${data.id}, true)">
            ${
                feather.icons["x-circle"].toSvg({
                    class: "font-medium-3 cursor-pointer text-danger",
                })
            }
        </div>
    </div>`
    selectedDataContainer.append(html)
    selectedDatasNames.push(data)
}

/** Ажилтнуудыг харуулах нь */
function renderEmployeeChoices({ employees, data })
{
    employees.map(
        (employee, idx) => displaySelectedDatas(employee, false)
    )

    function selectBranch()
    {
        let checkedIds = [];
        let selectedNodes = $("#employees-tree").jstree("get_checked", true);
        $.each(selectedNodes, function() {
            checkedIds.push(this.id);
        });
        let checkedEmpIds = checkedIds.filter(el => el.startsWith("emp_"))
        if (beforeCheckedIds.length === 0)
        {
            checkedEmpIds.map((empId) =>
            {
                let splitedId = empId.replace("emp_", '')
                $(`#item-${splitedId}-emp`).removeClass("d-none")
            })
        }
        beforeCheckedIds.map(
            (empId, idx) =>
            {
                let splitedId = empId.replace("emp_", '')
                if (checkedEmpIds.includes(empId))
                {
                    $(`#item-${splitedId}-emp`).removeClass("d-none")
                }
                else {
                    $(`#item-${splitedId}-emp`).addClass("d-none")
                }
            }
        )
        if (beforeCheckedIds.length < checkedEmpIds.length)
        {
            const newEmps = checkedEmpIds.filter(el => !beforeCheckedIds.includes(el))
            newEmps.map((empId) =>
            {
                let splitedId = empId.replace("emp_", '')
                $(`#item-${splitedId}-emp`).removeClass("d-none")
            })
        }
        selectedDatas = []
        checkedEmpIds.map((empId) =>
        {
            let splitedId = empId.replace("emp_", '')
            selectedDatas.push(splitedId)
        })
        beforeCheckedIds = checkedEmpIds
    }

    employeesTree
        .bind('activate_node.jstree', function (e, data) {
            selectBranch()
        })
        .jstree(
            {
                "core" : {
                    "multiple" : true,
                    'data' : data
                },
                plugins: ['types', 'checkbox'],
                checkbox : {
                    tie_selection : false,
                },
                types: {
                    default: {
                        icon: 'fad fa-sitemap text-primary-green'
                    },
                    sub: {
                        icon: 'fas fa-landmark text-primary'
                    },
                    sub1: {
                        icon: 'far fa-circle text-success'
                    },
                    sub2: {
                        icon: "far fa-circle text-success"
                    },
                    sub3: {
                        icon: 'far fa-circle text-success'
                    }
                }
            }
        )
        .on("ready.jstree", function (e, data) {
            //  Дэлгэрэнгүй дараад ороод харж байвал сонгогдсон утгуудыг харуулах
            if (Object.keys(surveyDetail).length)
            {
                const nodeids = surveyDetail.employees.map((id, idx) => `emp_${id}`)
                employeesTree.jstree(true).check_node(nodeids);
                selectBranch()
                $(".list-btn-next").click()
            }
        })
}

songoltSubOrgSelect.on('change', (event) => handleChangeList(event, 'songolt-sub-org'))
songoltSalbarSelect.on('change', (event) => handleChangeList(event, 'songolt-salbar'))
songoltPositionSelect.on('change', (event) => handleChangeList(event, 'songolt-position'))
/** Жагсаалт формын select ийн утга солигдоход */
function handleChangeList(event, fieldId)
{
    //  хамрах хүрээний сонголтоос хамаараад өөр2 field үүдийг харуулна
    let lastChoice = getLastChoice()
    let name = lastChoice.attr("id")
    let value = event.target.value

    if (name !== fieldId)
    {
        let data = choicesData[fieldId + "-select"]
        const index = data.findIndex(el => el.id + "" === value)
        let children = index > -1 ? data[index].children : []
        // select хоорондын хамаарал
        let selectRels = {
            'songolt-sub-org': songoltSalbarSelect,
            "songolt-salbar": songoltEmployeeSelect,
        }
        setOptionsToChoices(children, selectRels[fieldId])
    }
    //  датагаа цуглуулж авах нь
    else if ($(event.target).val())
    {
        let values = $(event.target).val()

        let isAdd = selectedDatas.length < values.length
        let isRemove = !isAdd

        if (selectedDatas.length === values.length)
        {
            return
        }

        //  select ээс дата устгасан байвал
        if (isRemove)
        {
            let removedId = selectedDatas.find(el => !values.includes(el))
            rmSelectedData({}, removedId)
            return
        }

        value = values.find(el => !selectedDatas.includes(el))
        let data = choicesData[fieldId + "-select"]
        let sdata = {}
        //  хэрвээ ажилтангаас сонгосон бол дахиж хүүхдээс нь хайх хэрэгтэй
        if (fieldId === 'songolt-employee')
        {
            let workIdx = null
            let found = data
                .find(el =>
                    {
                        return el.children.find((el, idx) =>
                            {
                                if (el.id + "" === value)
                                {
                                    workIdx = idx
                                    return true
                                }
                            })
                    })
            sdata = found.children[workIdx]
        }
        else {
            let index = data.findIndex(el => el.id + "" === value)
            sdata = index > -1 ? data[index] : {}
        }

        selectedDatas = [...values]
        displaySelectedDatas(sdata)
        //  Дэлгэрэнгүй дараад ороод харж байвал дараачийн хуудсыг харуулах
        if (Object.keys(surveyDetail).length)
        {
            $(".list-btn-next").click()
        }
    }
}

/** ЖАгсаалт формын сонголтуудыг дуудах нь */
async function getChoicesOptions(query, $container)
{
    let $select = $container.find("select")
    const rsp = await fetchData(LIST_PAGE_AJAX_URL + "?" + query, "", "GET")
    const { success, data, errors } = rsp
    if (success)
    {
        !query.includes("songolt-employee")
        ?
            setOptionsToChoices(data, $select)
        :
            renderEmployeeChoices(data)
    }
    return rsp
}

/** Жагсаалт форм харагдаж байгаа учраас back аас датагаа дуудаж харуулах */
async function renderListForm(choices)
{
    let lastChoice = choices[choices.length - 1]
    //  хамгийн сүүлчийн select ийг multiple болгох нь
    let name = lastChoice.attr("id")
    let query = objectToQueryString({ choices: name })
    await useLoader(
        getChoicesOptions(query, choices[0]),
        contentSection
    )
}

/** Формын step солигдоод анх ороход хийгдэх үйлдүүд */
function changeForm(index, contentElem)
{
    const willBlockForms = [LIST_FORM, GENERAL_FORM, SURVEY_KIND_FORM, QUESTIONS_FORM]
    //  хэрвээ хэн нэгэн асуултанд хариулсан бол засаж болохгүй
    if (willBlockForms.includes(index) && surveyDetail?.has_pollee)
    {
        ccontentElem = $(contentElem).find(".c-content")
        if (!ccontentElem.find(".inactive").length)
        {
            ccontentElem.append(`
                <div class="inactive p-2">
                    <p class="fs-18">Засаж болохгүй</p>
                </div>
            `)
        }
    }

    /** Жагсаалт формын select үүдийг бүгдийг нь арилгах */
    function resetClassesChoice()
    {
        [songoltSubOrg, songoltSalbar, songoltPosition, songoltEmployee]
            .map(
                (choice, idx) =>
                {
                    choice.removeClass("d-block")
                    choice.addClass("d-none")
                    choice.find("select").html("")
                }
            )
    }

    if (index === 0)
    {
        resetClassesChoice()
    }

    //  Жагсаалт
    if (index === LIST_FORM)
    {
        //  хамрах хүрээний сонголтоос хамаараад өөр2 field үүдийг харуулна
        let choices = choicesForKind[parseInt(selectedSurveyKind)]
        choices?.map(
            (choiceSelect, idx) =>
            {
                choiceSelect.removeClass("d-none")
                choiceSelect.addClass("d-block")
            }
        )

        if (choices)
            renderListForm(choices)
    }
}

stepperEl.addEventListener('show.bs-stepper', function (event) {
    var index = event.detail.indexStep;
    var numberOfSteps = $(event.target).find('.step').length - 1;
    var line = $(event.target).find('.step');
    const contentElem = $(event.target).find(".content")[index]

    // The first for loop is for increasing the steps,
    // the second is for turning them off when going back
    // and the third with the if statement because the last line
    // can't seem to turn off when I press the first item. ¯\_(ツ)_/¯

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

    changeForm(index, contentElem)
});

function displayBatalgaajulah(_form)
{
    if (_form)
        generalData = new FormData(_form[0])
    let questionValues = $('.questions').repeaterVal()
    questions = questionValues.questions
    // TODO: VALIDATE шалгах
    renderPreview()
}

$(stepperEl)
    .find('.btn-next')
    .each(function () {
        $(this).on('click', function (e) {
            e.preventDefault();

            let currentIndex = numberedStepper._currentIndex
            let formElem = $(this).parents('form')

            //  step1  дараагийн форм руу орохын тулд хамрах хүрээний төрөл сонгосон байх
            if (currentIndex == SURVEY_KIND_FORM)
            {
                if (!selectedSurveyKind)
                {
                    toastr['warning']('', "Төрөл сонгоно уу", {
                        timeOut: 2500,
                        closeButton: true,
                        hideDuration: 200,
                        progressBar: true,
                        newestOnTop: true
                    })
                    return
                }
                else {
                    if ([ALL, ORG].includes(selectedSurveyKind))
                    {
                        numberedStepper.to(currentIndex + 2)
                    }
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
                if (currentIndex === GENERAL_FORM)
                {
                    generalData = new FormData(formElem[0])
                }
                if (currentIndex === QUESTIONS_FORM)
                {
                    if (!qValid)
                    {
                        toastr['warning']('', `${MAX_RATING_MAX_VALUE} -с хэтрэхгүй байх ёстой`, {
                            timeOut: 2500,
                            closeButton: true,
                            hideDuration: 200,
                            progressBar: true,
                            newestOnTop: true
                        })
                        return
                    }
                    displayBatalgaajulah()
                }
                numberedStepper.next();
            }

        });
    });

$(stepperEl)
    .find('.btn-prev')
    .on('click', function () {
        let currentIndex = numberedStepper._currentIndex

        // step3 аас step2 руу орж байхад
        if (currentIndex == GENERAL_FORM)
        {
            //  нийт болон org сонгосон байвал step2 ийг алгасах
            if ([ALL, ORG].includes(selectedSurveyKind))
            {
                numberedStepper.to(currentIndex - 2)
            }
        }
        numberedStepper.previous();
    });

//  Хамрах хүрээний төрөл болгон дээр onclick
surveyKinds.on("click", selectedSurveyKinds)

/** хуучин active ийг болиулах нь */
function deActiveKind()
{
    surveyKinds.each(
        function ()
        {
            let $this = $(this)
            let hasActive = $this.hasClass("active")
            if (hasActive)
            {
                $this.removeClass('active')
            }
        }
    )
}

/** Хамрах хүрээний төрлийг сонгосноор дараагийн form руу орно */
function selectedSurveyKinds(event)
{
    let kindId = $(event.target).data("ckind")
    deActiveKind()
    //  тухайн дарагдсан element ийг active болгох нь
    event.target.classList.add("active")

    if (kindId !== EMPLOYEES)
    {
        //  хамрах хүрээ солигдох үед select2 ийг multiple болгох нь
        if (selectedSurveyKind !== kindId)
        {
            //  тухайн форм руу орохоосоо сүүлчийн select input ийг select2 болгох
            let choices = choicesForKind[parseInt(kindId)]
            if (choices)
            {
                let lastChoice = choices[choices.length - 1]
                lastChoice.find("select").select2({
                    multiple: true,
                    closeOnSelect: false
                })
            }
        }

        //  хуучин select2 ийн multiple ийг арилгах
        if (selectedSurveyKind !== kindId && selectedSurveyKind && selectedSurveyKind !== EMPLOYEES + "")
        {
            let choices = choicesForKind[parseInt(selectedSurveyKind)]
            if (choices)
            {
                let lastChoice = choices[choices.length - 1]
                lastChoice.find("select").select2({ multiple: false, closeOnSelect: true })
            }
        }
    }

    selectedDatas = []
    selectedDatasNames = []
    selectedDataContainer.html("")
    selectedSurveyKind = kindId
}

// ----------- STEP4 --------------

function getParentSection(event)
{
    const $el = $(event.target)
    const repeatItem = $el.parents("div[data-repeater-item]")
    return repeatItem
}

// form repeater jquery
questionsRepeater.repeater({
    show: function () {
        const _this = $(this)

        if (!qValid) {
            _this.slideUp(_this);
            return
        }
        _this.slideDown();

        //  асуултын хэддэх гэсэн тоог харуулах нь
        let index = _this.closest("[data-repeater-item]").index()
        _this.find(".qst-index").text(`${index + 1})`)

        if (Object.keys(surveyDetail).length)
        {
            _this.find("#question-kind").change()
        }

        // шинээр үүсэж байгаа дээр анхны утгуудыг оноож өгөх нь
        _this.find("#rating_max_count").val("5")
        _this.find("#low_rating_word").val("Муу")
        _this.find("#high_rating_word").val("Сайн")

        // Feather Icons
        if (feather) {
            feather.replace({ width: 14, height: 14 });
        }
    },
    hide: function (deleteElement) {
        const _this = $(this)
        const isQuestion = _this.find(".big-remove").length > 0
        const qid = _this.find("input[id='q-id']").val()
        const cid = _this.find("input[id='c-id']").val()
        const text = 'Та энэ асуултыг устгахдаа итгэлтэй байна уу?'
        const isConfirm = isQuestion ? confirm(text) : true
        if (isConfirm)
        {
            let fetch
            if (qid)
            {
                fetch = fetchData(`/survey/delete-question/${qid}/`, null, 'DELETE')
            }
            else if (cid)
            {
                fetch = fetchData(`/survey/delete-choice/${cid}/`, null, 'DELETE')
            }

            if (!fetch)
            {
                _this.slideUp(deleteElement);
                return
            }
            useLoader(
                fetch,
                _this
            )
                .then(
                    ({ success, data, error }) =>
                    {
                        if (success)
                        {
                            _this.slideUp(deleteElement);
                        }
                    }
                )

        }
    },
    repeaters: [{
        // (Required)
        // Specify the jQuery selector for this nested repeater
        selector: '.inner-repeater',
        hide: function (deleteElement) {
            const _this = $(this)
            if (confirm('Та энэ сонголтыг устгахдаа итгэлтэй байна уу?'))
            {
                _this.slideUp(deleteElement);
            }
        },
        show: function() {
            $(this).slideDown();
        }
    }],
});

/** max rating ийг valdiation шалгах */
function checkRatingMaxCount(event)
{
    const value = event.target.value
    if (parseInt(value) > MAX_RATING_MAX_VALUE)
    {
        qValid = false
        toastr['warning']('', `${MAX_RATING_MAX_VALUE} -с хэтрэхгүй байх ёстой`, {
            timeOut: 2500,
            closeButton: true,
            hideDuration: 200,
            progressBar: true,
            newestOnTop: true
        })
        return
    }
    else {
        qValid = true
    }
}

//  асуултын төрөл солигдоход төрлөөс хамаарсан input үүдийг харуулах
function handleQuestionKind(event)
{
    const value = parseInt(event.target.value)
    const repeatItem = getParentSection(event)

    const dynamicInputs = ['#choices-container', '#max_choice_count_container', '#rating_container']
    dynamicInputs
        .map((selector, idx) => repeatItem.find(selector).addClass("d-none"))
    /** тухайн харагдахгүй байгаа element ийг харуулна */
    function removeClass(selector)
    {
        let el = repeatItem.find(selector)
        el.removeClass("d-none")
    }

    //  хэрвээ сонголттой байвал input ийг харуулна
    if ([KIND_ONE_CHOICE, KIND_MULTI_CHOICE].includes(value))
    {
        removeClass('#choices-container')
    }

    if (value === KIND_MULTI_CHOICE)
    {
        removeClass("#max_choice_count_container")
    }

    if (value === KIND_RATING)
    {
        removeClass("#rating_container")
    }
}
// -------------------------------

// ------ step5 preview ----------

function displayChoice(title, isMulti=false)
{
    return `
        <div class="form-check">
            <input class="form-check-input" type="${isMulti ? "checkbox" : "radio"}" disabled readonly>
            <label class="form-check-label">${title}</label>
        </div>
    `
}

function makeQuestionText(question, isRequired, maxChoiceCount)
{
    let text = question
    let requiredHtml = '<span style="color: red;">*</span>'
    return text + (isRequired ? requiredHtml : "") + (maxChoiceCount ? `  (Хамгийн ихдээ ${maxChoiceCount} -г сонгоно)` : "")
}

function makeRatingAns(textLow, textHigh, numStars, qIndx)
{
    function radios()
    {
        let html = ""
        for (let index = 1; index <= numStars; index++)
        {
            html += `
                <div class="mx-1">
                    <input type="radio" id="radio-${qIndx}-${index}-in" value="${index}" class="form-check-input" disabled />
                    <label htmlFor="radio-${qIndx}-${index}-in" class="form-label d-flex justify-content-center">
                        ${index}
                    </label>
                </div>
            `
        }
        return html
    }
    return `
        <div class="d-flex align-items-center">
            <div>
                ${textLow}
            </div>
            ${radios()}
            <div>
                ${textHigh}
            </div>
        </div>
    `
}

function getNames()
{
    let names = []
    selectedDatas.map(
        (id, idx) =>
        {
            const nameObj = selectedDatasNames.find(el =>
                {
                    return el.id + "" === id
                })
            if (nameObj)
            {
                names.push(nameObj.name)
            }
        }
    )
    return names.join(",")
}

/** Асуултуудыг бүтнээр нь нэг харуулах */
function renderPreview()
{
    const hamrahHuree = Object.fromEntries(HAMRAH_HUREES)[selectedSurveyKind]
    const { title, description, logo, is_required: tIsRequired, has_shuffle, is_hide_employees, start_date, end_date } = Object.fromEntries(generalData)
    previewContainer.html("")
    previewContainer
        .append(
            `
            <p><span class="fw-bold">Хамрах хүрээ:</span> ${hamrahHuree}</p>
            ${selectedDatas.length ? `<h6 class="mb-2">${getNames()}</h6>` : ""}
            <p><span class="fw-bold">Нэр: </span> ${makeQuestionText(title, tIsRequired)}</p>
            <p><span class="fw-bold">Тайлбар: </span> ${description}</p>
            <p><span class="fw-bold">Огноо:</span> ${start_date} - ${end_date}</p>
            ${
                generalDataImg
                ?
                    `<img
                        src="${generalDataImg}"
                        alt="photo"
                        class=""
                        style="width: 150px;"
                        onerror="this.onerror=null; this.src='/media/400x245.jpg'"
                    />`
                :
                    ""
            }
            <div class="fs-12">
                ${tIsRequired ? `<li>Заавал бөглөнө</li>` : ""}
                ${has_shuffle ? `<li>Асуултыг холино</li>` : ""}
                ${is_hide_employees ? "<li>Бөглөсөн хүнийг нууна</li>" : ""}
            </div>
            <hr />
            <p class="fw-bold mt-1">Асуултууд:</p>
            `
        )
    previewContainer.append(`<div class="questions"></div>`)
    let questionsEl = previewContainer.find(".questions")

    //  Асуултуудыг гаргах нь
    const asuultuud = Object.keys(surveyDetail).length && surveyDetail.has_pollee ? surveyDetail.questions : questions
    asuultuud.map(
        (qel, idx) =>
        {
            const index = idx + 1
            const kind = parseInt(qel.kind)
            const question = qel.question
            const highRatingWord = qel.high_rating_word
            const lowRatingWord = qel.low_rating_word
            const isRequired = qel.is_required.length > 0
            const maxChoiceCount = qel.max_choice_count
            const numStars = qel.rating_max_count
            const choices = qel['choices']

            questionsEl.append(
                `
                    <div class="d-flex">
                        <div>
                            ${index}) &nbsp;
                        </div>
                        <div>
                            ${makeQuestionText(question, isRequired, maxChoiceCount)}
                        </div>
                    </div>
                `
            )

            if (kind === KIND_TEXT) // Бичвэр сонгосон үед
            {
                questionsEl.append(
                    `
                    <textarea class="form-control" disabled readonly placeholder="Хариултыг бичнэ"></textarea>
                    `
                )
            }
            else if (kind === KIND_BOOLEAN) // Тийм үгүй сонголттой гэсэн үед
            {
                questionsEl.append(
                    ['Тийм', 'Үгүй'].map((text, idx) => displayChoice(text))
                )
            }
            else if (kind === KIND_ONE_CHOICE) // Зөвхөн нэг сонголттой үед
            {
                questionsEl.append(
                    choices.map(({ choices }, idx) => displayChoice(choices))
                )
            }
            else if (kind === KIND_MULTI_CHOICE) // Олон сонголттой үед
            {
                questionsEl.append(
                    choices.map(({ choices }, idx) => displayChoice(choices, true))
                )
            }
            else if (kind === KIND_RATING) // Үнэлгээ өгдөг байх үед
            {
                questionsEl.append(
                    makeRatingAns(lowRatingWord, highRatingWord, numStars, idx)
                )
            }

            questionsEl.append(`<div class="mb-2"></div>`)

        }
    )
}

function submitSurvey()
{
    let formElem = $form

    if (formElem.valid())
    {
        let body = Object.fromEntries(generalData)
        body['hamrah_huree_choices'] = selectedDatas
        body['kind'] = selectedSurveyKind
        body['questions'] = questions
        const imageBody = new FormData()
        imageBody.append("image", generalData.get("logo"))
        //  зургыг хадгалах

        let fetch = Object.keys(surveyDetail).length
            ? fetchData(`/survey/update/${surveyDetail.id}/`, body, 'PUT')
            : fetchData('/survey/create/', body, 'POST')

        useLoader(
            fetch,
            $form,
        )
        .then(
            ({ success, data, errors }) =>
            {
                    if (success)
                    {
                        fetchData(`/survey/image/${data.id}/`, imageBody, 'POST', '', false, { message: false })
                            .catch( err => {
                                toastr['warning']('', "Зураг хадгалахад алдаа гарлаа", {
                                    timeOut: 2500,
                                    closeButton: true,
                                    hideDuration: 200,
                                    progressBar: true,
                                    newestOnTop: true
                                })
                            })
                        modal.modal("hide")
                        warningModal.modal("hide")
                        stateFilter.change()
                    }
                    else {
                        console.log(errors);
                    }
                }
            )
    }
}

function showWarningModal()
{
    if (surveyDetail.has_pollee)
    {
        numberedStepper.next();
        return
    }
    warningModal.modal("show")
}

$(stepperEl)
    .find('.btn-submit')
    .on('click', showWarningModal)

/**
 1. Баталгаажуулах дарахаар модалаар итгэлтэй байна уу гэж асуух DONE
 2. Асуултууд дээр ID тавьж өгөх түүгээр нь хуучнийг нь update хийх DONE
 3. Асуулт устгахад шууд back тай нь хамт устгах тэгэхдээ хүнээсээ модалаар асуух DONE
 4. Update хийж байгаа баталгаажуулах форм дээр шинээр нэмэгдсэн асуулт харагдахгүй байгааг засах DONE
 5. Update хийхгээд орох үед зураг ядаж зураг байхгүй гэдэг зураг харуулахгүй байна DONE
 */
