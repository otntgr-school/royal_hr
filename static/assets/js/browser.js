/** Хэрэглэгч дээр cookie хадгалах нь
 * @param {string}  cookieName  cookie ний нэр
 * @param {any}     cookieValue cookie ний утга
 * @param {number}  exMs        cookie ний утга
*/
function setCookie(cookieName, cookieValue, exMs=( 24 * 60 * 60 * 1000 ))
{
    const date = new Date();
    date.setTime(date.getTime() + ( exMs ));
    let expires = "expires=" + date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}

/** Document дээрх cookie нүүдээс тухайн нэг cookie г авах
 * @param {string} cookieName тухайн авах cookie ний нэр
 */
function getCookie(cookieName)
{
    let name = cookieName + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let cookies = decodedCookie.split(';');
    for(let i = 0; i < cookies.length; i++) {
        let c = cookies[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

/** scroll ийн болиулах нь
 * TODO:  scroll зогсоож байгааг сайжруулах
 */
function disableScroll() {
    // To get the scroll position of current webpage
    let topScroll = window.pageYOffset || document.documentElement.scrollTop;
    let leftScroll = window.pageXOffset || document.documentElement.scrollLeft;

    // if scroll happens, set it to the previous value
    window.onscroll = function() {
        window.scrollTo(leftScroll, topScroll);
    };
}

/** болиулсан scroll ийг сайжруулах нь */
function enableScroll() {
    window.onscroll = function() {};
}

function searchParamsToObject(search) {
    return Object.fromEntries(new URLSearchParams(search));
}

function objectToQueryString(obj)
{
    var str = [];
    for (var p in obj)
        if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        }
    return str.join("&");
}

// first_name=gg1|gg2|gg3&last_name=B1
const objectToQuery = (object={}) =>
{
    if(!object) return
    let text = ''
    Object.entries(object).map(
        (element) =>
        {
            if(element[1].length === 0) return
            let subTexts = ''
            Array.isArray(element[1])
            ?
                element[1].map(
                    (element, index) =>
                    {
                        subTexts = subTexts + element + "|"
                    }
                )
            :
                subTexts = element[1]

            if (Array.isArray(element[1])) {
				subTexts = subTexts.slice(0, -1)
			}
            text = `${text}&${element[0]}=${subTexts}`
        }
    )
    return text
}
