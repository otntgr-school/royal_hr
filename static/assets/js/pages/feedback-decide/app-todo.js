/*=========================================================================================
    File Name: app-todo.js
    Description: app-todo
    ----------------------------------------------------------------------------------------
    Item Name: Vuexy  - Vuejs, HTML & Laravel Admin Dashboard Template
    Author: PIXINVENT
    Author URL: http://www.themeforest.net/user/pixinvent
==========================================================================================*/

var taskTitle,
    flatPickr = $('.task-due-date'),
    newTaskModal = $('.sidebar-todo-modal'),
    newTaskForm = $('#form-modal-todo'),
    favoriteStar = $('.todo-item-favorite'),
    modalTitle = $('.modal-title'),
    addBtn = $('.add-todo-item'),
    addTaskBtn = $('.add-task button'),
    updateTodoItem = $('.update-todo-item'),
    updateBtns = $('.update-btn'),
    taskDesc = $('#task-desc'),
    taskAssignSelect = $('#task-assigned'),
    taskTag = $('#task-tag'),
    overlay = $('.body-content-overlay'),
    menuToggle = $('.menu-toggle'),
    sidebarToggle = $('.sidebar-toggle'),
    sidebarLeft = $('.sidebar-left'),
    sidebarMenuList = $('.sidebar-menu-list'),
    todoFilter = $('#todo-search'),
    sortAsc = $('.sort-asc'),
    sortDesc = $('.sort-desc'),
    todoTaskList = $('.todo-task-list'),
    todoTaskListWrapper = $('.todo-task-list-wrapper'),
    listItemFilter = $('.list-group-filters'),
    noResults = $('.no-results'),
    checkboxId = 100,
    isRtl = $('html').attr('data-textdirection') === 'rtl';

var assetPath = '../../../app-assets/';
if ($('body').attr('data-framework') === 'laravel') {
    assetPath = $('body').attr('data-asset-path');
}

// if it is not touch device
if (!$.app.menu.is_touch_device()) {
    if (sidebarMenuList.length > 0) {
        var sidebarListScrollbar = new PerfectScrollbar(sidebarMenuList[0], {
            theme: 'dark'
        });
    }
    if (todoTaskListWrapper.length > 0) {
        var taskListScrollbar = new PerfectScrollbar(todoTaskListWrapper[0], {
            theme: 'dark'
        });
    }
}
// if it is a touch device
else {
    sidebarMenuList.css('overflow', 'scroll');
    todoTaskListWrapper.css('overflow', 'scroll');
}

// Add class active on click of sidebar filters list
if (listItemFilter.length) {
    listItemFilter.find('a').on('click', function () {
        if (listItemFilter.find('a').hasClass('active')) {
            listItemFilter.find('a').removeClass('active');
        }
        $(this).addClass('active');
    });
}

// Main menu toggle should hide app menu
if (menuToggle.length) {
    menuToggle.on('click', function (e) {
        sidebarLeft.removeClass('show');
        overlay.removeClass('show');
    });
}

// Todo sidebar toggle
if (sidebarToggle.length) {
    sidebarToggle.on('click', function (e) {
        e.stopPropagation();
        sidebarLeft.toggleClass('show');
        overlay.addClass('show');
    });
}

// On Overlay Click
if (overlay.length) {
    overlay.on('click', function (e) {
        sidebarLeft.removeClass('show');
        overlay.removeClass('show');
        $(newTaskModal).modal('hide');
    });
}

/** Жагсаалтанд байгаа тухайн элементийг шинэчлэх нь */
function changeListElement(feedback)
{
    let element = $(`.todo-item[data-cid="${selectedData.id}"]`)
    //  хайлтан дээр state нь check лэгдсэн байвал түүний state ийг нь солих
    if (searchs.state.includes(feedback.state + "") || searchs.state.length === 0)
    {
        let titleWrapper = element.children(".todo-title-wrapper")
        let todoAction = titleWrapper.children(".todo-item-action")
        let stateWrapper = todoAction.children(".avatar-wrapper")
        stateWrapper.html(getStateElement(feedback))
    }
    //  хайлтан дээр state нь check лэгдээгүй байвал арилгах
    else {
        element.remove()
    }
}

