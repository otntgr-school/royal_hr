/*=========================================================================================
  File Name: app.js
  Description: Template related app JS.
  ----------------------------------------------------------------------------------------
  Item Name: Vuexy  - Vuejs, HTML & Laravel Admin Dashboard Template
  Author: Pixinvent
  Author URL: hhttp://www.themeforest.net/user/pixinvent
==========================================================================================*/
window.colors = {
  solid: {
    primary: '#036c86',
    secondary: '#82868b',
    success: '#28C76F',
    info: '#00cfe8',
    warning: '#f15c2b',
    danger: '#EA5455',
    dark: '#4b4b4b',
    black: '#000',
    white: '#fff',
    body: '#f8f8f8'
  },
  light: {
    primary: '#036c86',
    secondary: '#82868b1a',
    success: '#28C76F1a',
    info: '#00cfe81a',
    warning: '#f15c2b',
    danger: '#EA54551a',
    dark: '#4b4b4b1a'
  }
};
(function (window, document, $) {
  'use strict';
  var $html = $('html');
  var $body = $('body');
  var $textcolor = '#4e5154';
  var assetPath = '../../../app-assets/';

  if ($('body').attr('data-framework') === 'laravel') {
    assetPath = $('body').attr('data-asset-path');
  }

  // to remove sm control classes from datatables
  if ($.fn.dataTable) {
    $.extend($.fn.dataTable.ext.classes, {
      sFilterInput: 'form-control',
      sLengthSelect: 'form-select'
    });
  }

  $(window).on('load', function () {
    var rtl;
    var compactMenu = false;

    if ($body.hasClass('menu-collapsed') || localStorage.getItem('menuCollapsed') === 'true') {
      compactMenu = true;
    }

    if ($('html').data('textdirection') == 'rtl') {
      rtl = true;
    }

    setTimeout(function () {
      $html.removeClass('loading').addClass('loaded');
    }, 1200);

    $.app.menu.init(compactMenu);

    // Navigation configurations
    var config = {
      speed: 300 // set speed to expand / collapse menu
    };
    if ($.app.nav.initialized === false) {
      $.app.nav.init(config);
    }

    Unison.on('change', function (bp) {
      $.app.menu.change(compactMenu);
    });

    // Tooltip Initialization
    // $('[data-bs-toggle="tooltip"]').tooltip({
    //   container: 'body'
    // });
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Collapsible Card
    $('a[data-action="collapse"]').on('click', function (e) {
      e.preventDefault();
      $(this).closest('.card').children('.card-content').collapse('toggle');
      $(this).closest('.card').find('[data-action="collapse"]').toggleClass('rotate');
    });

    // Cart dropdown touchspin
    if ($('.touchspin-cart').length > 0) {
      $('.touchspin-cart').TouchSpin({
        buttondown_class: 'btn btn-primary',
        buttonup_class: 'btn btn-primary',
        buttondown_txt: feather.icons['minus'].toSvg(),
        buttonup_txt: feather.icons['plus'].toSvg()
      });
    }

    // Do not close cart or notification dropdown on click of the items
    $('.dropdown-notification .dropdown-menu, .dropdown-cart .dropdown-menu').on('click', function (e) {
      e.stopPropagation();
    });

    //  Notifications & messages scrollable
    $('.scrollable-container').each(function () {
      var scrollable_container = new PerfectScrollbar($(this)[0], {
        wheelPropagation: false
      });
    });

    // Reload Card
    $('a[data-action="reload"]').on('click', function () {
      var block_ele = $(this).closest('.card');
      var reloadActionOverlay;
      if ($html.hasClass('dark-layout')) {
        var reloadActionOverlay = '#10163a';
      } else {
        var reloadActionOverlay = '#fff';
      }
      // Block Element
      block_ele.block({
        message: feather.icons['refresh-cw'].toSvg({ class: 'font-medium-1 spinner text-primary' }),
        timeout: 2000, //unblock after 2 seconds
        overlayCSS: {
          backgroundColor: reloadActionOverlay,
          cursor: 'wait'
        },
        css: {
          border: 0,
          padding: 0,
          backgroundColor: 'none'
        }
      });
    });

    // Close Card
    $('a[data-action="close"]').on('click', function () {
      $(this).closest('.card').removeClass().slideUp('fast');
    });

    $('.card .heading-elements a[data-action="collapse"]').on('click', function () {
      var $this = $(this),
        card = $this.closest('.card');
      var cardHeight;

      if (parseInt(card[0].style.height, 10) > 0) {
        cardHeight = card.css('height');
        card.css('height', '').attr('data-height', cardHeight);
      } else {
        if (card.data('height')) {
          cardHeight = card.data('height');
          card.css('height', cardHeight).attr('data-height', '');
        }
      }
    });

    // Add disabled class to input group when input is disabled
    $('input:disabled, textarea:disabled').closest('.input-group').addClass('disabled');

    // Add sidebar group active class to active menu
    $('.main-menu-content').find('li.active').parents('li').addClass('sidebar-group-active');

    // Add open class to parent list item if subitem is active except compact menu
    var menuType = $body.data('menu');
    if (menuType != 'horizontal-menu' && compactMenu === false) {
      $('.main-menu-content').find('li.active').parents('li').addClass('open');
    }
    if (menuType == 'horizontal-menu') {
      $('.main-menu-content').find('li.active').parents('li:not(.nav-item)').addClass('open');
      $('.main-menu-content').find('li.active').closest('li.nav-item').addClass('sidebar-group-active open');
      // $(".main-menu-content")
      //   .find("li.active")
      //   .parents("li")
      //   .addClass("active");
    }

    //  Dynamic height for the chartjs div for the chart animations to work
    var chartjsDiv = $('.chartjs'),
      canvasHeight = chartjsDiv.children('canvas').attr('height'),
      mainMenu = $('.main-menu');
    chartjsDiv.css('height', canvasHeight);

    if ($body.hasClass('boxed-layout')) {
      if ($body.hasClass('vertical-overlay-menu')) {
        var menuWidth = mainMenu.width();
        var contentPosition = $('.app-content').position().left;
        var menuPositionAdjust = contentPosition - menuWidth;
        if ($body.hasClass('menu-flipped')) {
          mainMenu.css('right', menuPositionAdjust + 'px');
        } else {
          mainMenu.css('left', menuPositionAdjust + 'px');
        }
      }
    }

    /* Text Area Counter Set Start */

    $('.char-textarea').on('keyup', function (event) {
      checkTextAreaMaxLength(this, event);
      // to later change text color in dark layout
      $(this).addClass('active');
    });

    /*
    Checks the MaxLength of the Textarea
    -----------------------------------------------------
    @prerequisite:  textBox = textarea dom element
            e = textarea event
                    length = Max length of characters
    */
    function checkTextAreaMaxLength(textBox, e) {
      var maxLength = parseInt($(textBox).data('length')),
        counterValue = $('.textarea-counter-value'),
        charTextarea = $('.char-textarea');

      if (!checkSpecialKeys(e)) {
        if (textBox.value.length < maxLength - 1) textBox.value = textBox.value.substring(0, maxLength);
      }
      $('.char-count').html(textBox.value.length);

      if (textBox.value.length > maxLength) {
        counterValue.css('background-color', window.colors.solid.danger);
        charTextarea.css('color', window.colors.solid.danger);
        // to change text color after limit is maxedout out
        charTextarea.addClass('max-limit');
      } else {
        counterValue.css('background-color', window.colors.solid.primary);
        charTextarea.css('color', $textcolor);
        charTextarea.removeClass('max-limit');
      }

      return true;
    }
    /*
    Checks if the keyCode pressed is inside special chars
    -------------------------------------------------------
    @prerequisite:  e = e.keyCode object for the key pressed
    */
    function checkSpecialKeys(e) {
      if (e.keyCode != 8 && e.keyCode != 46 && e.keyCode != 37 && e.keyCode != 38 && e.keyCode != 39 && e.keyCode != 40)
        return false;
      else return true;
    }

    $('.content-overlay').on('click', function () {
      $('.search-list').removeClass('show');
      var searchInput = $('.search-input-close').closest('.search-input');
      if (searchInput.hasClass('open')) {
        searchInput.removeClass('open');
        searchInputInputfield.val('');
        searchInputInputfield.blur();
        searchList.removeClass('show');
      }

      $('.app-content').removeClass('show-overlay');
      $('.bookmark-wrapper .bookmark-input').removeClass('show');
    });

    // To show shadow in main menu when menu scrolls
    var container = document.getElementsByClassName('main-menu-content');
    if (container.length > 0) {
      container[0].addEventListener('ps-scroll-y', function () {
        if ($(this).find('.ps__thumb-y').position().top > 0) {
          $('.shadow-bottom').css('display', 'block');
        } else {
          $('.shadow-bottom').css('display', 'none');
        }
      });
    }
  });

  // Hide overlay menu on content overlay click on small screens
  $(document).on('click', '.sidenav-overlay', function (e) {
    // Hide menu
    $.app.menu.hide();
    return false;
  });

  // Execute below code only if we find hammer js for touch swipe feature on small screen
  if (typeof Hammer !== 'undefined') {
    var rtl;
    if ($('html').data('textdirection') == 'rtl') {
      rtl = true;
    }

    // Swipe menu gesture
    var swipeInElement = document.querySelector('.drag-target'),
      swipeInAction = 'panright',
      swipeOutAction = 'panleft';

    if (rtl === true) {
      swipeInAction = 'panleft';
      swipeOutAction = 'panright';
    }

    if ($(swipeInElement).length > 0) {
      var swipeInMenu = new Hammer(swipeInElement);

      swipeInMenu.on(swipeInAction, function (ev) {
        if ($body.hasClass('vertical-overlay-menu')) {
          $.app.menu.open();
          return false;
        }
      });
    }

    // menu swipe out gesture
    setTimeout(function () {
      var swipeOutElement = document.querySelector('.main-menu');
      var swipeOutMenu;

      if ($(swipeOutElement).length > 0) {
        swipeOutMenu = new Hammer(swipeOutElement);

        swipeOutMenu.get('pan').set({
          direction: Hammer.DIRECTION_ALL,
          threshold: 250
        });

        swipeOutMenu.on(swipeOutAction, function (ev) {
          if ($body.hasClass('vertical-overlay-menu')) {
            $.app.menu.hide();
            return false;
          }
        });
      }
    }, 300);

    // menu close on overlay tap
    var swipeOutOverlayElement = document.querySelector('.sidenav-overlay');

    if ($(swipeOutOverlayElement).length > 0) {
      var swipeOutOverlayMenu = new Hammer(swipeOutOverlayElement);

      swipeOutOverlayMenu.on('tap', function (ev) {
        if ($body.hasClass('vertical-overlay-menu')) {
          $.app.menu.hide();
          return false;
        }
      });
    }
  }

  $(document).on('click', '.menu-toggle, .modern-nav-toggle', function (e) {
    e.preventDefault();

    // Toggle menu
    $.app.menu.toggle();

    setTimeout(function () {
      $(window).trigger('resize');
    }, 200);

    if ($('#collapse-sidebar-switch').length > 0) {
      setTimeout(function () {
        if ($body.hasClass('menu-expanded') || $body.hasClass('menu-open')) {
          $('#collapse-sidebar-switch').prop('checked', false);
        } else {
          $('#collapse-sidebar-switch').prop('checked', true);
        }
      }, 50);
    }

    // Save menu collapsed status in localstorage
    if ($body.hasClass('menu-expanded') || $body.hasClass('menu-open')) {
      localStorage.setItem('menuCollapsed', false);
    } else {
      localStorage.setItem('menuCollapsed', true);
    }

    // Hides dropdown on click of menu toggle
    // $('[data-bs-toggle="dropdown"]').dropdown('hide');

    return false;
  });

  // Add Children Class
  $('.navigation').find('li').has('ul').addClass('has-sub');
  // Update manual scroller when window is resized
  $(window).resize(function () {
    $.app.menu.manualScroller.updateHeight();
  });

  $('#sidebar-page-navigation').on('click', 'a.nav-link', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $this = $(this),
      href = $this.attr('href');
    var offset = $(href).offset();
    var scrollto = offset.top - 80; // minus fixed header height
    $('html, body').animate(
      {
        scrollTop: scrollto
      },
      0
    );
    setTimeout(function () {
      $this.parent('.nav-item').siblings('.nav-item').children('.nav-link').removeClass('active');
      $this.addClass('active');
    }, 100);
  });

  // main menu internationalization

  // init i18n and load language file
  if ($body.attr('data-framework') === 'laravel') {
    // change language according to data-language of dropdown item
    var language = $('html')[0].lang;
    if (language !== null) {
      // get the selected flag class
      var selectedLang = $('.dropdown-language')
        .find('a[data-language=' + language + ']')
        .text();
      var selectedFlag = $('.dropdown-language')
        .find('a[data-language=' + language + '] .flag-icon')
        .attr('class');
      // set the class in button
      $('#dropdown-flag .selected-language').text(selectedLang);
      $('#dropdown-flag .flag-icon').removeClass().addClass(selectedFlag);
    }
  } else {
    i18next.use(window.i18nextXHRBackend).init(
      {
        debug: false,
        fallbackLng: 'en',
        backend: {
          loadPath: '/static/app-assets/data/locales/{{lng}}.json'
        },
        returnObjects: true
      },
      function (err, t) {
        // resources have been loaded
        jqueryI18next.init(i18next, $);
      }
    );

    // change language according to data-language of dropdown item
    $('.dropdown-language .dropdown-item').on('click', function () {
      var $this = $(this);
      $this.siblings('.selected').removeClass('selected');
      $this.addClass('selected');
      var selectedLang = $this.text();
      var selectedFlag = $this.find('.flag-icon').attr('class');
      $('#dropdown-flag .selected-language').text(selectedLang);
      $('#dropdown-flag .flag-icon').removeClass().addClass(selectedFlag);
      var currentLanguage = $this.data('language');
      i18next.changeLanguage(currentLanguage, function (err, t) {
        $('.main-menu, .horizontal-menu-wrapper').localize();
      });
    });
  }

  // Waves Effect
  Waves.init();
  Waves.attach(
    ".btn:not([class*='btn-relief-']):not([class*='btn-gradient-']):not([class*='btn-outline-']):not([class*='btn-flat-'])",
    ['waves-float', 'waves-light']
  );
  Waves.attach("[class*='btn-outline-']");
  Waves.attach("[class*='btn-flat-']");

  $('.form-password-toggle .input-group-text').on('click', function (e) {
    e.preventDefault();
    var $this = $(this),
      inputGroupText = $this.closest('.form-password-toggle'),
      formPasswordToggleIcon = $this,
      formPasswordToggleInput = inputGroupText.find('input');

    if (formPasswordToggleInput.attr('type') === 'text') {
      formPasswordToggleInput.attr('type', 'password');
      if (feather) {
        formPasswordToggleIcon.find('svg').replaceWith(feather.icons['eye'].toSvg({ class: 'font-small-4' }));
      }
    } else if (formPasswordToggleInput.attr('type') === 'password') {
      formPasswordToggleInput.attr('type', 'text');
      if (feather) {
        formPasswordToggleIcon.find('svg').replaceWith(feather.icons['eye-off'].toSvg({ class: 'font-small-4' }));
      }
    }
  });

  // on window scroll button show/hide
  $(window).on('scroll', function () {
    if ($(this).scrollTop() > 400) {
      $('.scroll-top').fadeIn();
    } else {
      $('.scroll-top').fadeOut();
    }

    // On Scroll navbar color on horizontal menu
    if ($body.hasClass('navbar-static')) {
      var scroll = $(window).scrollTop();

      if (scroll > 65) {
        $('html:not(.dark-layout) .horizontal-menu .header-navbar.navbar-fixed').css({
          background: '#fff',
          'box-shadow': '0 4px 20px 0 rgba(0,0,0,.05)'
        });
        $('.horizontal-menu.dark-layout .header-navbar.navbar-fixed').css({
          background: '#161d31',
          'box-shadow': '0 4px 20px 0 rgba(0,0,0,.05)'
        });
        $('html:not(.dark-layout) .horizontal-menu .horizontal-menu-wrapper.header-navbar').css('background', '#fff');
        $('.dark-layout .horizontal-menu .horizontal-menu-wrapper.header-navbar').css('background', '#161d31');
      } else {
        $('html:not(.dark-layout) .horizontal-menu .header-navbar.navbar-fixed').css({
          background: '#f8f8f8',
          'box-shadow': 'none'
        });
        $('.dark-layout .horizontal-menu .header-navbar.navbar-fixed').css({
          background: '#161d31',
          'box-shadow': 'none'
        });
        $('html:not(.dark-layout) .horizontal-menu .horizontal-menu-wrapper.header-navbar').css('background', '#fff');
        $('.dark-layout .horizontal-menu .horizontal-menu-wrapper.header-navbar').css('background', '#161d31');
      }
    }
  });

  // Click event to scroll to top
  $('.scroll-top').on('click', function () {
    $('html, body').animate({ scrollTop: 0 }, 75);
  });

  function getCurrentLayout() {
    var currentLayout = '';
    if ($html.hasClass('dark-layout')) {
      currentLayout = 'dark-layout';
    } else if ($html.hasClass('bordered-layout')) {
      currentLayout = 'bordered-layout';
    } else if ($html.hasClass('semi-dark-layout')) {
      currentLayout = 'semi-dark-layout';
    } else {
      currentLayout = 'light-layout';
    }
    return currentLayout;
  }

  // Get the data layout, for blank set to light layout
  var dataLayout = $html.attr('data-layout') ? $html.attr('data-layout') : 'light-layout';

  // Navbar Dark / Light Layout Toggle Switch
  $('.nav-link-style').on('click', function () {
    var currentLayout = getCurrentLayout(),
      switchToLayout = '',
      prevLayout = localStorage.getItem(dataLayout + '-prev-skin', currentLayout);

    // If currentLayout is not dark layout
    if (currentLayout !== 'dark-layout') {
      // Switch to dark
      switchToLayout = 'dark-layout';
    } else {
      // Switch to light
      // switchToLayout = prevLayout ? prevLayout : 'light-layout';
      if (currentLayout === prevLayout) {
        switchToLayout = 'light-layout';
      } else {
        switchToLayout = prevLayout ? prevLayout : 'light-layout';
      }
    }
    // Set Previous skin in local db
    localStorage.setItem(dataLayout + '-prev-skin', currentLayout);
    // Set Current skin in local db
    localStorage.setItem(dataLayout + '-current-skin', switchToLayout);

    // Call set layout
    setLayout(switchToLayout);

    // ToDo: Customizer fix
    $('.horizontal-menu .header-navbar.navbar-fixed').css({
      background: 'inherit',
      'box-shadow': 'inherit'
    });
    $('.horizontal-menu .horizontal-menu-wrapper.header-navbar').css('background', 'inherit');
  });

  // Get current local storage layout
  var currentLocalStorageLayout = localStorage.getItem(dataLayout + '-current-skin');

  // Set layout on screen load
  //? Comment it if you don't want to sync layout with local db
  setLayout(currentLocalStorageLayout);

  function setLayout(currentLocalStorageLayout) {
    var navLinkStyle = $('.nav-link-style'),
      currentLayout = getCurrentLayout(),
      mainMenu = $('.main-menu'),
      navbar = $('.header-navbar'),
      // Witch to local storage layout if we have else current layout
      switchToLayout = currentLocalStorageLayout ? currentLocalStorageLayout : currentLayout;

    $html.removeClass('semi-dark-layout dark-layout bordered-layout');

    if (switchToLayout === 'dark-layout') {
      $html.addClass('dark-layout');
      mainMenu.removeClass('menu-light').addClass('menu-dark');
      navbar.removeClass('navbar-light').addClass('navbar-dark');
      navLinkStyle.find('.ficon').replaceWith(feather.icons['sun'].toSvg({ class: 'ficon' }));
    } else if (switchToLayout === 'bordered-layout') {
      $html.addClass('bordered-layout');
      mainMenu.removeClass('menu-dark').addClass('menu-light');
      navbar.removeClass('navbar-dark').addClass('navbar-light');
      navLinkStyle.find('.ficon').replaceWith(feather.icons['moon'].toSvg({ class: 'ficon' }));
    } else if (switchToLayout === 'semi-dark-layout') {
      $html.addClass('semi-dark-layout');
      mainMenu.removeClass('menu-dark').addClass('menu-light');
      navbar.removeClass('navbar-dark').addClass('navbar-light');
      navLinkStyle.find('.ficon').replaceWith(feather.icons['moon'].toSvg({ class: 'ficon' }));
    } else {
      $html.addClass('light-layout');
      mainMenu.removeClass('menu-dark').addClass('menu-light');
      navbar.removeClass('navbar-dark').addClass('navbar-light');
      navLinkStyle.find('.ficon').replaceWith(feather.icons['moon'].toSvg({ class: 'ficon' }));
    }
    // Set radio in customizer if we have
    if ($('input:radio[data-layout=' + switchToLayout + ']').length > 0) {
      setTimeout(function () {
        $('input:radio[data-layout=' + switchToLayout + ']').prop('checked', true);
      });
    }
  }
})(window, document, jQuery);

