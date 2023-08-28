var listContainer = $(".survey-list-grid"),
    noResult = $(".no-res"),
    stateFilter = $("#state-filter"),
    info = $("#info")

let sudalgaaBoglohForm = document.getElementById('sudalgaaBoglohForm')
let sudalgaaBoglohFormInputs = document.getElementById('sudalgaaBoglohFormInputs')
let formBtnSub = document.getElementById('formBtnSub')
let formBtnClose = document.getElementById('formBtnClose')
let sudalgaaBoglohInputs = {}
let isSubmitted = false

let sudalgaaBoglohFormJq = $('#sudalgaaBoglohForm')
let boglohValidate
let selectedSurveyId = ''

let sums = {}
let limits = {}

let alreadySubmittedList = []

const KIND_ONE_CHOICE = 1
const KIND_MULTI_CHOICE = 2
const KIND_BOOLEAN = 3
const KIND_RATING = 4
const KIND_TEXT = 5

function displayRadioInput(quest)
{
    const radios = quest.choices.map(
        (choice, index) =>
        {
            return (
                `
                    <div class="col-lg-3 col-md-6">
                        <input class="form-check-input" type="radio" id="${quest.id}-${index}" name="${quest.id}" value="${choice.id} ">
                        <label class="me-1" for="${quest.id}-${index}">${choice.choices}</label>
                    </div>
                `
            )
        }
    ).join(" ")
    return radios
}

function handleCheckbox(event, questId)
{
    if(event.target.checked)
    {
        if(limits[questId] <= sums[questId] ? sums[questId] : 0)
        {
            event.target.checked = false
            return
        }
        sums[questId] = (sums?.[questId] ? sums?.[questId] : 0) + 1
    }
    else
    {
        sums[questId] = (sums?.[questId] ? sums?.[questId] : 0) - 1
    }
}

function displayCheckboxInput(quest)
{

    limits[quest.id] = quest.max_choice_count

    const checkboxs = quest.choices.map(
        (choice, index) =>
        {
            return (
                `
                    <div class="col-lg-3 col-md-6 d-flex align-items-center">
                        <div class="form-check form-check-inline me-0">
                            <input onchange="handleCheckbox(event, ${quest.id})" class="form-check-input ${quest.id}" type="checkbox" id="${quest.id}-${index}" name="${quest.id}" value="${choice.id}">
                        </div>
                        <label for="${quest.id}-${index}">${choice.choices}</label>
                    </div>
                `
            )
        }
    ).join(" ")
    return checkboxs
}

function displayRateYo(quest)
{
    const qIndx = quest.id
    function radios()
    {
        let html = ""
        for (let index = 1; index <= quest.rating_max_count; index++)
        {
            html += `
                <div class="mx-1">
                    <input type="radio" id="radio-${qIndx}-${index}-in" name="name-${qIndx}-name" value="${index}" class="form-check-input" />
                    <label htmlFor="radio-${qIndx}-${index}-in" class="form-label d-flex justify-content-center">
                        ${index}
                    </label>
                </div>
            `
        }
        return html
    }
    return(
        `
            <div class="d-flex align-items-center">
                <div>
                    ${quest.low_rating_word}
                </div>
                ${radios()}
                <div>
                    ${quest.high_rating_word}
                </div>
            </div>
        `
    )
}