// Формын validate
if (newTaskForm.length) {
    newTaskForm.validate({
        ignore: '.ql-container *', // ? ignoring quill editor icon click, that was creating console error
        rules: {
            "decided_content": { required: true },
            'what': { required: true },
            'decided_at': { required: true },
        }
    });

    //  Форм дээр хадгалах товч дарах үед
    newTaskForm.on('submit', function (e) {
        e.preventDefault();
        var isValid = newTaskForm.valid();
        if (!isValid) { return }

        const formData = new FormData(e.target)
        formData.append("is_my", searchs.is_my)
        formData.delete("commands")
        newImages.map((cmd, idx) => formData.append("commands", cmd))
        removeImgIds.map((cmd, idx) => formData.append("remove_commands", cmd))
        fetchData(`/feedback/decide-list/${selectedData.id}/`, formData, 'PUT', "", false)
            .catch(err => err)
            .then(
                ({ success, data, erros }) =>
                {
                    if (success)
                    {
                        changeListElement(data)
                        newTaskModal.modal('hide');
                        overlay.removeClass('show');
                    }
                }
            )
    });
}

// Sort Ascending
if (sortAsc.length) {
    sortAsc.on('click', function () {
        todoTaskListWrapper
            .find('li')
            .sort(function (a, b) {
                return $(b).find('.todo-title').text().toUpperCase() < $(a).find('.todo-title').text().toUpperCase() ? 1 : -1;
            })
            .appendTo(todoTaskList);
    });
}
// Sort Descending
if (sortDesc.length) {
    sortDesc.on('click', function () {
        todoTaskListWrapper
            .find('li')
            .sort(function (a, b) {
                return $(b).find('.todo-title').text().toUpperCase() > $(a).find('.todo-title').text().toUpperCase() ? 1 : -1;
            })
            .appendTo(todoTaskList);
    });
}

// Filter task
if (todoFilter.length) {
    todoFilter.on('keyup', function () {
        var value = $(this).val().toLowerCase();
        if (value !== '') {
            $('.todo-item').filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
            var tbl_row = $('.todo-item:visible').length; //here tbl_test is table name

            //Check if table has row or not
            if (tbl_row == 0) {
                if (!$(noResults).hasClass('show')) {
                    $(noResults).addClass('show');
                }
            } else {
                $(noResults).removeClass('show');
            }
        } else {
            // If filter box is empty
            $('.todo-item').show();
            if ($(noResults).hasClass('show')) {
                $(noResults).removeClass('show');
            }
        }
    });
}

// For chat sidebar on small screen
if ($(window).width() > 992) {
    if (overlay.hasClass('show')) {
        overlay.removeClass('show');
    }
}

$(window).on('resize', function () {
    // remove show classes from sidebar and overlay if size is > 992
    if ($(window).width() > 992) {
        if ($('.body-content-overlay').hasClass('show')) {
            $('.sidebar-left').removeClass('show');
            $('.body-content-overlay').removeClass('show');
            $('.sidebar-todo-modal').modal('hide');
        }
    }
});


/*
  1. Шийдвэрлэх жагсаалт дээр хүний зургийг харуулах DONE
  2. Илгээсэн зөвшөөрсөн этрийг жагсаалт дээр ялгах DONE
  3. Өргөдөл үүсгэхэд хүн сонгож болно сонгохгүй байсан ч болно DONE
  4. Өргөдөл шийдэх үед файл хавсаргах DONE
  5. Надад ирсэн хүсэлт гэж хуудас гаргах (түүнийгээ decide тай нэг html ээр хийх) DONE
  6. Файлыг татах DONE
  7. Хүн өөрийн үүсгэсэн санал гомдлыг засаж болохгүй байх
  8. Татгалзсан эсвэл зөвшөөрсөн тайлбарыг харуулах
*/

