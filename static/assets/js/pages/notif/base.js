let notifContainer = $(".dropdown-notification"),
    notifCount = $(".n-info"), //  шинэ ирсэн мэдэгдлийн тоо харуулах div
    notifList = $(".n-list"),
    nBtn = $(".n-btn"),
    totalNew = 0,
    readNotifIds = new Set()
    countNotif = 0
    notDiv = document.getElementById('notifDiv')
    isEnded = false

const notifLoader = document.getElementById('loaderNotif')

/** Тухайн нэг мэдэгдлийн element */
function displayNotifItem(notif)
{
    let isNew = !readNotifIds.has(notif.id)
    if (isNew)
    {
        readNotifIds.delete(notif.id)
    }
    const div = document.createElement('div');

    div.innerHTML = `
        <a class="d-flex" onclick="handleNotif(event, ${notif.id})" id="notif-${notif.id}-notif" ${notif.url ? `href="${notif.url}"` : ""}>
            <div
                class="list-item d-flex align-items-start position-relative"
            >
                <div class="me-1 d-flex flex-column">
                    <div class="avatar">
                        <img
                            src="${notif.icon ? notif.icon : "/media/53x53.jpg"}"
                            alt="avatar"
                            width="32"
                            height="32"
                            onerror="this.onerror=null; this.src='/media/53x53.jpg'"
                        />
                    </div>
                </div>
                <div class="list-item-body flex-grow-1">
                    <p class="media-heading">
                        <span class="fw-bolder">
                            ${notif.name}:
                        </span>
                        ${notif.title}
                    </p>
                    <small class="notification-text">
                        ${notif.content}
                    </small>
                    <div class="d-flex">
                        <small class="notification-text d-flex align-items-center mb-0">
                            <div class="new-dot" style="background-color: ${notif.lvl_color}; width: 10px; height: 10px"></div>
                            &nbsp; ${notif.lvl_name}
                        </small>
                        <small class="notification-text mb-0 ms-auto">
                            ${timeZoneToDateString(notif.created_at)}
                        </small>
                    </div>
                </div>
                ${isNew ? '<div class="position-absolute new-dot is-new" style="right: 15px; top: 40%;"></div>' : ""}
            </div>
        </a>
    `
    return div
}

/** Уншсанаар гэж фронт дээр тэмдэглэх */
function setRead(id)
{
    let element = $(`#notif-${id}-notif`)
    element.find(".is-new").remove()
    totalNew = totalNew - 1
    setCounts(totalNew)
    if (!totalNew)
    {
        $(".notif-badge").remove()
    }
}

/** Тухайн нэг мэдэгдэл дээр дарах үед уншсан наар тэмдэглэх */
function handleNotif(event, id)
{
    let element = $(`#notif-${id}-notif`)
    let isNew = element.find(".is-new").length
    if (!isNew) return

    fetchData(`/notif/state/${id}/`)
        .catch(err => err)
        .then(
            ({ success, data: isRead, error }) =>
            {
                if (success && isRead)
                {
                    setRead(id)
                }
            }
        )
}

/** Бүх notif ийг уншсан аар тэмдэглэх */
function handleReadAll()
{
    if (!totalNew) return

    useLoader(
        fetchData(`/notif/state/all/`),
        notifList
    )
        .catch(err => err)
        .then(
            ({ success, data: isRead, error }) =>
            {
                if (success)
                {
                    totalNew = 0
                    $(".is-new").remove()
                    $(".notif-badge").remove()
                    notifCount.text(`Шинэ 0`)
                }
            }
        )
}

function setNotifList(notifs)
{
    if (countNotif == 0 && !notifs.length)
    {
        notifList.html(`<span class="d-flex align-items-center text-muted justify-content-center my-2">Танд мэдэгдэл байхгүй байна</span>`)
        return
    }
    notifs.map(
        (notif, idx) =>
        {
            notDiv.appendChild(displayNotifItem(notif))
        }
    )
}

function setCounts(count)
{
    totalNew = count
    notifCount.text(`Шинэ ${count}`)
    if (count)
    {
        let dispCount = parseInt(MAX_NOTIF) < count ? `${MAX_NOTIF}+` : count
        nBtn.append(`<span class="badge rounded-pill bg-danger badge-up notif-badge">${dispCount}</span>`)
    }
}

function firstSetCounts()
{
    notifList.html("")
    useLoader(
        fetchData(`/notif/action-read-count/`),
        notifList,
    )
    .catch(err => err)
    .then(
        ({ success, data, error }) =>
        {
            if (success)
            {
                setCounts(data.new_count)
            }
        }
    )
}

firstSetCounts()

/** Back аас мэдэгдлүүдийг дуудаж харуулах нь */
async function getNotifs(count)
{
    if(!isEnded)
    {
        notifLoader.classList.add('loaderWew')
        const { success, errors, data } = await fetchData(`/notif/action/?count=${count}`, null, 'GET').catch(err => err)
            .finally(() => { notifLoader.disabled = false; notifLoader.classList.remove('loaderWew') })
        if(success)
        {
            data.read_notifs.forEach(item => readNotifIds.add(item))
            setNotifList(data.notifs)
            if(data.notifs.length === 0)
                isEnded = true
        }
    }
}

getNotifs(countNotif)

notDiv.addEventListener('scroll', function ( event ) {
	if (notDiv.offsetHeight + notDiv.scrollTop >= notDiv.scrollHeight-1) {
        countNotif++
        getNotifs(countNotif)
    }
});
