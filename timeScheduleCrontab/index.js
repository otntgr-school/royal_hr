const ZKLib = require('node-zklib')
const fs = require('fs')
const axios = require('axios');

const dateString = new Date().toString()
const dateFormatedString = dateString.replace(dateString.slice(dateString.indexOf('GMT+'), dateString.length), '')

var todayDateString = new Date().toDateString();

function createFolder(path)
{
	try
	{
		if (!fs.existsSync(`${__dirname}/${path}`))
		{
			fs.mkdirSync(`${__dirname}/${path}`);
		}
	}
	catch (err)
	{
		fs.appendFile(`${__dirname}/error.txt`, `create folder => ${JSON.stringify(err)}\n`, 'utf-8');
	}
}

async function timeMachine(ip, port=4370)
{
    let zkInstance = new ZKLib(ip, port, 1000000000, 4000);

    try
    {
        await zkInstance.createSocket()

        /** Хэрэглэгчийн тоо, бүртгэлийн тоо зэрэг ерөнхий мэдээллийг авах */
        // await zkInstance.getInfo()
    }
    catch (error)
    {
        fs.appendFile(`${__dirname}/error.txt`, `create socket => ${JSON.stringify(error)}\n`, 'utf-8');
    }

    /** Бүртгэлтэй хэрэглэгчид */
    const users = await zkInstance.getUsers();
	const usersData = users.data

    const logs = await zkInstance.getAttendances();

    zkInstance.getRealTimeLogs((data)=>{
        // do something when some checkin
        console.log(data)
    })

    var todayLogs = logs.data.filter(element => element.recordTime.toDateString() == todayDateString)

    var todayRealLogs = []

	for (let todayLog of todayLogs)
	{
		let uid = todayLog.deviceUserId

		let findedObj = usersData.find(val => val.userId == uid)

		if (findedObj && !findedObj.name.includes('.'))
		{
			todayRealLogs.push(
			{
				'employee_id': findedObj.name,
				'date_time_record': new Date(todayLog.recordTime).toLocaleString().replace(',', ''),
			})
		}
	}

    let res = await axios.post('http://hr.mnun.edu.mn/device/', todayRealLogs);

    const yearFolderIpName = `${ip}/${port}`
    const yearFolderName = `${ip}/${port}/${new Date().getFullYear()}`
	const yearAndMonthFolderName = `${ip}/${port}/${new Date().getFullYear()}/${new Date().getMonth() + 1}`

    createFolder(ip)
    createFolder(yearFolderIpName)
    createFolder(yearFolderName)
    createFolder(yearAndMonthFolderName)

    fs.appendFile(`${__dirname}/${yearAndMonthFolderName}/${new Date().getFullYear()}-${new Date().getMonth() + 1}-${new Date().getDate()}.txt`, `${dateFormatedString} => ${JSON.stringify(todayRealLogs)}\n`, 'utf-8', err => {
		if (err)
		{
			throw err;
		}
	});

    await zkInstance.disconnect();
}

timeMachine("122.201.25.246", 4370);
timeMachine("122.201.25.246", 4371);