function displayInput(quest, index)
{
    return {
        [KIND_ONE_CHOICE]: `
            <div class="col-12 mt-1">
                <label name="gg" class="form-label" style="margin-bottom: 5px; font-size: 14px" for="holiday">${index}. ${quest.question}:${quest.is_required ? "<span style='color: red'>*</span>" : ""}</label><br>
                <div class="row specialInputContainer">
                    ${displayRadioInput(quest)}
                </div>
            </div>
        `,
        [KIND_MULTI_CHOICE]: `
            <div class="col-12 mt-1">
                <label name="gg" class="form-label" style="margin-bottom: 5px; font-size: 14px" for="holiday">${index}. ${quest.question} /${quest.max_choice_count}-г сонгоорой/:${quest.is_required ? "<span style='color: red'>*</span>" : ""}</label><br>
                <div class="row specialInputContainerCheckbox">
                    ${displayCheckboxInput(quest)}
                </div>
            </div>
        `,
        [KIND_BOOLEAN]: `
            <div class="col-12 mt-1">
                <label name="gg" class="form-label" style="margin-bottom: 5px; font-size: 14px" for="holiday">${index}. ${quest.question}:${quest.is_required ? "<span style='color: red'>*</span>" : ""}</label><br>
                <div class="row specialInputContainer">
                    <label><input class="form-check-input" type="radio" id="${quest.id}-0" value="1" name="${quest.id}"> Тийм</label>
                    <label><input class="form-check-input" type="radio" id="${quest.id}-1" value="0" name="${quest.id}"> Үгүй</label>
                </div>
            </div>
        `,
        [KIND_RATING]: `
            <div class="col-12 mt-1">
                <label name="gg" class="form-label" style="margin-bottom: 5px; font-size: 14px" for="holiday">${index}. ${quest.question}:${quest.is_required ? "<span style='color: red'>*</span>" : ""}</label><br>
                ${displayRateYo(quest, index)}
            </div>
        `,
        [KIND_TEXT]: `
            <div class="col-12 mt-1">
                <label name="gg" class="form-label" style="margin-bottom: 5px; font-size: 14px">${index}. ${quest.question}:${quest.is_required ? "<span style='color: red'>*</span>" : ""}</label>
                <textarea type="text" id="${quest.id}" name="${quest.id}" class="form-control" placeholder="" data-msg="Энэ талбарыг бөглөнө үү" ></textarea>
            </div>
        `
    }[quest.kind]
}

/** Тухайн судалгааны төлөвийг харуулах element ийг авах нь */
function stateEl(state)
{
    return {
        "WAITING": `<span class="badge bg-warning">Эхлээгүй </span>`,
        "PROGRESSING": `<span class="badge bg-primary">Идэвхитэй</span>`,
        "FINISH": `<span class="badge bg-danger">Дууссан</span>`
    }[state]
}

function stateMy(state)
{
    if(state)
    {
        return `<span class="badge bg-success">Бөглөсөн</span>`
    }
    else
    {
        return `<span class="badge bg-warning">Бөглөөгүй</span>`
    }
}

/** Судалгааны жагсаалтын item */
function surveryItem(data)
{
    // бөглөсөн судалгаа байвал хадгална
    if(data.submitted)
    {
        alreadySubmittedList.push(data.id)
    }

    let html = `<div class="card mb-0 overflow-hidden" onclick="getQuestions(${data.id}, '${data.state}', ${data.has_shuffle})" data-bs-toggle="modal" data-bs-target="#editUser">
        <div class="card-body">
            <div class="mb-0">
                ${stateEl(data.state)}
                ${stateMy(data.submitted)}
            </div>
            <div class="mt-1 d-flex fs-13 custom-flex">
                <span class="fw-bold d-block">Судалгаа нэр: &nbsp; </span>
                <span>${data.title} ${data.is_required ? `<span style="color: red;">*</span>` : ""}</span>
            </div>
            <div class="d-flex fs-13 mt-1 custom-flex">
                <span class="fw-bold d-block">Тайлбар: &nbsp;</span>
                <span class="description-overflow">${data.description}</span>
            </div>
            <div class="d-flex fs-13 mt-1 custom-flex">
                <span class="fw-bold d-block">Эхлэх хугацаа: &nbsp;</span>
                <span>${timeZoneToDateString(data.start_date)}</span>
            </div>
            <div class="d-flex fs-13 mt-1 custom-flex">
                <span class="fw-bold d-block">Дуусах хугацаа: &nbsp;</span>
                <span>${timeZoneToDateString(data.end_date)}</span>
            </div>
            <div class="d-flex fs-13 mt-1 custom-flex">
                <span class="fw-bold d-block">Судалгаа үүсгэсэн: &nbsp;</span>
                <span>${data.created_by}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center fs-13 mt-1">
                <span >Нийт асуулт: ${data.question_count}</span>
                <a class="text-decoration-underline text-dark">Дэлгэрэнгүй</a>
            </div>
        </div>
    </div>`
    return html
}

/** Тухайн жагсаалтны мэдээллийн самбар */
function displayInfo(count)
{
    let html = `<span>Нийт: ${count} судалгаа байна.</span>`
    if (count) noResult.addClass('d-none')
    else noResult.removeClass('d-none')
    info.html(html)
}

