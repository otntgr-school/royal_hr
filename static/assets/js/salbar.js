(function (window, undefined) {
    'use strict';

    let wtf = []

    let salbarMenu = $("#salbar-menu")
    // Салбарын жагсаалтыг өгөх нь

    async function getData()
    {
        const rsp = await fetch(
            "/salbar/sub-org-list/",
            {
                method: "GET"
            }
        ).catch(err => alert("aldaa"))
        if (rsp.ok) {
            return rsp.json()
        }
        return rsp
    }

    if (salbarMenu.length)
    {
        getData()
            .then(rsp =>
                {
                    salbarMenu.jstree({
                        core: {
                            data: rsp
                        },
                        plugins: ['types', 'contextmenu', 'state'],
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
                    salbarMenu.bind(
                        "select_node.jstree",
                        function (e, data)
                        {
                            if (data.node.parent !== '#' && data.node.a_attr.href !== window.location.pathname && wtf.length > 0)
                            {
                                window.location.href = data.node.a_attr.href
                            }
                            wtf.push(data.node.a_attr.href)
                        }
                    )
                })
    }
})(window);
