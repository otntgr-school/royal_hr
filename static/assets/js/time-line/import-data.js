
const MAX_WINDOW_WIDTH = 1200   // Window max хэмжээ хадгалах хувьсагч
var isData = false              // Дата байгаа эсгийх хадгалах хувьсагч
var maxDivHeigth = 200          // Хамгийн өндөр div-ийн өндөрийг хадгалах хувьсагч
var is_active = false           // Эхлэх div
var dataList = []               // Data хадгалах хувьсагч

function reinitSwiper(swiper) {
    setTimeout(function () {
        swiper.update()
    }, 500);
}

function getMigrationsList(data)
{
    if(data)
    {
        const div = document.createElement('div');
        div.classList.add("timelineCont")
        div.classList.add("col-12")
        div.innerHTML = `
            <div class="row">
                <div class="date col-12 col-md-3">
                    <h2></h2>
                </div>

                <div class="text col-12 col-md-9">
                    <p></p>
                </div>
            </div>
        `;
        document.getElementById("timeline").appendChild(div);

        dataList = sortByDate(data.user_experience, data.employee_data)
        dataList.map(function(eachData)
        {
            if('migration' in eachData)
            {
                addMigration(eachData)
                if(maxDivHeigth < eachData.migration.length * 60 )
                    maxDivHeigth = eachData.migration.length * 60
            }
            else
            {
                addExperience(eachData)
            }
        })

        const div2 = document.createElement('div');
        div2.classList.add("timelineCont")
        div2.classList.add("col-12")
        div2.innerHTML = `
        <div class="row">
            <div class="date col-12 col-md-3">
                <h2></h2>
            </div>
            <div class="text col-12 col-md-9">
                <p></p>
            </div>
        </div>
        `;
        document.getElementById("timeline").appendChild(div2);

        $(function()
        {
            $('#timeline').timelinev(
                {
                    containerDivs:    '.timelineCont',
                    dateDiv:         '.date',
                    textDiv:         '.text',
                    dateHtml:        'h2',
                    textHtml:        'p',
                    dateActiveClass: '.active',
                });
        });

        document.getElementById("timeline").style.height = `${maxDivHeigth + data.employee_data.length * 57 + data.user_experience.length *72}px`;
        const allDateDiv = document.getElementsByClassName("date col-12 col-md-3")
        allDateDiv[allDateDiv.length-1].style.height = `${maxDivHeigth}px`

        data.employee_data.map(function(eachData)
        {
            addSlider(eachData)
        })

        const _swiper = new Swiper('.swiper-hystory',
            {
                speed: 600,
                parallax: true,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev'
                },
            }
        );
        reinitSwiper(_swiper)
        isData=true
        if(window.innerWidth >= MAX_WINDOW_WIDTH)
        {
            document.getElementById("timeline").style.display = "block";
            document.getElementById("testSlider").style.display = "none";
            document.getElementById("haventWorkerHystory").style.display = "none";
        }
        else
        {
            document.getElementById("timeline").style.display = "none";
            document.getElementById("testSlider").style.display = "block";
            document.getElementById("haventWorkerHystory").style.display = "none";
        }
    }
}

// Window size өөрчлөхдэх үед дата байвал аль style аар ажлчны түүхийг харуулыг зохицуулна
function onResize() {
    if(window.innerWidth >= MAX_WINDOW_WIDTH && isData)
    {
        document.getElementById("timeline").style.display = "block";
        document.getElementById("testSlider").style.display = "none";
        document.getElementById("haventWorkerHystory").style.display = "none";
    }
    else if (window.innerWidth <= MAX_WINDOW_WIDTH && isData)
    {
        document.getElementById("timeline").style.display = "none";
        document.getElementById("testSlider").style.display = "block";
        document.getElementById("haventWorkerHystory").style.display = "none";
    }
};
$("#workerHistory").on('hidden.bs.modal', function () {
    window.removeEventListener("resize", onResize)
});
$("#workerHistory").on('show.bs.modal', function () {
    window.addEventListener("resize", onResize)
});

function addMigration(eachData)
{
    const div = document.createElement('div');
    div.classList.add("timelineCont")
    div.classList.add("col-12")
    div.style.height = 'auto'

    if(!is_active)
    {
        div.classList.add("active")
        is_active = true
    }

    div.innerHTML = `
        <div class="row">
            <div class="date col-12 col-md-3">
                <h2>${eachData.org} ${eachData.date_joined}</h2>
            </div>
            <div class="text col-12 col-md-9">
                ${eachData.migration.map(
                    (mig) =>
                    {
                        if(mig.employee_mood === "Ажилд орсон" || mig.employee_mood === "Шилжилт хөдөлгөөн хийсэн")
                        {
                            return `
                            <p>${setText(mig)}</p>
                            `
                        }
                        else
                        {
                            return `
                            <p> - ${feather.icons['user-minus'].toSvg( { style: `color:red`, } ) } ${mig.date_left} ${mig.employee_mood}.</p>`
                        }
                    }
                ).join("")}
            </div>
        </div>
    `;
    document.getElementById('timeline').appendChild(div);
}