/** Фронт дээр судалгааны жагсаалтыг харуулна */
function displaySurveys(datas)
{
    datas.map(
        (data, idx) =>
        {
            let html = surveryItem(data)
            listContainer.append(html)
        }
    )
}

/** Судалгааны жагсаалтыг back аас татаж авах нь */
async function getSurveyList(state)
{
    listContainer.html("")
    const { data, errors, success } = await fetchData(BOGLOH_LIST_URL + "?state=" + state)
    if (success)
    {
        displayInfo(data.length)
        displaySurveys(data)
    }
}

// Анхны утга өгөх
function setInputValues(data, onlyDisable=false)
{
    if(onlyDisable)
    {
        Object.entries(sudalgaaBoglohInputs).map(
            (inputValue) =>
            {
                if(inputValue[1] == KIND_TEXT)
                {
                    document.getElementById(inputValue[0]).disabled = true
                    return
                }
                if(inputValue[1] == KIND_RATING)
                {
                    $(`input[name='name-${inputValue[0]}-name']`).attr("disabled", true)
                    return
                }
                if(inputValue[1] == KIND_BOOLEAN)
                {
                    // document.getElementById(inputValue[0]).disabled = true
                    // return
                    const radios = document.getElementsByName(inputValue[0])
                    var elementsRadio = [... radios]
                    elementsRadio.map(
                        (radio) =>
                        {
                            radio.disabled = true
                        }
                    )
                    return
                }
                if(inputValue[1] == KIND_MULTI_CHOICE)
                {
                    $('.specialInputContainerCheckbox input[type=checkbox]').attr('disabled','true');
                    return
                }
                if(inputValue[1] == KIND_ONE_CHOICE)
                {
                    const radios = document.getElementsByName(inputValue[0])
                    var elementsRadio = [... radios]
                    elementsRadio.map(
                        (radio) =>
                        {
                            radio.disabled = true
                        }
                    )
                    return
                }
            }
        )
        return
    }
    data.map(
        (inputValue) =>
        {
            if(sudalgaaBoglohInputs[inputValue.question] == KIND_TEXT)
            {
                document.getElementById(inputValue.question).value = inputValue.answer
                document.getElementById(inputValue.question).disabled = true
                return
            }
            if(sudalgaaBoglohInputs[inputValue.question] == KIND_RATING)
            {
                $(`input[name='name-${inputValue.question}-name'][value='${inputValue.answer}']`).attr('checked', true);
                $(`input[name='name-${inputValue.question}-name']`).attr("disabled", true)
                return
            }
            if(sudalgaaBoglohInputs[inputValue.question] == KIND_BOOLEAN)
            {
                // document.getElementById(inputValue.question).checked = inputValue.answer === "1"
                // document.getElementById(inputValue.question).disabled = true
                // return
                const radios = document.getElementsByName(inputValue.question)
                var elementsRadio = [... radios]
                elementsRadio.map(
                    (radio) =>
                    {
                        radio.disabled = true
                        if(radio.value == inputValue.answer)
                        {
                            radio.checked = true
                        }
                    }
                )
                return
            }
            if(sudalgaaBoglohInputs[inputValue.question] == KIND_MULTI_CHOICE)
            {
                $('.specialInputContainerCheckbox input[type=checkbox]').attr('disabled','true');
                $(`.specialInputContainerCheckbox`).find('[value=' + inputValue.choosed_choices.join('], [value=') + ']').prop("checked", true)
                return
            }
            if(sudalgaaBoglohInputs[inputValue.question] == KIND_ONE_CHOICE)
            {
                const radios = document.getElementsByName(inputValue.question)
                var elementsRadio = [... radios]
                elementsRadio.map(
                    (radio) =>
                    {
                        radio.disabled = true
                        if(radio.value == inputValue.choosed_choices[0])
                        {
                            radio.checked = true
                        }
                    }
                )
                return
            }
        }
    )
}

