/** **Баганыг нууж хаахыг хүсвэл үүнийг ажиллуулах**
 * - Анхнаасаа харагдахгүй байлгие гэвэл selector-ын ардаас `disabled text-decoration-line-through` залгаж бичнэ.
 * @param {string} table Datatable-ийн утга
 * @param {string} selector selector-уудад аль datatable гэдгийг илэрхийлэх className
*/
function toggleColumns(table, selector='.toggle-vis')
{
	function _hide(_el)
	{
		// Get the column API object
		var column = table.column(_el.attr('data-column'));

		// Toggle the visibility
		column.visible(!_el.hasClass("disabled text-decoration-line-through"));
	}

	$(selector).each(
		(index, el) =>
		{
			_hide($(el))
		}
	)

	$(selector)
		.off('click')
		.on('click', function (e) {
			e.preventDefault();
			$(this).toggleClass("disabled text-decoration-line-through")
			_hide($(this))
		});
}

/**
 * Datable ийн header ийг хуулж input гаргах нь
 * @param {string} dtClass тухайн datatable ийг гэж илэрхийлэх class or id example: .user-datatable
 */
function cloneHeader(dtClass, fixedOptions)
{
    //  HEADER ийг хуулж авах нь
    $(`${dtClass} thead tr`)
        .clone(true)
		.addClass("filters")
        .appendTo(`${dtClass} thead`)
}

/**
 * Fixed Header тэй үед хөлөөр хайя
 * @param {string} dtClass тухайн datatable ийг гэж илэрхийлэх class or id example: .user-datatable
 * @param {Array} showSearchIndexs тухайн datatable ийн хайх input гаргах column ийн index үүдийг өгнө
 */
function cloneFooter(dtClass, cloneHeaders, inputOptions)
{
	let filterContainer = $(`${dtClass} thead tr.filter-container`)
	//  Footer ийг хуулж авах нь
	$(`${dtClass} tfoot th`).each(function(i)
	{
		if (cloneHeaders.includes(i))
		{
			var title = $(this).text();
			let toFilter = filterContainer.length ? filterContainer : $(this)
			let html = `
				${
					inputOptions?.[i]?.type == "select"
					?
						`
							<select data-index="${i}" class="form-select form-select-sm ${inputOptions[i].class ?? ""}">
								${!inputOptions[i].noEmpty && `<option value="">-- Сонгоно уу --</option>`}
								${
									inputOptions[i].options.map(
										(opt, idx) =>
											`<option value="${opt.id}">${opt.name}</option>`
									).join(" ")
								}
							</select>
						`
					:
						`
						<input type="text" class="form-control form-control-sm ${inputOptions?.[i]?.class ?? ""}" placeholder="${title} хайх" data-index="${i}"/>
						`
				}
			`
			filterContainer.length
			?	toFilter.append(`<th style="padding: 5px 2.5px 5px 2.5px!important">${html}</th>`)
			:	toFilter.html(html)
		}
		else {
			filterContainer.length
			? 	filterContainer.append("<th></th>")
			:	$(this).text("")
		}
	})
}

/** хөлөөр хайсан input ээр хайх нь */
function searchFooter(dtable)
{
	let filterContainer = $(dtable.table().container()).find(`thead tr.filter-container`)
	// let filterContainer = $(`${dtClass} )

	let inputSelector = filterContainer.length ? 'thead tr.filter-container input' : 'tfoot input'
	let selectSelector = filterContainer.length ? 'thead tr.filter-container select' : 'tfoot select'
	$( dtable.table().container() ).on( 'keyup', inputSelector,  _throttle(function() {
        dtable
            .column( $(this).data('index') )
            .search( this.value )
            .draw();
    }, 1000 ));
	$( dtable.table().container() ).on( 'change', selectSelector, function() {
        dtable
            .column( $(this).data('index') )
            .search( this.value )
            .draw();
    });
}

const _throttle = (func, delay) => {
	let lastFunc
	let lastRan
	let context
	let args

	const timeOutFunc = () =>
	{
		if ((Date.now() - lastRan) >= delay)
		{
			func.apply(context, args);
			lastRan = Date.now();
		}
	}

	return function()
	{
		context = this;
		args = arguments;

		if (!lastRan)
		{
			func.apply(context, args)
			lastRan = Date.now();
		}
		else
		{
			clearTimeout(lastFunc);
			lastFunc = setTimeout(timeOutFunc, delay - (Date.now() - lastRan));
		}
	}
}

/**
 * datatable ийн input үүдээр хайх нь
 * @param {string} api тухайн datatable ийг гэж илэрхийлэх
 * @param {Array} showSearchIndexs тухайн datatable ийн хайх input гаргах column ийн index үүдийг өгнө
 */
