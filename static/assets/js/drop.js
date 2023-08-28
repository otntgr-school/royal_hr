let newImages = []
let removeImgIds = []

let initText = "Файл оруулна уу"
let dropArea = document.getElementById('cdrop-area')
let dropText = document.getElementById("cdrop-text")
let gallery = document.getElementById("gallery")
const fileInputs = dropArea.getElementsByTagName("input")
const fileInput = fileInputs.item(0)
dropText.innerText = initText

dropText.addEventListener("click", () =>
{
    fileInput.click()
})

fileInput.addEventListener("change", (e) =>
{
    e.preventDefault()
    e.stopPropagation()
    let files = e.target.files
    handleFiles(files)
})

;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false)
})

function preventDefaults (e) {
    e.preventDefault()
    e.stopPropagation()
}

;['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
})

;['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
})

function highlight(e) {
    dropArea.classList.add('highlight')
    dropText.innerText = "Ийшээ тавина уу"
}

function unhighlight(e) {
    dropArea.classList.remove('highlight')
    dropText.innerText = initText
}

function checkAcceptType(files)
{
    const newFiles = []
    for (const idx in files)
    {
        const file = files[idx]
        if (file.type && fileInput.accept.includes(file.type))
        {
            newFiles.push(file)
        }
    }
    return newFiles
}

dropArea.addEventListener('drop', handleDrop, false)
function handleDrop(e) {
    let dt = e.dataTransfer
    let files = dt.files

    files = checkAcceptType(files)

    handleFiles(files)
}

function handleFiles(files) {
    files = [...files]
    files.forEach(uploadFile)
    files.forEach(previewFile)
}

function uploadFile(file) {
    newImages.push(file)
}

/** Зургийг устгах нь */
function handleDelete(event)
{
    const imgContainer = $(event.target).parents(".cgallery-item")
    const img = imgContainer.find("img")
    const imgId = img.attr("id")
    if (imgId)
    {
        removeImgIds.push(imgId)
    }
    imgContainer.remove()
}

/** Зураг мөн эсэхийг шалгах нь */
function checkIsImage(type)
{
    let allowedExts = ['.avif']
    if (type.startsWith("image") || allowedExts.includes(type)) {
        return true
    }
    return false
}

/** Оруулсан файл болон зургийг харуулах нь */
function setImage(imageSrc, imageName, imageId='')
{
    let parent = document.createElement("div")
    parent.className = "col-12 col-md-6 cgallery-item"

    let img = document.createElement('img')
    img.id = imageId
    img.src = imageSrc

    let actions = document.createElement("div")
    actions.className = 'actions'
    actions.innerHTML = `
        <div>
            ${
                imageId
                ?
                    `<a
                        href="/download-attachment/?attachId=${imageId}"
                        class="cdownload cbtn"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top"
                        data-bs-original-title="Устгах"
                    >
                        ${feather.icons['download'].toSvg(
                            {
                                class: "text-info cicon"
                            }
                        )}
                    </a>`
                :
                    ""
            }
            <span
                role="button"
                class="cdelete cbtn" onclick="handleDelete(event)"
                data-bs-toggle="tooltip"
                data-bs-placement="top"
                data-bs-original-title="Устгах"
            >
                ${feather.icons['trash'].toSvg(
                    {
                        class: "text-danger cicon"
                    }
                )}
            </span>
        </div>
    `

    let name = document.createElement("span")
    name.innerText = imageName

    parent.appendChild(actions)
    parent.appendChild(img)
    parent.appendChild(name)
    gallery.appendChild(parent)
}

/** Файл нь хэрвээ зураг байвал тухайн зургийг харуулна
 * Зургаас өөр файл байвал зүгээр файлын png харуулна
 */
function previewFile(file) {
    if (checkIsImage(file.type))
    {
        let reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onloadend = function() {
            setImage(reader.result, file.name)
        }
    }
    else {
        setImage('/media/file400x400.png', file.name)
    }
}

/** Back аас ирсан файлын жагсаалтыг харуулах нь */
function displayFiles(attachments)
{
    attachments.map(
        (attach, idx) =>
        {
            if (attach.has_file)
            {
                if (checkIsImage(attach.mime_type ?? attach.ext)) {
                    setImage(attach.url, attach.name, attach.id)
                }
                else {
                    setImage('/media/file400x400.png', attach.name, attach.id)
                }
            }
        }
    )
}

/** Хоослох */
function resetGallery()
{
    newImages = []
    removeImgIds = []
    gallery.innerHTML = ""
    fileInput.value = ""
}

if (jQuery?.validator)
{
    jQuery.validator.addMethod("checkDrop", function(value, element) {
        return gallery.childNodes.length > 0
    }, "Файл оруулаагүй байна");

    jQuery.validator.addMethod("sizeDrop", function(value, element) {
        let check = true

        if (!element?.files || !element?.files.length)
        {
            return true
        }

        for (const file of element.files)
        {
            if (file.size > 3 * 1024 * 1024)
            {
                check = false
                break
            }
        }
        return check
    }, "нэг файлын хэмжээ 3мб аас хэтэрсэн байна");
}