// асуулт авах
async function getQuestions(surId, state, has_shuffle)
{
    sums = {}
    limits = {}
    sudalgaaBoglohInputs ={}
    // Бөглөсөн судалгаа эсэхийг шалгах
    if(alreadySubmittedList.includes(surId) || state === "FINISH")
    {
        formBtnSub.classList.add('d-none')
        formBtnClose.classList.add('d-none')
        isSubmitted = true
    }
    else
    {
        formBtnSub.classList.remove('d-none')
        formBtnClose.classList.remove('d-none')
        isSubmitted = false
    }
    sudalgaaBoglohFormInputs.innerHTML = ''
    selectedSurveyId = surId
    let { data, success } = await fetchData(`/survey/question/${surId}/`, null, 'GET')
    if(success)
    {
        let rules = {}
        let messages = {}
        if(has_shuffle) data = shuffle(data)
        sudalgaaBoglohFormInputs.innerHTML = data.map(
            (quest, index) =>
            {
                // validate оруулж байна
                rules[quest.id] = {
                    required: quest.is_required
                }
                messages[quest.id] = {
                    required: 'Энэ талбарыг заавал бөглөх ёстой'
                }

                // input үүдийг авж байна
                sudalgaaBoglohInputs[quest.id] = `${quest.kind}`
                return displayInput(quest, index + 1)
            }
        ).join(" ")

        state === "FINISH" && setInputValues(null, true)

        if (sudalgaaBoglohFormJq.length) {
            boglohValidate = sudalgaaBoglohFormJq.validate({
                rules,
                messages,
                // validate алдаа хаана гархыг зааж байна
                errorPlacement: function(error, element)
                {
                    if ( element.is(":radio"))
                    {
                        error.appendTo( element.parents('.specialInputContainer') );
                    }
                    else if ( element.is(":checkbox"))
                    {
                        error.appendTo( element.parents('.specialInputContainerCheckbox') );
                    }
                    else
                    {
                        error.insertAfter( element );
                    }
                }
            })
        }
        sudalgaaBoglohForm.onsubmit = function(event){sudalgaaBoglohSubmit(event)}
    }
    if(isSubmitted)
    {
        const { success, data } = await fetchData(`/survey/bogloson/${surId}/`, null , 'GET')
        if(success)
        {
            setInputValues(data)
        }
    }
}

async function sudalgaaBoglohSubmit(event)
{
    event.preventDefault()
    const body = []
    if(!sudalgaaBoglohFormJq.valid())
    {
        return
    }
    Object.entries(sudalgaaBoglohInputs).map(
        async (element) =>
        {
            const type = element[1]
            const input = element[0]

            // Radio байвал
            if(type == KIND_ONE_CHOICE)
            {
                var radios = document.getElementsByName(input);
                for (var i = 0, length = radios.length; i < length; i++) {
                    if (radios[i].checked) {
                        body.push(
                            {
                                answer: null,
                                question: input,
                                choosed_choices: [radios[i].value],
                                survey: selectedSurveyId
                            }
                        )
                    }
                }
            }
            // checkbox байвал
            else if (type == KIND_MULTI_CHOICE || type == KIND_BOOLEAN)
            {
                // KIND_BOOLEAN
                if(!$(`input.${input}:checked`).length)
                {
                    const radios = document.getElementsByName(input);
                    const radiosArray = [ ...radios ]
                    radiosArray.map(
                        (radio) =>
                        {
                            if(radio.checked)
                            {
                                body.push(
                                    {
                                        answer: radio.value,
                                        question: input,
                                        choosed_choices: [],
                                        survey: selectedSurveyId
                                    }
                                )
                            }
                        }
                    )
                    return
                }

                // KIND_MULTI_CHOICE
                const selected = $(`input.${input}:checked`).map(function(_, el) {
                    return $(el).val();
                }).get();

                body.push(
                    {
                        answer: null,
                        question: input,
                        choosed_choices: selected,
                        survey: selectedSurveyId
                    }
                )
            }
            else if (type == KIND_RATING)
            {
                const songolt = $(`input[name='name-${input}-name']:checked`).val()
                body.push(
                    {
                        answer: songolt ?? "0",
                        question: input,
                        choosed_choices: [],
                        survey: selectedSurveyId
                    }
                )
            }
            else {
                body.push(
                    {
                        answer: document.getElementById(input).value,
                        question: input,
                        choosed_choices: [],
                        survey: selectedSurveyId
                    }
                )
            }
        }
    )
    const { success } = await fetchData('/survey/boglohList/', body, 'POST')
    if(success)
    {
        stateFilter.change()
        formBtnClose.click()
        sudalgaaBoglohInputs = {}
        isSubmitted = false
        selectedSurveyId = ''
        alreadySubmittedList = []
    }
}

stateFilter.on("change", (event) =>
{
    const state = event.target.value
    getSurveyList(state)
})

stateFilter.change()
