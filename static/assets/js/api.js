const blockOptions = {
    message:
        '<div class="d-flex justify-content-center align-items-center"><p class="me-50 mb-0">Уншиж байна...</p><div class="spinner-grow spinner-grow-sm text-white" role="status"></div>',
    css: {
        backgroundColor: 'transparent',
        color: '#fff',
        border: '0'
    },
    overlayCSS: {
        opacity: 0.5
    }
}

/** Loader харуулах */
function addLoader(section)
{
    //  section байвал тухайн section дээр loader харуулна
    if (section)
    {
        section.block(blockOptions)
    }
    //  эсвэл хуудас даяар loader харуулна
    else {
        $.blockUI(blockOptions)
    }
}

/** loader ийг арилгах нь */
function rmLoader(section)
{
    if (section)
    {
        section.unblock()
    }
    else
    {
        $.unblockUI()
    }
}

const noBodyRequests = [ 'GET', 'DELETE' ]

/**
 * Формын error ийг ajax errors ирэх үед input ийн доор алдааг харуулах
 * @param {Object} errors back аас ирсэн erros
 */
const displayError = (errors) =>
{
    for( const error in errors )
    {
        const errorAlreadyDisplay = document.getElementById(error + 'Error')
        if(errorAlreadyDisplay) return
        let errorElement = document.createElement('div')
        errorElement.id = error + 'Error'
        errorElement.classList.add("errorFromBack")
        errorElement.style.fontSize = '12px'
        errorElement.textContent = errors[error]
        if(document.getElementById(error)?.parentElement)
        {
            let inputsFather = document.getElementById(error).parentElement
            if (inputsFather.classList.contains('input-group'))
            {
                inputsFather = inputsFather.parentElement
            }
            inputsFather.appendChild(errorElement)
        }
    }
}

/**
 * input ийн доор байрлах бүх error ийг арилгах нь
 * @param {*} errorz
 */
const deleteError = (errorz) =>
{
    const errors = document.querySelectorAll('.errorFromBack');
    errors.forEach(error => {
        error.remove();
    });

    if(errorz)
    {
        for( const error in errorz )
        {
            let errorElement = document.createElement('div')
            errorElement.classList.add("error")
            errorElement.textContent = errors[error][0]
            if(document.getElementById(error)?.parentElement)
            {
                const inputsFather = document.getElementById(error).parentElement
                inputsFather.appendChild(errorElement)
            }
        }
    }
}

let initOptions = {
    message: true
}
async function fetchData(url = '', data = {}, method = 'GET', contentType = 'application/json', needParse=true, opts={}) {
    const options = { ...initOptions, ...opts }
    var token = document.cookie.split(';').find(e => e.trim().startsWith('csrftoken'))
    token = token.split('csrftoken=')[1]
    const requestOptions = {
        method: method,
        credentials: 'same-origin',
        headers: {
            ...contentType ? { 'Content-Type': contentType, } : {},
            "X-CSRFToken": token
        },
    }

    if(!noBodyRequests.includes(method)) {
        if (needParse)
        {
            requestOptions.body = JSON.stringify(data)
        }
        else {
            requestOptions.body = data
        }
    }

    const response = await fetch(url, requestOptions)
    if(response)
    {
        const { data, success, info , error, errors, warning } = await response.clone().json()
        if(errors)
        {
            // input ийг validate алдаа г харуулах
            displayError(errors)
        } else {
            // input ийн харагдсан байгаа validate алдаануудыг устгах
            deleteError(errors)
        }
        if(success && info)
        {
            options.message
            &&
            toastr['success']('', info.message, {
                timeOut: 2500,
                closeButton: true,
                hideDuration: 200,
                progressBar: true,
                newestOnTop: true
            })
        }
        if(!success && warning)
        {
            options.message
            &&
            toastr['warning']('', warning.message, {
                timeOut: 2500,
                closeButton: true,
                hideDuration: 200,
                progressBar: true,
                newestOnTop: true
            })
        }
        if(!success && error)
        {
            options.message
            &&
            toastr['error']('', error.message, {
                timeOut: 2500,
                closeButton: true,
                hideDuration: 200,
                progressBar: true,
                newestOnTop: true
            })
        }
    }
    return response.json()
};

/**  */
async function useLoader(fetch, section)
{
    addLoader(section)
    const rsp = await fetch.catch((err) => err)
    rmLoader(section)
    return rsp
}