function searchColumn(api, showSearchIndexs)
{
	api
		.columns()
		.eq(0)
		.each(
			function (index)
			{
				var cell = $('.filters th').eq(
					$(api.column(index).header()).index()
				);
				if (showSearchIndexs.includes(index))
				{
                    var title = $(cell).text();
					$(cell).html('<input type="text" class="form-control form-control-sm" placeholder="Search ' + title + '" />');
					$('input', cell).off('keyup change').on('keyup change', function () {
							if (api.column(index).search() !== this.value)
							{
								api.column(index).search(this.value).draw();
							}
						});
				}
				else {
					$(cell).html("")
				}
			}
		)
}

/**
 * Аль ID сонгож түүн дээр хийгдэх үйлдэл
 * @param {Function} callbackFn Ямар функцийг ажиллуулах функцийн нэр
 */
const changeChoosedId = (callbackFn) =>
{
	const deletebtn = document.getElementById("deletebtn")
	deletebtn.onclick = callbackFn
}


const QUANTITY_REGEX = /(.)(?=(\d{3})+$)/g
const EMAIL_REGEX = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
const REGISTER_NUMBER_REGEX = /[a-яА-Я]{2}[0-9]{8}/
const fullZero = (num, spliceNo=-2) => ("0" + num).slice(spliceNo)
function timeZoneToDateString(timezone, hasHour=true, symbol="-", hasMs=false)
{

    if(timezone === '') return timezone

    const date = new Date(timezone)

    /** сар */
    const month = fullZero(date.getMonth() + 1)
    /** өдөр */
    const day = fullZero(date.getDate())
    /** жил */
    const year = date.getFullYear()

    /** цаг */
    const hour = fullZero(date.getHours())
    /** минут */
    const minute = fullZero(date.getMinutes())
    /** с */
    const seconds = fullZero(date.getSeconds())
    /** мс */
    const ms = date.getMilliseconds()

    const hours = `${hour}:${minute}:${seconds}${hasMs ? `:${ms}` : ""}`

    const full = `${year}${symbol}${month}${symbol}${day}${hasHour ? " " + hours : ""}`

    return full
}

function bytesToSize(bytes) {
	const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
	if (bytes === 0) return 'n/a'
	const i = parseInt(Math.floor(Math. log(bytes) / Math.log(1024)), 10)
	if (i === 0) return `${bytes} ${sizes[i]})`
	return `${(bytes / (1024 ** i)).toFixed(1)} ${sizes[i]}`
}

const quantityFormat = (quantity) =>
{
    let numQuantity = parseFloat(quantity)
    if(numQuantity < 0) return null
    if(isNaN(numQuantity)) return 0
    return String(numQuantity).replace(QUANTITY_REGEX, '$1,')
}

function shuffle(array) {
	let currentIndex = array.length,
		randomIndex

	// While there remain elements to shuffle.
	while (currentIndex != 0) {
		// Pick a remaining element.
		randomIndex = Math.floor(Math.random() * currentIndex)
		currentIndex--

		// And swap it with the current element.
		;[array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]]
	}

	return array
}

// attach id өгөхөд татна.. Attach list ээ харуулсан бол onclick дээрн энэ function дуудаад id гаа дамжуул
const handleDownloadAttach = async (id) =>
{
	window.open("/download-attachment/?attachId=" + id, '_blank');
}

// Аттач жагсаалт харуулах... tools дотор байгаа modal html ийн include хийж оруулж байгаад ашиглана
const getAttachmetsList = async (url, id, elemId="attachemtsDiv") =>
{
	const { success, data: { attachments } } = await fetchData(`${url}${id}/`, null, 'GET')
	// Modal ний дотох div. tools гэсэн folder дотор байгаa
	const attachemtsDiv = document.getElementById(elemId)
	if(success)
	{
		if(!attachments || attachments.length === 0)
		{
			attachemtsDiv.innerHTML = "<div class='text-center mt-3'>Илэрц олдсонгүй</div>"
			return
		}
		attachemtsDiv.innerHTML = attachments.map(
			(attach, index) =>
			{
				return `
					<div class='row mt-1 mb-1'>
						<div class='col-6' style='
							text-align: left;
							white-space: nowrap;
							overflow: hidden;
							text-overflow: ellipsis;
							'
						>
							${index + 1}. ${attach.name}
						</div>
						<div class='col-2'>${attach.size}</div>
						<div class='col-2'>${timeZoneToDateString(attach.created_at, false)}</div>
						${
							attach.has_file
							?
								`
								<div class='col-2 text-danger cursor-pointer' style='text-decoration: underline' value='Download' onclick='handleDownloadAttach(${attach.id})'>
									Татах
								</div>
								`
							:
								"<small>Файл устсан байна</small>"
						}
					</div>
					${(attachments.length - 1) !== index ? "<div class='row' style='height: 1px; background-color: grey'></div>" : ""}
				`
			}
		).join("")
	}
	else
	{
		attachemtsDiv.innerHTML = "<div class='text-center mt-3'>Илэрц олдсонгүй</div>"
	}
}
