let worksList = $(".today-works-list")

/** Back аас датануудаа авах нь */
function getWorkList()
{
    useLoader(fetchData('/work-calendar/today/'), worksList)
        .then(
            ({ success, data }) =>
            {
                if (success)
                {
                    if(Object.keys(data).length > 0)
                    {
                        function sortTime(a, b)
                        {
                            if ( a.today_time < b.today_time ){
                                return -1;
                            }
                            if ( a.today_time > b.today_time ){
                                return 1;
                            }
                            return 0;
                        }
                        data.sort(sortTime).map(function(eachData)
                        {
                            addRow(eachData)
                        })
                    }
                    else
                    {
                        parentDiv = document.getElementById('today-activate')
                        parentDiv.style.display = 'flex'
                        parentDiv.style.alignItems = 'center'
                        parentDiv.style.justifyContent = 'center'
                        const div = document.createElement('div');
                        div.className = 'row';
                        div.innerHTML = `
                        <div>
                            <div class="col-12 col-md-6" style="width:auto;display:flex; justify-content: center; align-items: center;">
                                ${feather.icons["file"].toSvg({
                                    class: "avatar-icon",
                                    style: `color:${data.color}; width:30%; height:30%`,
                                })}
                            </div>
                            <div class="avatar-icon font-medium-3" style="width: auto; padding-left: 5px;">
                                Үйл ажиллагаа байхгүй...
                            </div>
                        </div>
                        `;
                        parentDiv.appendChild(div);
                    }
                    document.getElementById('today-title').innerText =`Танд өнөөдөр ${Object.keys(data).length} үйл ажиллагаа байна`
                }
            }
        )
}

getWorkList()
// today-activate

function addRow(data) {
    const div = document.createElement('div');
    div.innerHTML = `
    <div class="transaction-item row">
        <div class="col-12 col-md-6">
            <div class="avatar float-start bg-light-primary rounded me-1">
                <div class="avatar-content">
                        ${feather.icons["feather"].toSvg({
                        class: "avatar-icon font-medium-3",
                        style: `color:${data.color}`,
                    })}
                </div>
            </div>
            <div class="more-info">
                <h6 class="mb-0">${data.title}</h6>
                <small>${data.work_title}</small>
            </div>
        </div>
        <div class="col-12 col-md-6 mt-1 mt-md-0">
            <div class="avatar float-start bg-light-primary rounded me-1">
                <div class="avatar-content">
                        ${feather.icons["calendar"].toSvg({
                        class: "avatar-icon font-medium-3",
                        style: `color:${data.color}`,
                    })}
                </div>
            </div>
            <div class="more-info">
                <h6 class="mb-0">${data.today_time ?? "Өнөөдөр"}</h6>
                <small>${data.location ?? "-"}</small>
            </div>
        </div>
    </div>
    <hr>
    `;
    document.getElementById('today-activate').appendChild(div);
}
