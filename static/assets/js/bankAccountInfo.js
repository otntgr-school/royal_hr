var editBankAccountInfoJqFrom = $('#editBankAccountInfoForm')
const editBankLoader = document.getElementById('loaderWeew8')
let validateEditBankAccountInfo
let bankAccountList = $("#bank-account-list")
let bankData = null
let editId = null

function select2OptionChange(option) {
    if(!('title' in option))
        return option

    var bankInfo = $(`
                    <div class="d-flex justify-content-start">
                        <div class="avatar avatar-border">
                            <img
                                src='${option.title ? `/media/${option.title}` : "/media/53x53.jpg"}'
                                alt="avatar"
                                height="25"
                                width="25"
                                onerror="this.onerror=null; this.src='/media/53x53.jpg'"
                            />
                        </div>
                        <div>
                            <h5 style="margin: 3px 2px;">${option.text}</h5>
                        </div>
                    </div>
                `);
    return bankInfo;
}

$("#bankInfoSelect").select2({
    templateResult: select2OptionChange,
    templateSelection: select2OptionChange
});

$("#editBankInfoSelect").select2({
    templateResult: select2OptionChange,
    templateSelection: select2OptionChange
});

/** Банкын нэг айтем */
function bankAccountItem(data)
{
    console.log();
    let html = `
    <div class="cardMaster border rounded p-2 mb-1">
        <div class="d-flex justify-content-between flex-sm-row flex-column">
            <div class="d-flex flex-row align-items-center mb-50">
                <div class="avatar avatar-border m-50">
                    <img
                        src='${data.bank_info.image ? `${data.bank_info.image}` : "/media/53x53.jpg"}'
                        alt="avatar"
                        height="35"
                        width="35"
                        onerror="this.onerror=null; this.src='/media/53x53.jpg'"
                    />
                </div>
                <div class="user-info">
                    <h6 class="mb-0">${data.bank_info.name}</h6>
                    <p class="mb-0">${data.number}</p>
                </div>
            </div>
            <div class="d-flex flex-column text-start text-lg-end">
                <div class="d-flex order-sm-0 order-1 mt-1 mt-sm-0">
                    <button class="btn btn-outline-primary me-75 waves-effect" onclick="editAccountInfo(${data.id})">
                        Засах
                    </button>
                    <button class="btn btn-outline-danger waves-effect" onclick="deleteAccountInfo(${data.id})">Устгах</button>
                </div>
            </div>
        </div>
    </div>
    `
    return html
}

// Ирсэн датааг тухайн жагсаалт харуулах div-д хийх нь
function loopData(data)
{
    bankData = data
    $('#haventBankAccount').hide()

    if (bankData && bankData.length >= 1)
    {
        if (document.getElementById('workerIndexBankAccountButton'))
        {
            document.getElementById('workerIndexBankAccountButton').style.display = 'none'
        }

        if (document.getElementById('employeeAddBankAccountButton'))
        {
            document.getElementById('employeeAddBankAccountButton').style.display = 'none'
        }
    }

    data.map(function(bankAccountInfo)
        {
            html = bankAccountItem(bankAccountInfo)
            bankAccountList.append(html)
        })
}

/** Банкуудыг дуудах нь */
async function getDatas(pk=null)
{
    if(pk)
    {
        const { data, success, errors } = await fetchData(`/bank/bank-account-list/${pk}/`, null, 'GET')
        if(success && data && data.length > 0)
        {
            loopData(data)
        }
    }
    else
    {
        const { data, success, errors } = await fetchData(`/bank/bank-account-list/`, null, 'GET')
        if(success && data && data.length > 0)
        {
            loopData(data)
        }
    }
}

async function deleteAccountInfo(id)
{
    const { success, data } = await fetchData(`/bank/bank-account-info-create/${id}/`, null, 'DELETE')
    if(success)
    {
        location.reload();
    }
}

function editAccountInfo(data)
{
    const bankAccountInfo = bankData.find(eachdata => eachdata.id===data)
    editId = bankAccountInfo.id
    $(`#editNumber`).val(bankAccountInfo.number).change()
    $(`#editBankInfoSelect`).val(bankAccountInfo.bank).change()
    $('#editBankAccountModal').modal('show');
}

if (editBankAccountInfoJqFrom.length) {
    validateEditBankAccountInfo = editBankAccountInfoJqFrom.validate({
        rules: {
            "bankInfoSelect": {
                required: true,
            },
            "number": {
                required: true
            },
        },
        messages: {
            'bankInfoSelect': {
                required: 'Банк талбарыг бөглөнө үү.',
            },
            'number': {
                required: 'Дансны дугаар талбарыг бөглөнө үү.',
            },
        }
    });
}
const editBankAccountInputs = ['editBankInfoSelect','editNumber']
const editBankAccountInfoSubmit = async (event, employeeID=null) =>
{
    event.preventDefault()
    if(!validateEditBankAccountInfo.checkForm())
    {
        return
    }
    const generalBody = {}
    const editAccountInfoSubmit = document.getElementById('editbankAccountInfoSubmitBtn')

    editBankAccountInputs.map(
        (input) =>
        {
            const domElement = document.getElementById(input)
            let elemetValue = domElement.value
            generalBody[input] = elemetValue
        }
    )
    editAccountInfoSubmit.disabled = true
    editBankLoader.classList.add('loaderWew')
    if (!employeeID)
    {
        const { success, errors } = await fetchData(`/bank/bank-account-info-create/${editId}/`, generalBody, 'PUT').catch(err => err)
        .finally(() => { editAccountInfoSubmit.disabled = false; contactLoader.classList.remove('loaderWew') })
        if(errors)
        {
            // input ийг validate алдаа г харуулах
            displayError(errors)
        } else {
            // input ийн харагдсан байгаа validate алдаануудыг устгах
            deleteError(errors)
        }
        // амжилтатй үүсвэл id ирээд form цэвэрлэх
        if(success)
        {
            location.reload();
            editAccountInfoSubmit.disabled = true
            document.querySelector('#editbankAccountInfoSubmitBtn').click()
            setTimeout(() => {
                editAccountInfoSubmit.disabled = false
            }, 100);
        }
    }
    else
    {
        const { success, errors } = await fetchData(`/bank/bank-account-info-create/${editId}/${employeeID}/`, generalBody, 'PUT').catch(err => err)
        .finally(() => { editAccountInfoSubmit.disabled = false; contactLoader.classList.remove('loaderWew') })
        if(errors)
        {
            // input ийг validate алдаа г харуулах
            displayError(errors)
        } else {
            // input ийн харагдсан байгаа validate алдаануудыг устгах
            deleteError(errors)
        }
        // амжилтатй үүсвэл id ирээд form цэвэрлэх
        if(success)
        {
            location.reload();
            editAccountInfoSubmit.disabled = true
            document.querySelector('#editbankAccountInfoSubmitBtn').click()
            setTimeout(() => {
                editAccountInfoSubmit.disabled = false
            }, 100);
        }
    }
}
