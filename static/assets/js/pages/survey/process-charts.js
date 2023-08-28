//  1.   General гэсэн дээр ямар хугацаанд хэдэн хүн бөглөсөнг харуулах(Асуултуудаар нь ангилж болно) - line area
//  2.   Ажилтан харах чеклэгдсэн байвал ямар ажилтан хэдэн асуултанд хариулсанг бас харуулах


let pies = [],
    bars = [],
    lines = []

function displayPrintBtn() {
    return `
    <div class="d-flex justify-content-end mb-2">
      <div class="btn btn-primary cprint-btn" onclick="printQuestion('tab-questions')">
        Бүгдийг хэвлэх
      </div>
    </div>
  `
}

function displayHeader(question) {
    return `
        <div class="d-flex
        flex-sm-row flex-column
        justify-content-md-between
        align-items-start
        justify-content-start">
          <div>
            <h4 class="card-title mb-75">${question.question}</h4>
            <span class="card-subtitle">${question.rsp_count} удаа хариулт илгээсэн байна.</span>
          </div>
          <div class="d-flex align-items-center mt-md-0 mt-1">
            <div class="btn btn-secondary cprint-btn" onclick="printQuestion('container-${question.id}-con')">
              ${feather.icons["printer"].toSvg({
                        class: "font-medium-2",
                    })
                }
            </div>
          </div>
      </div>
    `
}

function printQuestion(elemId) {
    const printBtn = $(`#${elemId}`).find(".cprint-btn")
    printBtn.hide()
    printJS(elemId, 'html')
    printBtn.show()
}

function getDataLabel(question) {
    const label = []
    const data = []
    question.pollees.map(
        (pll, idx) => {
            label.push(pll.name ?? "")
            data.push(pll.count ?? 0)
        }
    )
    return [label, data]
}

function displayAnswers(question) {
    let html = `<div class="col-12" id="container-${question.id}-con">
        <div class="">
            ${displayHeader(question)}
            <div class="card-body">
                <ul class="list-group">
                    ${
                        question.pollees.map(
                            (answer) => {
                                return `<li class="list-group-item">
                                            ${answer.name}
                                            <p class="pb-0 mb-0">
                                                <small>${answer.count} удаа давтагдсан</small>
                                            </p>
                                        </li>`
                            }
                        ).join("")
                    }
                </ul>
            </div>
            <hr />
          </div>
    </div>`
    return html
}

function displayPieChart(question) {
    const [label, data] = getDataLabel(question)
    pies.push({ question, label, data })
    let html = `<div class="col-12" id="container-${question.id}-con">
        <div class="">
            ${displayHeader(question)}
            <div class="card-body">
                <div id="donut-${question.id}-chart"></div>
            </div>
            <hr />
          </div>
    </div>
    `
    return html
}

function displayBarChart(question) {
    const [label, data] = getDataLabel(question)
    bars.push({ question, label, data })
    let html = `<div class="col-12" id="container-${question.id}-con">
        <div class="">
            ${displayHeader(question)}
            <div class="card-body">
                <div id="bar-${question.id}-chart"></div>
            </div>
            <hr />
        </div>
    </div>
    `
    return html
}

