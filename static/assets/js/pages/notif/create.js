const ALL_SCOPE = 7

let scopeKindInputs = $("input[name='scope_kind']"),
    cTree = $("#data-tree"),
    notifForm = $("#notif-action")

/** Ажилтнуудыг харуулах нь */
function renderTree(data)
{
    cTree
        .jstree(
            {
                "core" : {
                    "multiple" : true,
                    'data' : data
                },
                plugins: ['types', 'checkbox'],
                types: {
                    default: {
                        icon: 'fad fa-sitemap text-primary-green'
                    },
                    sub: {
                        icon: 'fas fa-landmark text-primary'
                    },
                    sub1: {
                        icon: 'far fa-circle text-success'
                    },
                    sub2: {
                        icon: "far fa-circle text-success"
                    },
                    sub3: {
                        icon: 'far fa-circle text-success'
                    }
                }
            }
        )
}

function destroyTree()
{
    cTree.jstree("destroy");
}

/** ЖАгсаалт формын сонголтуудыг дуудах нь */
async function getChoicesOptions(kindId)
{
    const rsp = await fetchData(`/notif/choice/${kindId}/`, "", "GET")
    const { success, data, errors } = rsp
    if (success)
    {
        destroyTree()
        renderTree(data)
    }
    return rsp
}

scopeKindInputs.on("change", (event) =>
{
    const kindId = event.target.value
    if (kindId === ALL_SCOPE + "")
    {
        destroyTree()
        cTree.text("Бүх хүнд")
        return
    }
    getChoicesOptions(kindId)
})

function getScopeKey(scopeKind)
{
    let keys = {
        "1": "org_",
        "2": "sub_",
        "3": "salbar_",
        "4": "pos_",
        "5": "emp_",
        "6": "user_",
    }
    return keys?.[scopeKind]
}

/** Хмарах хүрээнд сонгогдсон утгуудыг авах нь */
function getScopeIds(scopeKind)
{
    let checkedIds = [];
    let selectedNodes = cTree.jstree("get_checked", true);
    $.each(selectedNodes, function() {
        checkedIds.push(this.id);
    });

    let scopeKey = getScopeKey(scopeKind)

    let filtered = checkedIds
                        .filter(checkedId => checkedId.includes(scopeKey))
                        .map(el => el.replace(scopeKey, ''))

    return filtered
}

jQuery.validator.addMethod("noSpace", function(value, element)
{
    $(element).val(value.trim())
    return true
});

let validate = notifForm.validate({
    rules: {
        'title': { required: true, noSpace: true },
        'content': { required: true, noSpace: true },
        'ntype': { required: true },
        'url': { required: false },
        "from_kind": { required: true },
        "scope_kind": { required: true },
    }
});

function resetForm()
{
    notifForm.trigger("reset");
    destroyTree()
}

/** Болих товч дарах үед */
function handleReset()
{
    resetForm()
}

/** Мэдэгдэл шинээр үүсгэх нь */
function handleSubmit(event)
{
    if(!validate.checkForm())
    {
        return
    }

    event.preventDefault()
    const formData = new FormData(event.target)
    const body = Object.fromEntries(formData)
    const scopeIds = getScopeIds(body.scope_kind)
    body.scope_ids = scopeIds
    useLoader(
        fetchData('/notif/action/', body, 'POST'),
        notifForm,
    )
        .catch(er => er)
        .then(
            ({ success, data, errors }) =>
            {
                if (success)
                {
                    handleReset()
                }
            }
        )
}
