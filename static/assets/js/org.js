(function (window, undefined) {
    'use strict';
    let wtf = []

    let orgMenu = $("#org-menu")

    async function getData()
    {
        const rsp  = await fetch(
            "/org/org-register/",
            {
                method: "GET"
            }
        ).catch(err => alert(aldaa))
        if (rsp.ok){
            return rsp.json()
        }
        return rsp
    }

    if (orgMenu.length)
    {
        getData()
            .then(rsp =>
                {
                    orgMenu.jstree({
                        core: {
                            data: rsp
                        },
                        plings: ['types', 'contextmenu', 'state'],
                        types: {
                            default: {
                                icon: 'fas fa-code-branch text-primary-green'
                            },
                            sub: {
                                icon: 'fas fa-landmark text-primary'
                            },
                            sub1: {
                                icon: 'fas fa-circle text-success '
                            },
                            sub2: {
                                icon: 'fas fa-circle text-success '
                            },
                            sub3: {
                                icon: 'fas fa-circle text-success '
                            }
                        }
                    });
                    orgMenu.bind(
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