function renderPieChart() {

    let donutChartConfig = {
        chart: {
            height: 350,
            type: 'donut'
        },
        legend: {
            show: true,
            position: 'right'
        },
        dataLabels: {
            enabled: true,
            formatter: function (val, opt) {
                return parseInt(val) + '%';
            }
        },
        plotOptions: {
            pie: {
                donut: {
                    labels: {
                        show: true,
                        name: {
                            fontSize: '2rem',
                            fontFamily: 'Montserrat'
                        },
                        value: {
                            fontSize: '1rem',
                            fontFamily: 'Montserrat',
                            formatter: function (val) {
                                return parseInt(val);
                            }
                        },
                        total: {
                            show: true,
                            fontSize: '1.5rem',
                            label: 'Нийт',
                            // formatter: function (w) {
                            //     return '31%';
                            // }
                        }
                    }
                }
            }
        },
        responsive: [
            {
                breakpoint: 992,
                options: {
                    chart: {
                        height: 380
                    }
                }
            },
            {
                breakpoint: 576,
                options: {
                    chart: {
                        height: 320
                    },
                    plotOptions: {
                        pie: {
                            donut: {
                                labels: {
                                    show: true,
                                    name: {
                                        fontSize: '1.5rem'
                                    },
                                    value: {
                                        fontSize: '1rem'
                                    },
                                    total: {
                                        fontSize: '1.5rem'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ]
    };

    pies.map(
        ({ question, label, data }) =>
        {
            let donutChartEl = document.querySelector(`#donut-${question.id}-chart`)
            donutChartConfig['labels'] = label
            donutChartConfig['series'] = data
            let donutChart = new ApexCharts(donutChartEl, donutChartConfig);
            donutChart.render();
        }
    )
}

function renderBarChart() {
    let lineChartConfig = {
        chart: {
            height: 400,
            type: 'bar',
            zoom: {
                enabled: false
            },
            parentHeightOffset: 0,
            toolbar: {
                show: false
            }
        },
        markers: {
            strokeWidth: 7,
            strokeOpacity: 1,
            strokeColors: [window.colors.solid.white],
            colors: [window.colors.solid.warning]
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'straight'
        },
        colors: [window.colors.solid.warning],
        grid: {
            xaxis: {
                lines: {
                    show: true
                }
            },
            padding: {
                top: -20
            }
        },
        tooltip: {
            custom: function (data) {
                return (
                    '<div class="px-1 py-50">' +
                    '<span>' +
                    data.series[data.seriesIndex][data.dataPointIndex] +
                    '</span>' +
                    '</div>'
                );
            }
        },
    }
    bars.map(
        ({ question, label, data }) =>
        {
            let lineChartEl = document.querySelector(`#bar-${question.id}-chart`)
            lineChartConfig['xaxis'] = {
                categories: label
            }
            lineChartConfig['series'] = [
                {
                    data
                }
            ]
            let lineChart = new ApexCharts(lineChartEl, lineChartConfig);
            lineChart.render();
        }
    )
}

function displayLineChart(question)
{
    const [label, data] = getDataLabel(question)
    lines.push({ question, label, data })
    return `<div class="col-12" id="container-${question.id}-con">
        <div class="">
            <h4 class="card-title mb-75"> Хариулсан хугацаа </h4>
            <div class="card-body">
                <div id="line-${question.id}-chart"></div>
            </div>
            <hr />
        </div>
    </div>`
}

function renderLineChart({ custom, type }) {
    let lineChartConfig = {
        chart: {
            height: 400,
            type: type ?? "line",
            zoom: {
                enabled: false
            },
            parentHeightOffset: 0,
            toolbar: {
                show: false
            }
        },
        markers: {
            strokeWidth: 7,
            strokeOpacity: 1,
            strokeColors: [window.colors.solid.white],
            colors: [window.colors.solid.warning]
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'straight'
        },
        colors: [window.colors.solid.warning],
        grid: {
            xaxis: {
                lines: {
                    show: true
                }
            },
            padding: {
                top: -20
            }
        },
        tooltip: {
            custom: custom ? custom : function (data) {
                return (
                    '<div class="px-1 py-50">' +
                    '<span>' +
                        data.series[data.seriesIndex][data.dataPointIndex] +
                    '</span>' +
                    '</div>'
                );
            }
        },
    }
    lines.map(
        ({ question, label, data }) =>
        {
            let lineChartEl = document.querySelector(`#line-${question.id}-chart`)
            lineChartConfig['xaxis'] = {
                categories: label
            }
            lineChartConfig['series'] = [
                {
                    data
                }
            ]
            let lineChart = new ApexCharts(lineChartEl, lineChartConfig);
            lineChart.render();
        }
    )
}

function displayUsers(users)
{
    let html = `<div class="col-12">
        <div class="">
            <h4 class="card-title mb-75"> Оролцсон хүмүүс </h4>
            <div class="card-body">
                <ul class="list-group">
                    ${
                        users.map(
                            ({ user, count }) => {
                                return `<li class="list-group-item">
                                            <div class="avatar avatar-border">
                                                <img
                                                    src="${user.img ? user.img : "/media/53x53.jpg"}"
                                                    alt="avatar"
                                                    height="42"
                                                    width="42"
                                                    onerror="this.onerror=null; this.src='/media/53x53.jpg'"
                                                >
                                            </div>
                                            ${user.name}
                                            <p class="pb-0 mb-0">
                                                <small>${count} хариулт илгээсэн</small>
                                            </p>
                                        </li>`
                            }
                        ).join("")
                    }
                </ul>
            </div>
            <hr />
        </div>
    </div>`
    return html
}

function displayGeneralCharts(data)
{
    generalTab.html("")
    let html = displayLineChart({ id: 'ognoo', 'pollees': data.pollees })
    generalTab.append(html)
    renderLineChart(
        {
            custom: function (_data) {
                        return (
                            '<div class="px-1 py-50">' +
                            '<span>' +
                                _data.series[_data.seriesIndex][_data.dataPointIndex] + " хариулсан" +
                            '</span>' +
                            '</div>'
                        )
                    },
            type: "area",
        }
    )

    //  Ажилтны харуулах checkbox той байвал
    if (!surveyDetail.is_hide_employees)
    {
        let html = displayUsers(data.poll_users)
        generalTab.append(html)
    }
}

function renderCharts()
{
    setTimeout(() => {
        renderPieChart()
        renderBarChart()
    }, 50);
}

/**
KIND_ONE_CHOICE = 1 // 'Нэг сонголт'
KIND_MULTI_CHOICE = 2 // 'Олон сонголт'
KIND_BOOLEAN = 3 // 'Тийм // Үгүй сонголт'
KIND_RATING = 4 // 'Үнэлгээ'
KIND_TEXT = 5 // 'Бичвэр'
*/

function displayProcessCharts(surveyData) {

    pies = []
    bars = []

    questionsProcess.html("")
    let chartKinds = {
        [KIND_BOOLEAN]: displayPieChart,
        [KIND_ONE_CHOICE]: displayPieChart,
        [KIND_MULTI_CHOICE]: displayBarChart,
        [KIND_RATING]: displayBarChart,
        [KIND_TEXT]: displayAnswers,
    }
    useLoader(
        fetchData(`/survey/${surveyData.id}/pollees/`),
        processCharts.parent()
    )
        .catch(err => err)
        .then(
            ({ success, data, errors }) => {
                if (success) {
                    const questions = data.questions
                    displayGeneralCharts(data)
                    questionsProcess.append(displayPrintBtn())
                    questions.questions.map(
                        (q, idx) => {
                            const questionKind = q.kind
                            const fn = chartKinds[questionKind]
                            let _chart = fn(q)
                            questionsProcess.append($(_chart))
                        }
                    )
                }
            }
        )
        .finally(
            () =>
            {
                renderCharts()
            }
        )
}