// Ажилын түүх text format-лах
function setText(migData)
{
    text = `- `

    if(migData.employee_mood === 'Шилжилт хөдөлгөөн хийсэн')
        text += `
        ${feather.icons['users'].toSvg( {
                style: `color:orange`,
            } )
        }`
    else
        text += `
        ${feather.icons['user-plus'].toSvg( {
                style: `color:green`,
            } )
        }`

    if(migData.date_joined)
        text += ` ${migData.date_joined}`

    if(migData.salbar_new)
        text += ` ${ checkTextToUpper(migData.org_new)} - ${checkTextToUpper(migData.sub_org_new)} - ${checkTextToUpper(migData.salbar_new)} салбард`
    else if(migData.sub_org_new)
        text += ` ${ checkTextToUpper(migData.org_new)} - ${checkTextToUpper(migData.sub_org_new)} дэд байгуулгад`
    else
        text += ` ${ checkTextToUpper(migData.org_new)} байгууллагад`

    if(migData.org_position_new)
        text += ` ${checkTextToUpper(migData.org_position_new)} албан тушаалаар `
    else if(migData.org_position_old)
        text += ` ${checkTextToUpper(migData.org_position_old)} албан тушаалаар `

    if(migData.employee_mood === 'Шилжилт хөдөлгөөн хийсэн')
        text += ` томилогдсон.`
    else
        text += ` ${migData.employee_mood.toLowerCase()}.`

        return text
}

// Text-ийн хамгийн эхний үсгийг том болгон text-ийг тодруулах
function checkTextToUpper(data)
{
    if(data)
        return (data.charAt(0).toUpperCase() + data.slice(1)).bold()
}

//slider-д датаа нэмэх
function addSlider(eachData)
{
    const div = document.createElement('div');
    div.classList.add("swiper-slide")

    div.innerHTML = `
        <div class="title" data-swiper-parallax="-300">
            <h2>${eachData.org} ${eachData.date_joined}</h2>
        </div>
        <div class="text" data-swiper-parallax="-100">
            ${eachData.migration.map(
                (mig) =>
                {
                    if(mig.employee_mood === "Ажилд орсон" || mig.employee_mood === "Шилжилт хөдөлгөөн хийсэн")
                    {
                        return `
                        <p class="card-text">${setText(mig)}</p>
                        `
                    }
                    else
                    {
                        return `
                        <p class="card-text"> - ${feather.icons['user-minus'].toSvg( { style: `color:red`, } ) } ${mig.date_left} ${mig.employee_mood}.</p>`
                    }
                }
            ).join("")}
        </div>
    `;
    document.getElementById('historySwiper').appendChild(div);
}

// Ажлын туршагыг түүхэнд нэмэх
function addExperience(eachData)
{
    const div = document.createElement('div');
    div.classList.add("timelineCont")
    div.classList.add("col-12")
    div.style.height = 'auto'

    if(!is_active)
    {
        div.classList.add("active")
        is_active = true
    }

    div.innerHTML = `
        <div class="row">
            <div class="date col-12 col-md-3">
                <h2>${eachData.worked_place} ${parseInt(eachData.joined_date)}</h2>
            </div>
            <div class="text col-12 col-md-9">
                <p class="card-text"> - ${feather.icons['user-plus'].toSvg( { style: `color:green`, } ) } ${eachData.joined_date} ${checkTextToUpper(eachData.worked_place)} байгууллагад ${checkTextToUpper(eachData.pos)} албан тушаалаар ажилд орсон.</p>
                <p class="card-text"> - ${feather.icons['user-minus'].toSvg( { style: `color:red`, } ) } ${eachData.left_date} Ажлаас гарсан.</p>
            </div>
        </div>
    `;
    document.getElementById('timeline').appendChild(div);
}

// Compare тусламжтай 2 array нэгтгэн sort-лох
function sortByDate(user_experience, employee_data)
{
    var child = user_experience.concat(employee_data)
    child = child.sort(compare)
    return child
}

// Их багыг харьцуулах function
function compare( first, secound ) {
    first_item = first.joined_date.split('-').join('')
    secound_item = secound.joined_date.split('-').join('')

    if ( first_item < secound_item ){
        return -1;
    }
    if ( first_item > secound_item ){
        return 1;
    }
    return 0;
    }
