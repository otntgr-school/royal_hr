function renderPDF(pdfs, selector, options) {
    var options = options || { scale: 1 };

    let container = $(selector)
    container.html("")

    pdfs.map(
        (pdf, idx) =>
        {
            container.append(`
                <embed src="${pdf.url}" type="application/pdf" height="700px" style="width: 100%;">
            `)
        }
    )

}
