/*=========================================================================================
        File Name: form-input-mask.js
        Description: Input Masks
        ----------------------------------------------------------------------------------------
        Item Name: Vuexy  - Vuejs, HTML & Laravel Admin Dashboard Template
        Author: Pixinvent
        Author URL: hhttp://www.themeforest.net/user/pixinvent
==========================================================================================*/

$(function () {
	"use strict";

	var creditCard = $(".credit-card-mask"),
		phoneMask = $(".phone-number-mask"),
		dateMask = $(".date-mask"),
		timeMask = $(".time-mask"),
		yearMonthMask = $(".year-and-month"),
		onlyMonthMask = $(".only-year"),
		monthDayMask = $(".month-day"),
		yearMonthDayMask = $(".year-month-day"),
		dateTimeMask = $(".datetime-mask"),
		numeralMask = $(".numeral-mask"),
		numeralOnlyMask = $(".numeral-only-mask"),
		blockMask = $(".block-mask"),
		delimiterMask = $(".delimiter-mask"),
		customDelimiter = $(".custom-delimiter-mask"),
		prefixMask = $(".prefix-mask");

	// Credit Card
	if (creditCard.length) {
		creditCard.each(function () {
			new Cleave($(this), {
				creditCard: true,
			});
		});
	}

	// Phone Number
	if (phoneMask.length) {
		phoneMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				phone: true,
				phoneRegionCode: "MN",
			});
		})
	}

	// Date
	if (dateMask.length) {
		dateMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				date: true,
				delimiter: "-",
				datePattern: ["Y", "m", "d"],
			});
		})
	}

	// Time
	if (timeMask.length) {
		timeMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				time: true,
				timePattern: ["h", "m", "s"],
			});
		})
	}

	// Year and Month
	if (yearMonthMask.length) {
		yearMonthMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				date: true,
				delimiter: "-",
				datePattern: ["Y", "m"],
			});
		})
	}

	// Only Month
	if (onlyMonthMask.length) {
		onlyMonthMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				date: true,
				datePattern: ["Y"]
			})
		})
	}

	// Date amnd time
	if (dateTimeMask.length) {
		dateTimeMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				delimiters: ['-', '-', ' ', ':'],
				blocks: [4, 2, 2, 2, 2]
			});
		})
	}

	// Year month day
	if (yearMonthDayMask.length) {
		yearMonthDayMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				date: true,
				delimiter: "-",
				datePattern: ["Y", "m", 'd'],
			});
		})
	}

	// Month day
	if (monthDayMask.length) {
		monthDayMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				date: true,
				delimiter: "-сарын-",
				datePattern: ["m", 'd'],
			});
		})
	}

	//Numeral
	if (numeralMask.length) {
		numeralMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				numeral: true,
				numeralThousandsGroupStyle: "thousand",
			});
		})
	}

	//Numeral
	if (numeralOnlyMask.length) {
		numeralOnlyMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				numeral: true,
				numeralThousandsGroupStyle: 'none',
			});
		})
	}

	//Block
	if (blockMask.length) {
		blockMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				blocks: [4, 3, 3],
				uppercase: true,
			});
		})
	}

	// Delimiter
	if (delimiterMask.length) {
		delimiterMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				delimiter: "·",
				blocks: [3, 3, 3],
				uppercase: true,
			});
		})
	}

	// Custom Delimiter
	if (customDelimiter.length) {
		customDelimiter.toArray().forEach(function(field)
		{
			new Cleave(field, {
				delimiters: [".", ".", "-"],
				blocks: [3, 3, 3, 2],
				uppercase: true,
			});
		})
	}

	// Prefix
	if (prefixMask.length) {
		prefixMask.toArray().forEach(function(field)
		{
			new Cleave(field, {
				prefix: "+63",
				blocks: [3, 3, 3, 4],
				uppercase: true,
			});
		})
	}
});