// To use feather svg icons with different sizes
function featherSVG(iconSize) {
  // Feather Icons
  if (iconSize == undefined) {
    iconSize = '14';
  }
  return feather.replace({ width: iconSize, height: iconSize });
}

// jQuery Validation Global Defaults
if (typeof jQuery.validator === 'function') {
  jQuery.extend(jQuery.validator.messages, {
    required: "Энэ талбарыг бөглөнө үү",
    remote: "Please fix this field.",
    email: "Please enter a valid email address.",
    url: "Please enter a valid URL.",
    date: "Please enter a valid date.",
    dateISO: "Please enter a valid date (ISO).",
    number: "Please enter a valid number.",
    digits: "Please enter only digits.",
    creditcard: "Please enter a valid credit card number.",
    equalTo: "Please enter the same value again.",
    accept: "Please enter a value with a valid extension.",
    maxlength: jQuery.validator.format("{0}-с бага эсвэл тэнцүү утга оруулна уу"),
    minlength: jQuery.validator.format("{0}-с их эсвэл тэнцүү утга оруулна уу."),
    rangelength: jQuery.validator.format("Please enter a value between {0} and {1} characters long."),
    range: jQuery.validator.format("Please enter a value between {0} and {1}."),
    max: jQuery.validator.format("{0}-с бага эсвэл тэнцүү утга оруулна уу."),
    min: jQuery.validator.format("{0}-с их эсвэл тэнцүү утга оруулна уу.")
  });
  jQuery.validator.setDefaults({
    errorElement: 'label',
    errorPlacement: function (error, element) {
      if (
        element.parent().hasClass('input-group') ||
        element.hasClass('select2') ||
        element.attr('type') === 'checkbox'
      ) {
        error.insertAfter(element.parent());
      } else if (element.hasClass('form-check-input')) {
        error.insertAfter(element.parent().siblings(':last'));
      } else {
        error.insertAfter(element);
      }

      if (element.parent().hasClass('input-group')) {
        element.parent().addClass('is-invalid');
      }
    },
    highlight: function (element, errorClass, validClass) {
      $(element).addClass('error');
      if ($(element).parent().hasClass('input-group')) {
        $(element).parent().addClass('is-invalid');
      }
    },
    unhighlight: function (element, errorClass, validClass) {
      $(element).removeClass('error');
      if ($(element).parent().hasClass('input-group')) {
        $(element).parent().removeClass('is-invalid');
      }
    }
  });
}

