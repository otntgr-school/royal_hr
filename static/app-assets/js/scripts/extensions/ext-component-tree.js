/*=========================================================================================
	File Name: ext-component-tree.js
	Description: Tree
	----------------------------------------------------------------------------------------
	Item Name: Vuexy  - Vuejs, HTML & Laravel Admin Dashboard Template
	Author: Pixinvent
	Author URL: hhttp://www.themeforest.net/user/pixinvent
==========================================================================================*/

$(function () {
  'use strict';

  var basicTree = $('#jstree-basic'),
    customIconsTree = $('#jstree-custom-icons'),
    contextMenu = $('#jstree-context-menu'),
    dragDrop = $('#jstree-drag-drop'),
    checkboxTree = $('#jstree-checkbox'),
    ajaxTree = $('#jstree-ajax');

  var assetPath = '../../../app-assets/';
  if ($('body').attr('data-framework') === 'laravel') {
    assetPath = $('body').attr('data-asset-path');
  }

  // Basic
  if (basicTree.length) {
    basicTree.jstree();
  }

  // Custom Icons
  if (customIconsTree.length) {
    customIconsTree.jstree({
      core: {
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types'],
      types: {
        default: {
          icon: 'far fa-building'
        },
        html: {
          icon: 'fab fa-html5 text-danger'
        },
        css: {
          icon: 'fab fa-css3-alt text-info'
        },
        img: {
          icon: 'far fa-file-image text-success'
        },
        js: {
          icon: 'fab fa-node-js text-warning'
        }
      }
    });
  }

  // Context Menu
  if (contextMenu.length) {
    contextMenu.jstree({
      core: {
        check_callback: true,
        data: [
          {
            text: 'Дэд компани <span class="fw-bolder float-right">(2)</span>',
            children: [
              {
                text: 'Дэд компани 1.1',
                type: 'sub1'
              },
              {
                text: 'Дэд компани 1.2',
                type: 'sub1'
              }
            ]
          },
          {
            text: 'Дэд компани <span class="fw-bolder float-right">(3)</span>',
            state: {
              opened: false
            },
            children: [
              {
                text: 'Дэд компани 2.1',
                type: 'sub2'
              },
              {
                text: 'Дэд компани 2.2',
                type: 'sub2'
              },
              {
                text: 'Дэд компани 2.3',
                type: 'sub2'
              }
            ]
          },
          {
            text: 'Номин ххк <span class="fw-bolder float-right">(2)</span>',
            state: {
              opened: false
            },
            children: [
              {
                text: 'Номин моторс ххк',
                type: 'sub3'
              },
              {
                text: 'Номин финанс ххк',
                type: 'sub3'
              }
            ]
          },
          {
            text: 'Дэд компани 4',
            type: 'sub'
          },
          {
            text: 'Дэд компани 5',
            type: 'sub'
          },
          {
            text: 'Дэд компани 6',
            type: 'sub'
          }
        ]
      },
      plugins: ['types', 'contextmenu'],
      types: {
        default: {
          icon: 'fas fa-code-branch text-primary-green'
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
    });
  }

  // Drag Drop
  if (dragDrop.length) {
    dragDrop.jstree({
      core: {
        check_callback: true,
        data: [
          {
            text: 'Ерөнхий захирал',
            state: {
              opened: true
            },
            children: [
              {
                text: 'Санхүүгийн алба',
                type: 'css'
              },
              {
                text: 'Жижиглэн худалдааны алба',
                type: 'css'
              }
            ]
          },
        ]
      },
      plugins: ['types', 'dnd'],
      types: {
        default: {
          icon: 'far fa-folder'
        },
        html: {
          icon: 'fab fa-html5 text-danger'
        },
        css: {
          icon: 'fab fa-css3-alt text-info'
        },
        img: {
          icon: 'far fa-file-image text-success'
        },
        js: {
          icon: 'fab fa-node-js text-warning'
        }
      }
    });
  }

  // Checkbox
  if (checkboxTree.length) {
    checkboxTree.jstree({
      core: {
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types', 'checkbox', 'wholerow'],
      types: {
        default: {
          icon: 'far fa-folder'
        },
        html: {
          icon: 'fab fa-html5 text-danger'
        },
        css: {
          icon: 'fab fa-css3-alt text-info'
        },
        img: {
          icon: 'far fa-file-image text-success'
        },
        js: {
          icon: 'fab fa-node-js text-warning'
        }
      }
    });
  }

  // Ajax Example
  if (ajaxTree.length) {
    ajaxTree.jstree({
      core: {
        data: {
          url: assetPath + 'data/jstree-data.json',
          dataType: 'json',
          data: function (node) {
            return {
              id: node.id
            };
          }
        }
      },
      plugins: ['types', 'state'],
      types: {
        default: {
          icon: 'far fa-folder'
        },
        html: {
          icon: 'fab fa-html5 text-danger'
        },
        css: {
          icon: 'fab fa-css3-alt text-info'
        },
        img: {
          icon: 'far fa-file-image text-success'
        },
        js: {
          icon: 'fab fa-node-js text-warning'
        }
      }
    });
  }
});
