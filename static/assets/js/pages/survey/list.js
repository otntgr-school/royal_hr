var listContainer = $(".survey-list-grid"),
    noResult = $(".no-res"),
    stateFilter = $("#state-filter"),
    info = $("#info"),
    checkedSurveys = [],
    rejectModal = $("#warning-reject-modal")

/** Анхааруулгын Модалыг нээж харна */
function rejectSurvey(event)
{
    if (!checkedSurveys.length)
    {
        toastr['warning']('', "Сонгосон судалгаа байхгүй байна", {
            timeOut: 2500,
            closeButton: true,
            hideDuration: 200,
            progressBar: true,
            newestOnTop: true
        })
        return
    }
    rejectModal.modal("show")
}

/** Цуцлах Модалыг зөвшөөрвөл цуцлах хүсэлт явуулах нь */
async function successReject()
{
    const { success, data, errors } = await useLoader(fetchData(`/survey/reject/?ids=${checkedSurveys}`, "", 'DELETE'), listContainer)
    if (success)
    {
        stateFilter.change()
    }
}

/** Судалгааны id г цуглуулах нь */
function handleCheckSurvey(event, surveyId)
{
    const hasIdIdx = checkedSurveys.indexOf(surveyId)
    if (hasIdIdx !== -1)
    {
        checkedSurveys.splice(hasIdIdx, 1)
    }
    else
    {
        checkedSurveys.push(surveyId)
    }
}

/** Тухайн судалгааны төлөвийг харуулах element ийг авах нь */
function stateEl(state)
{
    return {
        "WAITING": `<span class="badge bg-warning">Эхлэх хугацаа болоогүй </span>`,
        "PROGRESSING": `<span class="badge bg-primary">Одоо явагдаж байгаа</span>`,
        "FINISH": `<span class="badge bg-danger">Явагдах хугацаа дууссан</span>`
    }[state]
}

/** Судалгааны жагсаалтын item */
function surveryItem(data)
{
    let html = `<div class="card mb-0 overflow-hidden">
        <div class="card-body">
            <div class="mb-0 d-flex align-items-center">
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="checkbox" onchange="handleCheckSurvey(event, ${data.id})" />
                </div>
                ${stateEl(data.state)}
            </div>
            <div class="mt-1 d-flex fs-13 custom-flex">
                <span class="fw-bold d-block">Судалгаа нэр: &nbsp;</span>
                <span>${data.title}</span>
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
            <div class="d-flex justify-content-between align-items-center fs-13 mt-1">
                <span>Нийт асуулт: ${data.question_count}</span>
                <a class="text-decoration-underline text-dark" onclick="handleDetail(event, ${data.id})">Дэлгэрэнгүй</a>
            </div>
        </div>
    </div>`
    return html
}

/** Анхны утгуудыг оноож өгөх нь судалгааны модал дээр */
function setInitDatas(surveyData)
{
    _surveyKind = surveyData.kind
    surveyDetail = surveyData

    //  step1 ийн утгыг оноох нь
    surveyKinds.each(
        (index, el) =>
        {
            _this = $(el)
            if (_this.data("ckind") === _surveyKind)
            {
                _this.click()
                $(".survey-kind-next").click()
            }
        }
    )

    // step2 нь харуулахдаа render хийдэг учраас scripts.js дотор хийчихсэн
    // step3
    titleInput.val(surveyData.title)
    descriptionInput.val(surveyData.description)
    startDateInput.val(surveyData.start_date)
    endDateInput.val(surveyData.end_date)
    hasShuffleInput.prop("checked", surveyData.has_shuffle)
    isRequiredInput.prop("checked", surveyData.is_required)
    isHideEmployeesInput.prop("checked", surveyData.is_hide_employees)
    logoImg.attr("src", surveyData.image_url ? surveyData.image_url : '/media/400x245.jpg')
    $(".general-form-next").click()

    //step4
    questionsRepeater.setList(surveyData.questions)
    displayBatalgaajulah($form)
    $(".question-next").click()

    if (surveyData.has_pollee)
    {
        btnSubmitC.removeClass("btn-success")
        btnSubmitC.addClass("btn-primary")
        btnSubmitC.html(`Дараах ${feather.icons["arrow-right"].toSvg({
            class: "align-middle ms-sm-25 ms-0",
        })}`)

        sudalgaaProcessTrigger.removeClass("d-none")
        sudalgaaProcess.removeClass("d-none")

        btnSubmitC.click()
        displayProcessCharts(surveyData)
    }
}

/** Тухайн судалгааны дэлгэрэнгүй */
function handleDetail(event, surveyId)
{
    useLoader(fetchData(`/survey/list/${surveyId}/`))
        .then(({ success, data, errors }) =>
        {
            if (success)
            {
                setInitDatas(data)
            }
        })
    modal.modal("show")
}

/** Тухайн жагсаалтны мэдээллийн самбар */
function displayInfo(count)
{
    let html = `<p class="mb-1 fs-13">Нийт: ${count} судалгаа байна.</p>`
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
    const { data, errors, success } = await fetchData(SURVEY_LIST_URL + "?state=" + state)
    if (success)
    {
        displayInfo(data.length)
        displaySurveys(data)
    }
}

stateFilter.on("change", (event) =>
{
    const state = event.target.value
    getSurveyList(state)
})

stateFilter.change()

//  Форм хаагдах үед бүх утгуудыг хоослох
modal.on('hidden.bs.modal', function () {
    // do something…
    titleInput.val("")
    descriptionInput.val("")
    startDateInput.val("")
    endDateInput.val("")
    hasShuffleInput.prop("checked", false)
    isRequiredInput.prop("checked", false)
    isHideEmployeesInput.prop("checked", false)
    logoImg.attr("src", "/media/400x245.jpg")
    deActiveKind()

    selectedDatas = []
    selectedDatasNames = []
    selectedDataContainer.html("")
    selectedSurveyKind = null
    questions = []
    questionsRepeater.setList([])
    surveyDetail = {}
    lines = []
    bars = []
    pies = []
    generalDataImg = null

    btnSubmitC.addClass("btn-success")
    btnSubmitC.removeClass("btn-primary")
    btnSubmitC.html("Баталгаажуулах")

    sudalgaaProcessTrigger.addClass("d-none")
    sudalgaaProcess.addClass("d-none")

    $form.find(".inactive").remove()

    numberedStepper.to(0)
});
