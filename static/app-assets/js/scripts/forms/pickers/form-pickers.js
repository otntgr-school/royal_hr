/*=========================================================================================
    File Name: pickers.js
    Description: Pick a date/time Picker, Date Range Picker JS
    ----------------------------------------------------------------------------------------
    Item Name: Vuexy  - Vuejs, HTML & Laravel Admin Dashboard Template
    Author: Pixinvent
    Author URL: hhttp://www.themeforest.net/user/pixinvent
==========================================================================================*/
(function (window, document, $) {
  'use strict';

  /*******  Flatpickr  *****/
  var basicPickr = $('.flatpickr-basic'),
    timePickr = $('.flatpickr-time'),
    calendarTimePickr = $('.flatpickr-calendar-time'),
    dateTimePickr = $('.flatpickr-date-time'),
    multiPickr = $('.flatpickr-multiple'),
    rangePickr = $('input.flatpickr-range'),
    rangePickrWrap = $('div.flatpickr-range'),
    humanFriendlyPickr = $('.flatpickr-human-friendly'),
    disabledRangePickr = $('.flatpickr-disabled-range'),
    inlineRangePickr = $('.flatpickr-inline');

  // Default
  if (basicPickr.length) {
    basicPickr.flatpickr({
      locale: {
          weekdays: {
              shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
              longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
          },
          months: {
              shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
              longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
          },
      },
    });
  }

  // Time
  if (timePickr.length) {
    timePickr.flatpickr({
      enableTime: true,
      noCalendar: true
    });
  }

  // Date and Time Авах
  if (calendarTimePickr.length) {
    calendarTimePickr.flatpickr({
      locale: {
        weekdays: {
          shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
          longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
        },
        months: {
          shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
          longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
        },
      },
      enableTime: true,
      noCalendar: false,
      time_24hr: true,
      minDate: 'today'
    });
  }

  // Date & TIme
  if (dateTimePickr.length) {
    dateTimePickr.flatpickr({
      locale: {
        weekdays: {
            shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
            longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
        },
        months: {
            shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
            longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
        },
      },
      enableTime: true
    });
  }

  // Multiple Dates
  if (multiPickr.length) {
    multiPickr.flatpickr({
      locale: {
        weekdays: {
            shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
            longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
        },
        months: {
            shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
            longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
        },
      },
      weekNumbers: true,
      mode: 'multiple',
      minDate: 'today'
    });
  }

  // Range
  if (rangePickr.length) {
    rangePickr.flatpickr({
      mode: 'range',
      onChange: function (selectedDates, datestr, config) {
        $(config.element).val(this.formatDate(selectedDates[0], "Y-m-d") + ' - ' + this.formatDate(selectedDates[1], "Y-m-d"));
      },
      locale: {
        weekdays: {
            shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
            longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
        },
        months: {
            shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
            longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
        },
    },
    });
  }

  // wrap range
  if (rangePickrWrap.length) {
    rangePickrWrap.flatpickr({
      mode: 'range',
      wrap: true,
      onChange: function (selectedDates, datestr, config) {
        $(config.element).find("[data-input]").val(this.formatDate(selectedDates[0], "Y-m-d") + ' - ' + this.formatDate(selectedDates[1], "Y-m-d"));
      },
      locale: {
        weekdays: {
            shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
            longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
        },
        months: {
            shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
            longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
        },
      },
    });
  }

  // Human Friendly
  if (humanFriendlyPickr.length) {
    humanFriendlyPickr.flatpickr({
      altInput: true,
      altFormat: 'F j, Y',
      dateFormat: 'Y-m-d'
    });
  }

  // Disabled Range
  if (disabledRangePickr.length) {
    disabledRangePickr.flatpickr({
      dateFormat: 'Y-m-d',
      disable: [
        {
          from: new Date().fp_incr(2),
          to: new Date().fp_incr(7)
        }
      ]
    });
  }

  // Inline
  if (inlineRangePickr.length) {
    inlineRangePickr.flatpickr({
      inline: true,
      locale: {
        weekdays: {
            shorthand: ['Ням', 'Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям'],
            longhand: ['Ням', 'Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан','Бямба'],
        },
        months: {
            shorthand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
            longhand: ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар', '10-р сар', '11-р сар', '12-р сар'],
        },
    },
    });
  }
  /*******  Pick-a-date Picker  *****/
  // Basic date
  if ($('.pickadate').length)
  {
    $('.pickadate').pickadate();
  }

  // Format Date Picker
  if ($('.format-picker').length)
  {
    $('.format-picker').pickadate({
      format: 'mmmm, d, yyyy'
    });
  }


  // Date limits
  if ($('.pickadate-limits').length)
  {
    $('.pickadate-limits').pickadate({
      min: [2019, 3, 20],
      max: [2019, 5, 28]
    });
  }

  // Disabled Dates & Weeks

  if ($('.pickadate-disable').length)
  {
    $('.pickadate-disable').pickadate({
      disable: [1, [2019, 3, 6], [2019, 3, 20]]
    });
  }

  // Picker Translations
  if ($('.pickadate-translations').length)
  {
    $('.pickadate-translations').pickadate({
      formatSubmit: 'dd/mm/yyyy',
      monthsFull: [
        'Janvier',
        'Février',
        'Mars',
        'Avril',
        'Mai',
        'Juin',
        'Juillet',
        'Août',
        'Septembre',
        'Octobre',
        'Novembre',
        'Décembre'
      ],
      monthsShort: ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'],
      weekdaysShort: ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'],
      today: "aujourd'hui",
      clear: 'clair',
      close: 'Fermer'
    });
  }

  // Month Select Picker
  if ($('.pickadate-months').length)
  {
    $('.pickadate-months').pickadate({
      selectYears: false,
      selectMonths: true
    });
  }

  // Month and Year Select Picker 2000-2030
  if ($('.pickadate-months-year-back').length)
  {
    $('.pickadate-months-year-back').pickadate({
      format: 'yyyy-mm-dd',
      monthsFull: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      monthsShort: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      weekdaysShort: ['Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям', 'Ням'],
      today: "Өнөөдөр",
      clear: 'Арилгах',
      close: 'Хаах',
      selectYears: true,
      selectYears: 50,
      min: new Date(),
      max: new Date((new Date().getFullYear() + 1), 12, 31),
      selectMonths: true
    });
  }

  // Month and Year Select Picker 2000-2030
  if ($('.pickadate-months-year-00-30').length)
  {
    $('.pickadate-months-year-00-30').pickadate({
      format: 'yyyy-mm-dd',
      monthsFull: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      monthsShort: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      weekdaysShort: ['Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям', 'Ням'],
      today: "Өнөөдөр",
      clear: 'Арилгах',
      close: 'Хаах',
      selectYears: true,
      selectYears: 50,
      min: new Date(2000,1,1),
      max: new Date(2030,11,31),
      selectMonths: true
    });
  }

  // Month and Year Select Picker 1900-2030
  if ($('.pickadate-months-year-1900-2030').length)
  {
    $('.pickadate-months-year-1900-2030').pickadate({
      format: 'yyyy-mm-dd',
      monthsFull: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      monthsShort: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      weekdaysShort: ['Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям', 'Ням'],
      today: "Өнөөдөр",
      clear: 'Арилгах',
      close: 'Хаах',
      selectYears: true,
      selectYears: 150,
      min: new Date(1900,1,1),
      max: new Date(2030,11,31),
      selectMonths: true
    });
  }

  // Month and Year Select Picker 1900-2100
  if ($('.pickadate-months-year-1900-2100').length)
  {
    $('.pickadate-months-year-1900-2100').pickadate({
      format: 'yyyy-mm-dd',
      monthsFull: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      monthsShort: [
        '1-сар',
        '2-сар',
        '3-сар',
        '4-сар',
        '5-сар',
        '6-сар',
        '7-сар',
        '8-сар',
        '9-сар',
        '10-сар',
        '11-сар',
        '12-сар'
      ],
      weekdaysShort: ['Дав', 'Мяг', 'Лха', 'Пүр', 'Баа', 'Бям', 'Ням'],
      today: "Өнөөдөр",
      clear: 'Арилгах',
      close: 'Хаах',
      selectYears: true,
      selectYears: 200,
      min: new Date(1900,1,1),
      max: new Date(2100,11,31),
      selectMonths: true,
    });
  }

  // Short String Date Picker
  if ($('.pickadate-short-string').length)
  {
    $('.pickadate-short-string').pickadate({
      weekdaysShort: ['S', 'M', 'Tu', 'W', 'Th', 'F', 'S'],
      showMonthsShort: true
    });
  }

  // Change first weekday
  if ($('.pickadate-firstday').length)
  {
    $('.pickadate-firstday').pickadate({
      firstDay: 1
    });
  }

  /*******    Pick-a-time Picker  *****/
  // Basic time
  if ($('.pickatime').length)
  {
    $('.pickatime').pickatime();
  }

  if ($('.pickatime-back').length)
  {
    $('.pickatime-back').pickatime({
      formatLabel: 'HH:i',
      format: 'HH:i',
      clear: ''
    });
  }

  // Format options
  if ($('.pickatime-format').length)
  {
    $('.pickatime-format').pickatime({
      // Escape any “rule” characters with an exclamation mark (!).
      format: 'T!ime selected: h:i a',
      formatLabel: 'HH:i a',
      formatSubmit: 'HH:i',
      hiddenPrefix: 'prefix__',
      hiddenSuffix: '__suffix'
    });

  }

  // Format options
  if ($('.pickatime-formatlabel').length)
  {
    $('.pickatime-formatlabel').pickatime({
      formatLabel: function (time) {
        var hours = (time.pick - this.get('now').pick) / 60,
          label = hours < 0 ? ' !hours to now' : hours > 0 ? ' !hours from now' : 'now';
        return 'h:i a <sm!all>' + (hours ? Math.abs(hours) : '') + label + '</sm!all>';
      }
    });

  }

  // Min - Max Time to select
  if ($('.pickatime-min-max').length)
  {
    $('.pickatime-min-max').pickatime({
      // Using Javascript
      min: new Date(2015, 3, 20, 7),
      max: new Date(2015, 7, 14, 18, 30)
  
      // Using Array
      // min: [7,30],
      // max: [14,0]
    });

  }

  // Intervals
  if ($('.pickatime-intervals').length)
  {

    $('.pickatime-intervals').pickatime({
      interval: 150
    });
  }

  // Disable Time
  if ($('.pickatime-disable').length)
  {
    $('.pickatime-disable').pickatime({
      disable: [
        // Disable Using Integers
        3,
        5,
        7,
        13,
        17,
        21
  
        /* Using Array */
        // [0,30],
        // [2,0],
        // [8,30],
        // [9,0]
      ]
    });

  }

  // Close on a user action
  if ($('.pickatime-close-action').length)
  {
    $('.pickatime-close-action').pickatime({
      closeOnSelect: false,
      closeOnClear: false
    });

  }
})(window, document, jQuery);


// Min - Max Time to select
if ($('.pickatime-min-max-interval').length)
{
  $('.pickatime-min-max-interval').pickatime({
    // Using Array
    min: [7,0],
    max: [22,0],
    twelvehour: false,
    format: "HH:i",
    hiddenName: true,
    interval: 60,
    clear: 'Арилгах',
  });
}
