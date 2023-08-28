function throttle(selector, cb, delay = 500)
{
    function mainThottle(callback)
    {
        let shouldWait = false
        let waitingArgs
        const timeoutFunc = () =>
        {
            if(waitingArgs == null)
            {
                shouldWait = false
            }
            else
            {
                callback(...waitingArgs)
                waitingArgs = null
                setTimeout(timeoutFunc, delay)
            }
        }

        return (...args) =>
        {
            if(shouldWait)
            {
                waitingArgs = args
                return
            }
            callback(...args)
            shouldWait = true

            setTimeout(timeoutFunc, delay)
        }
    }

    const update = mainThottle(() => cb())

    $(selector)
        .on("input", e =>
        {
            update(e.target.value)
        })
}

// debounce text бичиж дуууссанаас хойш  delay тоогоор хүлээн cb function ажиллуулах
function debounce(selector, cb, delay=500)
{
    function mainDebounce(callback)
    {
        let timeout

        return (...args) =>
        {
            clearTimeout(timeout)
            timeout = setTimeout(() => {
                callback(...args)
            }, delay);
        }
    }

    const update = mainDebounce(() => cb())

    $(selector)
        .on("input", e =>
        {
            update(e.target.value)
        })
}
