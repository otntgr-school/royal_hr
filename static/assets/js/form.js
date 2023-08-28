class CForm
{
    /**
     * Формтой холбоотой
     * @param {HTMLFormElement} event form ийн event
     */
    constructor(event, validate)
    {
        this.event = event
        this.data = this.getValuesFromForm()
        this.validate = validate
    }

    /** validate ийг форм дээр нэмэх */
    static validate(formId, fields)
    {
        var form = $(formId);

        let validate = form.validate({
            rules: fields
        });
        return validate
    }

    /** Формоос input үүдийн утгыг object болгож авах нь */
    getValuesFromForm()
    {
        const formData = new FormData(this.event.target)
        const data = Object.fromEntries(formData)
        return data
    }

    /** Формын дагуу хүсэлтийг явуулах нь
     * @param {string} url submit дарах url
     * @param {Object} fetchOptions.method хүсэлт явуулах method
     * @param {Object} options.reload хүсэлт амжилттай болсны ард ээр table reload хийх эсэх
    */
    async submit(url, fetchOptions, options)
    {
        if(!this.validate.checkForm())
        {
            return
        }

        const { success, errors } = await fetchData(url, data, fetchOptions.method)
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
            setInitForm()
            if (options.reload)
            {
                table.ajax.reload(null, true)
            }
        }
    }
}
