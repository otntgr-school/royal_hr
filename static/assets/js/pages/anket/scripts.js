var educationRepeator = $(".edus"),
    educationRepeator2 = $(".edus2"),

    familyRepeater = $(".family"),
    family2Repeater = $(".family2"),
    numbersRepeater = $(".numbers"),

    mergeshil1Repeator = $(".mergeshil1"),
    mergeshil2Repeator = $(".mergeshil2"),
    mergeshil3Repeator = $(".mergeshil3"),
    lagnuageRepeater = $(".languages"),
    pcChadwarRepeater = $(".pc-chadwar"),
    experienceRepeater = $(".experience"),

    largeModal = $("#largeModal"),

    skillTable = $(".skill-table"),
    staticSkills = [],
    extraSkillTable = $(".extra-skill-table"),
    repeaters = $(".crepeat")

let repeatOption = {
    initEmpty: true,
    show: function () {
        const _this = $(this)

        _this.slideDown();

		let yearMonthMask = $(".cyear-and-month")
        if (yearMonthMask)
        {
            yearMonthMask.toArray().forEach(function(field)
            {
                new Cleave(field, {
                    date: true,
                    delimiter: "-",
                    datePattern: ["Y", "m", 'd'],
                });
            })
        }

        let pickr = _this.find(".flatpickr-basic")
        if (pickr)
        {
            pickr.flatpickr({
                locale: {
                    weekdays: {
                        shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
                        longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
                    },
                    months: {
                        shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
                        longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
                    },
                },
            });
        }

        //  асуултын хэддэх гэсэн тоог харуулах нь
        // let index = _this.closest("[data-repeater-item]").index()
        // _this.find(".qst-index").text(`${index + 1})`)

        // Feather Icons
        if (feather) {
            feather.replace({ width: 14, height: 14 });
        }
    },
    hide: function (deleteElement) {
        const _this = $(this)
        const id = _this.find("input[id='id']").val()
        if (confirm('Та устгахдаа итгэлтэй байна уу')) {
            if (!id)
            {
                $(this).slideUp(deleteElement);
                return
            }
            const name = _this.parents().data("repeater-list")
            useLoader(
                fetchData(`/account/anket/${id}/${name}/`, "", 'DELETE'),
                _this
            )
                .catch(err => err)
                .then(
                    ({ success, data, error }) =>
                    {
                        if (success)
                        {
                            $(this).slideUp(deleteElement);
                        }
                    }
                )
        }
    },
}

let educationRepeatorRef = educationRepeator.repeater(repeatOption);
let educationRepeator2Ref = educationRepeator2.repeater(repeatOption);
let familyRepeaterRef = familyRepeater.repeater(repeatOption);
let family2RepeaterRef = family2Repeater.repeater(repeatOption);
let numbersRepeaterRef = numbersRepeater.repeater(repeatOption);
let mergeshil1RepeatorRef = mergeshil1Repeator.repeater(repeatOption);
let mergeshil2RepeatorRef = mergeshil2Repeator.repeater(repeatOption);
let mergeshil3RepeatorRef = mergeshil3Repeator.repeater(repeatOption);
let lagnuageRepeaterRef = lagnuageRepeater.repeater(repeatOption);
let experienceRepeaterRef = experienceRepeater.repeater(repeatOption);
let extraSkillTableRef = extraSkillTable.repeater(repeatOption);
let pcChadwarRepeaterRef = pcChadwarRepeater.repeater(repeatOption);

function displayLevelChoices(unique)
{
    let htmlRadios = ""
    SKILL_CHOICES.map(
        ([id, name], idx) =>
        {
            htmlRadios += `
            <div class="mx-1">
                <input class="form-check-input" type="radio" name="skill-${unique}" value="${id}" id="utga-${unique}-${id}-utga">
                <label class="form-check-label d-flex justify-content-center" for="utga-${unique}-${id}-utga">
                    ${name}
                </label>
            </div>
            `
        }
    )
    return htmlRadios
}

/** Нэг бүлэг ур чадварыг харуулах нь */
function displaySkills(groupSkills)
{
    let html = `
        <div class="table-responsive">
            <table class="table table-hover table-bordered small-text-thead">
            <thead>
                <tr>
                    <th colspan="2">${groupSkills.name}</th>
                    <th style="width: 120px">Түвшин</th>
                </tr>
            </thead>
            <tbody>
                ${
                    (() => {
                        let skillsHTML = ""
                        groupSkills.skills.map(
                            (skill, idx) =>
                            {
                                skillsHTML += `
                                    ${
                                        (
                                            () =>
                                            {
                                                let defHTML = ""
                                                skill.defs.map(
                                                    (def, didx) =>
                                                    {
                                                        defHTML += `
                                                        <tr>
                                                            ${
                                                                didx === 0
                                                                ?
                                                                    `
                                                                    <th rowspan="${skill.defs.length}">
                                                                        ${skill.name}
                                                                    </th>
                                                                    `
                                                                :
                                                                    ""
                                                            }
                                                            <th>
                                                                - ${def.name}
                                                            </th>
                                                            <td class="d-flex align-items-center">
                                                                ${displayLevelChoices(def.id)}
                                                            </td>
                                                        </tr>
                                                        `
                                                    }
                                                )
                                                return defHTML
                                            }
                                        )()
                                    }
                                `
                            }
                        )
                        return skillsHTML
                    })()
                }
    `
    return html
}

