let pageCookieName = 'pageList'

function makePageJson() {
    let pages = []
    $(".main-menu .nav-item a[href*='/']").not('.navbar-brand').each(
        (index, element) => {
            let el = $(element)
            let url = $(element).attr("href")
            let name = el.find("span").text().trim()
            let icon = el.find("i").data("feather")
            pages.push(
                {
                    name,
                    icon,
                    url
                }
            )
        }
    )
    let strPages = JSON.stringify(pages)
    _setCookie(pageCookieName, strPages)
    displayBookmarks(pages)
}

function _setCookie(cookieName, cookieValue, exMs = (24 * 60 * 60 * 1000)) {
    const date = new Date();
    date.setTime(date.getTime() + (exMs));
    let expires = "expires=" + date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}

function _getCookie(cookieName) {
    let name = cookieName + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let cookies = decodedCookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
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

/********************* Bookmark & Search ***********************/
// This variable is used for mouseenter and mouseleave events of search list
var $filename = $('.search-input input').data('search'),
    bookmarkWrapper = $('.bookmark-wrapper'),
    bookmarkStar = $('.bookmark-wrapper .bookmark-star'),
    bookmarkInput = $('.bookmark-wrapper .bookmark-input'),
    navLinkSearch = $('.nav-link-search'),
    searchInput = $('.search-input'),
    searchInputInputfield = $('.search-input input'),
    searchList = $('.search-input .search-list'),
    appContent = $('.app-content'),
    bookmarkSearchList = $('.bookmark-input .search-list');

// Bookmark icon click
bookmarkStar.on('click', function (e) {
    e.stopPropagation();
    bookmarkInput.toggleClass('show');
    bookmarkInput.find('input').val('');
    bookmarkInput.find('input').blur();
    bookmarkInput.find('input').focus();
    bookmarkWrapper.find('.search-list').addClass('show');

    var arrList = $('ul.nav.navbar-nav.bookmark-icons li'),
        $arrList = '',
        $activeItemClass = '';

    $('ul.search-list li').remove();

    for (var i = 0; i < arrList.length; i++) {
        if (i === 0) {
            $activeItemClass = 'current_item';
        } else {
            $activeItemClass = '';
        }

        var iconName = '',
            className = '';

        let _icon = $($($(arrList[i]).children().get(0)).children().get(0))
        let _navLink = $($(arrList[i]).children().get(0))

        if (_icon.hasClass('feather')) {
            var classString = _icon.attr("class");
            iconName = classString.split('feather-')[1].split(' ')[0];
            className = classString.split('feather-')[1].split(' ')[1];
        }

        $arrList += `
            <li class="auto-suggestion ${$activeItemClass}">
                <a class="d-flex align-items-center justify-content-between w-100" href=${_navLink.attr("href")}>
                    <div class="d-flex justify-content-start align-items-center">
                        ${feather.icons[iconName].toSvg({ class: 'me-75 ' + className })}
                        <span>
                            ${_navLink.data("bs-original-title").trim()}
                        </span>
                    </div>
                    ${feather.icons['star'].toSvg({ class: 'text-warning bookmark-icon float-end' })}
                </a>
            </li>
        `
    }
    $('ul.search-list').append($arrList);
});

// Navigation Search area Open
navLinkSearch.on('click', function () {
    var $this = $(this);
    var searchInput = $(this).parent('.nav-search').find('.search-input');
    searchInput.addClass('open');
    searchInputInputfield.focus();
    searchList.find('li').remove();
    bookmarkInput.removeClass('show');
});

// Navigation Search area Close
$('.search-input-close').on('click', function () {
    var $this = $(this),
        searchInput = $(this).closest('.search-input');
    if (searchInput.hasClass('open')) {
        searchInput.removeClass('open');
        searchInputInputfield.val('');
        searchInputInputfield.blur();
        searchList.removeClass('show');
        appContent.removeClass('show-overlay');
    }
});

// Filter
if ($('.search-list-main').length) {
    var searchListMain = new PerfectScrollbar('.search-list-main', {
        wheelPropagation: false
    });
}
if ($('.search-list-bookmark').length) {
    var searchListBookmark = new PerfectScrollbar('.search-list-bookmark', {
        wheelPropagation: false
    });
}
// update Perfect Scrollbar on hover
$('.search-list-main').mouseenter(function () {
    searchListMain.update();
});

// Add class on hover of the list
$(document).on('mouseenter', '.search-list li', function (e) {
    $(this).siblings().removeClass('current_item');
    $(this).addClass('current_item');
});
$(document).on('click', '.search-list li', function (e) {
    e.stopPropagation();
});

$('html').on('click', function ($this) {
    if (!$($this.target).hasClass('bookmark-icon')) {
        if (bookmarkSearchList.hasClass('show')) {
            bookmarkSearchList.removeClass('show');
        }
        if (bookmarkInput.hasClass('show')) {
            bookmarkInput.removeClass('show');
            appContent.removeClass('show-overlay');
        }
    }
});

// Prevent closing bookmark dropdown on input textbox click
$(document).on('click', '.bookmark-input input', function (e) {
    bookmarkInput.addClass('show');
    bookmarkSearchList.addClass('show');
});

async function editDBBookmark(url, state, returnData) {
    if (state === "NEW")
    {
        const rsp = await useLoader(fetchData("/account/page-bookmark/", { page: url }, "POST"), $(".bookmark-icons"))
        return { rsp, returnData }
    }
    else {
        const rsp = await useLoader(fetchData(`/account/page-bookmark/?page=${url}`, "", "DELETE"), $(".bookmark-icons"))
        return { rsp, returnData }
    }
}

// Favorite star click
$(document).on('click', '.bookmark-input .search-list .bookmark-icon', function (e) {
    e.stopPropagation();
    //  FAVORITE аас арилгах нь
    if ($(this).hasClass('text-warning'))
    {
        var arrList = $('ul.nav.navbar-nav.bookmark-icons li');
        for (var i = 0; i < arrList.length; i++) {

            let _navLink = $($(arrList[i]).children().get(0))

            if (_navLink.data("bs-original-title").trim() == $(this).parent()[0].innerText.trim()) {
                editDBBookmark(_navLink.attr("href"), 'DELETE', arrList[i])
                    .then(
                        ({ rsp, returnData }) =>
                        {
                            if (rsp.success)
                            {
                                $(returnData).remove();
                                $(this).removeClass('text-warning');
                            }
                        }
                    )
            }
        }
        e.preventDefault();
    }
    //  FAVORITE руу нэмэх нь
    else
    {
        e.preventDefault();

        let _icon = $($($(this).parent().children().get(0)).children().get(0))
        let __atag = $($(this).parent().get(0))
        var $url = __atag.attr("href"),
            $name = __atag.text(),
            $listItem = '',
            iconName = "";

        if (_icon.hasClass('feather'))
        {
            var classString = _icon.attr('class');
            iconName = classString.split('feather-')[1].split(' ')[0];
        }

        $listItem = `
            <li class="nav-item d-none d-lg-block">
                <a class="nav-link" href="${$url}" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-original-title="${$name.trim()}">
                    ${feather.icons[iconName].toSvg({ class: 'ficon' })}
                </a>
            </li>
        `

        editDBBookmark($url, 'NEW')
            .then(
                ({ rsp }) =>
                {
                    if (rsp.success)
                    {
                        $('ul.nav.bookmark-icons').append($listItem);
                        $(this).addClass('text-warning');
                    }
                }
            )
        $('[data-bs-toggle="tooltip"]').tooltip();

    }
});

// If we use up key(38) Down key (40) or Enter key(13)
$(window).on('keydown', function (e) {
    var $current = $('.search-list li.current_item'),
        $next,
        $prev;
    if (e.keyCode === 40) {
        $next = $current.next();
        $current.removeClass('current_item');
        $current = $next.addClass('current_item');
    } else if (e.keyCode === 38) {
        $prev = $current.prev();
        $current.removeClass('current_item');
        $current = $prev.addClass('current_item');
    }

    if (e.keyCode === 13 && $('.search-list li.current_item').length > 0) {
        var selected_item = $('.search-list li.current_item a');
        window.location = selected_item.attr('href');
        $(selected_item).trigger('click');
    }
});

function savedBookmarkDisplay(parsedPageList)
{
    let listContainer = $('ul.nav.navbar-nav.bookmark-icons')
    let filteredPageList = parsedPageList.filter(e => BOOKMARK_PAGES.includes(e.url) )

    for (let i = 0; i < filteredPageList.length; i++) {

        $listItem = `
            <li class="nav-item d-none d-lg-block">
                <a class="nav-link" href="${filteredPageList[i].url}" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-original-title="${filteredPageList[i].name.trim()}">
                    ${feather.icons[filteredPageList[i].icon].toSvg({ class: 'ficon' })}
                </a>
            </li>
        `
        listContainer.append($listItem)
    }
}

function displayBookmarks(pageList) {
    let parsedPageList = pageList
    if (typeof pageList === "string") {
        parsedPageList = JSON.parse(pageList)
    }

    savedBookmarkDisplay(parsedPageList)

    searchInputInputfield.on('keyup', function (e) {
        $(this).closest('.search-list').addClass('show');
        if (e.keyCode !== 38 && e.keyCode !== 40 && e.keyCode !== 13) {
            if (e.keyCode == 27) {
                appContent.removeClass('show-overlay');
                bookmarkInput.find('input').val('');
                bookmarkInput.find('input').blur();
                searchInputInputfield.val('');
                searchInputInputfield.blur();
                searchInput.removeClass('open');
                if (searchInput.hasClass('show')) {
                    $(this).removeClass('show');
                    searchInput.removeClass('show');
                }
            }

            // Define variables
            var value = $(this).val().toLowerCase(), //get values of input on keyup
                activeClass = '',
                bookmark = false,
                liList = $('ul.search-list li'); // get all the list items of the search

            liList.remove();
            // To check if current is bookmark input
            if ($(this).parent().hasClass('bookmark-input')) {
                bookmark = true;
            }

            // If input value is blank
            if (value != '') {
                appContent.addClass('show-overlay');

                // condition for bookmark and search input click
                if (bookmarkInput.focus()) {
                    bookmarkSearchList.addClass('show');
                } else {
                    searchList.addClass('show');
                    bookmarkSearchList.removeClass('show');
                }
                if (bookmark === false) {
                    searchList.addClass('show');
                    bookmarkSearchList.removeClass('show');
                }

                var $startList = '',
                    $otherList = '',
                    $htmlList = '',
                    $bookmarkhtmlList = '',
                    $pageList =
                        '<li class="d-flex align-items-center">' +
                        '<a href="#">' +
                        '<h6 class="section-label mt-75 mb-0">Pages</h6>' +
                        '</a>' +
                        '</li>',
                    $activeItemClass = '',
                    $bookmarkIcon = '',
                    $defaultList = '',
                    a = 0;

                let _pageList = parsedPageList

                // getting json data from file for search results
                for (var i = 0; i < _pageList.length; i++) {
                    // if current is bookmark then give class to star icon
                    // for laravel
                    if ($('body').attr('data-framework') === 'laravel') {
                        _pageList[i].url = assetPath + _pageList[i].url;
                    }

                    if (bookmark === true)
                    {

                        activeClass = ''; // resetting active bookmark class
                        var arrList = $('ul.nav.navbar-nav.bookmark-icons li'),
                            $arrList = '';

                        // Loop to check if current seach value match with the bookmarks already there in navbar
                        for (var j = 0; j < arrList.length; j++) {

                            const _atag = $($(arrList[j]).children().get(0))
                            if (_pageList[i].name.trim() === _atag.data("bs-original-title").trim())
                            {
                                activeClass = ' text-warning';
                                break;
                            }

                            else
                            {
                                activeClass = '';
                            }
                        }

                        $bookmarkIcon = feather.icons['star'].toSvg({ class: 'bookmark-icon float-end' + activeClass });
                    }

                    // Search list item start with entered letters and create list
                    if (_pageList[i].name.toLowerCase().indexOf(value) == 0 && a < 5) {
                        if (a === 0) {
                            $activeItemClass = 'current_item';
                        } else {
                            $activeItemClass = '';
                        }

                        $startList += `
                            <li class="auto-suggestion ${$activeItemClass}">
                                <a class="d-flex align-items-center justify-content-between w-100" href=${_pageList[i].url}>
                                    <div class="d-flex justify-content-start align-items-center">
                                        ${feather.icons[_pageList[i].icon].toSvg({ class: 'me-75 ' })}
                                        <span>
                                            ${_pageList[i].name.trim()}
                                        </span>
                                    </div>
                                    ${$bookmarkIcon}
                                </a>
                            </li>
                        `
                        a++;
                    }
                }

                for (var i = 0; i < _pageList.length; i++) {
                    if (bookmark === true) {
                        activeClass = ''; // resetting active bookmark class
                        var arrList = $('ul.nav.navbar-nav.bookmark-icons li'),
                            $arrList = '';
                        // Loop to check if current search value match with the bookmarks already there in navbar
                        for (var j = 0; j < arrList.length; j++) {

                            const _atag = $($(arrList[j]).children().get(0))

                            if (_pageList[i].name.trim() === _atag.data("bs-original-title").trim()) {
                                activeClass = ' text-warning';
                                break;
                            } else {
                                activeClass = '';
                            }
                        }

                        $bookmarkIcon = feather.icons['star'].toSvg({ class: 'bookmark-icon float-end' + activeClass });
                    }
                    // Search list item not start with letters and create list
                    if (
                        !(_pageList[i].name.toLowerCase().indexOf(value) == 0) &&
                        _pageList[i].name.toLowerCase().indexOf(value) > -1 &&
                        a < 5
                    ) {
                        if (a === 0) {
                            $activeItemClass = 'current_item';
                        } else {
                            $activeItemClass = '';
                        }
                        $otherList += `
                            <li class="auto-suggestion ${$activeItemClass}">
                                <a class="d-flex align-items-center justify-content-between w-100" href=${_pageList[i].url}>
                                    <div class="d-flex justify-content-start align-items-center">
                                        ${feather.icons[_pageList[i].icon].toSvg({ class: 'me-75 ' })}
                                        <span>
                                            ${_pageList[i].name.trim()}
                                        </span>
                                    </div>
                                    ${$bookmarkIcon}
                                </a>
                            </li>
                        `
                        a++;
                    }
                }

                $defaultList = $('.main-search-list-defaultlist').html();
                if ($startList == '' && $otherList == '') {
                    $otherList = $('.main-search-list-defaultlist-other-list').html();
                }

                // concatinating startlist, otherlist, defalutlist with pagelist
                $htmlList = $pageList.concat($startList, $otherList, $defaultList);
                $('ul.search-list').html($htmlList);
                // concatinating otherlist with startlist
                $bookmarkhtmlList = $startList.concat($otherList);

                $('ul.search-list-bookmark').html(
                    $bookmarkhtmlList === 'undefined'
                    ? `<div class="d-flex justify-content-center align-items-center">Хайлтын үр дүн байхгүй</div>`
                    : $bookmarkhtmlList
                );

            }

            else {
                if (bookmark === true) {
                    var arrList = $('ul.nav.navbar-nav.bookmark-icons li'),
                        $arrList = '';
                    for (var i = 0; i < arrList.length; i++) {
                        if (i === 0) {
                            $activeItemClass = 'current_item';
                        } else {
                            $activeItemClass = '';
                        }

                        var iconName = '',
                            className = '';

                        let _icon = $($($(arrList[i]).children().get(0)).children().get(0))
                        let _navLink = $($(arrList[i]).children().get(0))
                        if (_icon.hasClass('feather')) {
                            var classString = _icon.attr("class");
                            iconName = classString.split('feather-')[1].split(' ')[0];
                            className = classString.split('feather-')[1].split(' ')[1];
                        }

                        $arrList += `
                            <li class="auto-suggestion">
                                <a class="d-flex align-items-center justify-content-between w-100" href=${_navLink.attr("href")}>
                                    <div class="d-flex justify-content-start align-items-center">
                                        ${feather.icons[iconName].toSvg({ class: 'me-75 ' })}
                                        <span>
                                            ${_navLink.data("bs-original-title").trim()}
                                        </span>
                                    </div>
                                    ${feather.icons['star'].toSvg({ class: 'text-warning bookmark-icon float-end' })}
                                </a>
                            </li>
                        `
                    }
                    $('ul.search-list').append($arrList);
                }

                else {
                    // if search input blank, hide overlay
                    if (appContent.hasClass('show-overlay')) {
                        appContent.removeClass('show-overlay');
                    }
                    // If filter box is empty
                    if (searchList.hasClass('show')) {
                        searchList.removeClass('show');
                    }
                }

            }
        }
    });

}

let foundCookie = _getCookie(pageCookieName)
if (!foundCookie) {
    makePageJson()
}
else {
    displayBookmarks(foundCookie)
}