// Add validation class to input-group (input group validation fix, currently disabled but will be useful in future)
/* function inputGroupValidation(el) {
  var validEl,
    invalidEl,
    elem = $(el);

  if (elem.hasClass('form-control')) {
    if ($(elem).is('.form-control:valid, .form-control.is-valid')) {
      validEl = elem;
    }
    if ($(elem).is('.form-control:invalid, .form-control.is-invalid')) {
      invalidEl = elem;
    }
  } else {
    validEl = elem.find('.form-control:valid, .form-control.is-valid');
    invalidEl = elem.find('.form-control:invalid, .form-control.is-invalid');
  }
  if (validEl !== undefined) {
    validEl.closest('.input-group').removeClass('.is-valid is-invalid').addClass('is-valid');
  }
  if (invalidEl !== undefined) {
    invalidEl.closest('.input-group').removeClass('.is-valid is-invalid').addClass('is-invalid');
  }
} */

function __resetForm(forms)
{
  for (const form of forms)
  {
    const $form = $(form)
    $form?.validate()?.resetForm();
    deleteError && deleteError()
  }
}

$("button[type='reset']").on("click", (event) =>
{
  const forms = $(event.target).parents("form")
  if (forms.length)
  {
    __resetForm(forms)
  }
})

$(".modal").on("hide.bs.modal", (event) =>
{
  const forms = $(event.target).children().find("form")
  if (forms.length)
  {
    __resetForm(forms)
  }
})