function displayListSkills(data)
{
    skillTable.html("")
    data.map(
        (groupSkill, idx) =>
        {
            let html = displaySkills(groupSkill)
            skillTable.append(html)
        }
    )
}

function setInitValuesAnket(values)
{
    let not_names = ['repeater', 'id', 'skills', 'user_id']
    Object
        .keys(values)
        .filter((key, idx) => !not_names.includes(key))
        .map(
            (name, idx) =>
            {
                $(`input[name='${name}']`)?.val(values?.[name] ? values[name] : "")
                $(`select[name='${name}']`)?.val(values?.[name] ? values[name] : "")?.change()
            }
        )

    familyRepeaterRef.setList(values.repeater.family);
    family2RepeaterRef.setList(values.repeater.family2);
    numbersRepeaterRef.setList(values.repeater.numbers);

    educationRepeatorRef.setList(values.repeater.education1);
    educationRepeator2Ref.setList(values.repeater.education2);

    mergeshil1RepeatorRef.setList(values.repeater.mergeshil1);
    mergeshil2RepeatorRef.setList(values.repeater.mergeshil2);
    mergeshil3RepeatorRef.setList(values.repeater.mergeshil3);

    lagnuageRepeaterRef.setList(values.repeater.languages);
    pcChadwarRepeaterRef.setList(values.repeater['pc-chadwar'])
    extraSkillTableRef.setList(values.repeater['extra-skills']);

    experienceRepeaterRef.setList(values.repeater.experience);

    if (values.skills?.length)
    {
        values.skills.map(
            (skill, idx) =>
            {
                let radios = $(`input:radio[name='skill-${skill.skill_def}']`)
                radios.filter(`[value='${skill.level}']`).prop('checked', true);
            }
        )
    }
}

function getSkills()
{
    useLoader(Promise.all([fetchData("/worker/static/skills/"), fetchData("/account/anket/")]), skillTable).catch(err => err)
        .then(
            ([{ success, data, error }, { success: asuccess, data: adata, error: aerror }]) =>
            {
                if (success)
                {
                    displayListSkills(data)
                }
                if (asuccess)
                {
                    setInitValuesAnket(adata)
                }
            }
        )
}

function callNeedDatasAnket(event)
{
    if (staticSkills.length === 0)
    {
        getSkills()
    }
}

function getRepeaterVal(ref, key)
{
    try {
        return ref.repeaterVal()
    } catch (error) {
        return { [key]: [] }
    }
}

/** Анкетийг хадгалх нь */
function handleAnket(event)
{
    event.preventDefault()
    const formData = new FormData(event.target)
    const body = Object.fromEntries(formData)

    const repeatorsVal = {
        ...getRepeaterVal(familyRepeaterRef, 'family'),
        ...getRepeaterVal(family2RepeaterRef, 'family2'),
        ...getRepeaterVal(numbersRepeaterRef, 'numbers'),
        ...getRepeaterVal(educationRepeatorRef, 'education1'),
        ...getRepeaterVal(educationRepeator2Ref, 'education2'),
        ...getRepeaterVal(mergeshil1RepeatorRef, 'mergeshil1'),
        ...getRepeaterVal(mergeshil2RepeatorRef, 'mergeshil2'),
        ...getRepeaterVal(mergeshil3RepeatorRef, 'mergeshil3'),
        ...getRepeaterVal(lagnuageRepeaterRef, 'languages'),
        ...getRepeaterVal(extraSkillTableRef, 'extra-skills'),
        ...getRepeaterVal(experienceRepeaterRef, 'experience'),
        ...getRepeaterVal(pcChadwarRepeaterRef, 'pc-chadwar'),
    }

    let realBody = {}
    Object.keys(body).filter(el => !el.includes("[")).map((el, idx) => realBody[el] = body[el])

    useLoader(
        fetchData('/account/anket/', { repeatorsVal, realBody }, "POST"),
        largeModal
    )
    .catch(err => err)
    .then(({ success, data, error }) =>
    {
        if (success)
        {
            largeModal.modal("hide")
        }
    })

}
