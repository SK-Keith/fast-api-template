const newman = require('D:\\BaiduNetdiskDownload\\newman\\node_modules\\newman');
const fs = require('fs');
const path = require('path');
const async = require('D:\\BaiduNetdiskDownload\\newman\\node_modules\\async');

// 获取传递的参数  node .\run_newman_batch.js B081ZYPXXL,B07CSYNDF5,B09MLNYYMG
const args = process.argv.slice(2); // 去除前两个参数（执行路径和脚本路径）
console.log('传递的参数：', args);

// 默认的并发限制
let concurrencyLimit = 3;

// 构建数据结构
const page = parseInt(args[0]);
const search = args[1];
const data = [];

for (let i = 1; i <= page; i++) {
    data.push({
        "page": i,
        "search": search
    });
}

// 检查是否提供了并发限制参数
if (args.length > 3) {
    concurrencyLimit = parseInt(args[3]); // 将参数转换为整数
}

// 打印传递的参数
console.log('传递的参数：', args);
console.log('并发限制：', concurrencyLimit);
console.log('数据：', data);

// 记录开始时间
const startTime = Date.now();

// 并发执行 newman.run，最多同时执行 concurrencyLimit 个任务
async.mapLimit(data, concurrencyLimit, (singleIterationData, callback) => {
    console.log('参数：', singleIterationData);
    newman.run({
        collection: require('./pcollection.json'), // 使用相对路径引用集合文件
        iterationData: [singleIterationData], // 使用单个 iterationData 参数
    }).on('request', (err, args) => {
        console.log('提取的响应数据1-------------:');
        console.log(args.response);
        // 检查响应数据是否有效
        if (args.response && args.response.stream) {
            const responseBody = args.response.stream.toString('utf8');
            console.log('提取的响应数据:-------------');
            // console.log(responseBody);

            // 获取当前时间戳
            // const timestamp = Date.now();
            // 将参数值包含在文件名中
			// const filePath = path.join('D:\\BaiduNetdiskDownload\\newman', `${singleIterationData.search}_${singleIterationData.page}_${timestamp}.html`);
            // const folderName = new Date(timestamp).toISOString().slice(0, 10).replace(/-/g, '') + new Date(timestamp).toISOString().slice(11, 13);
            // const date = new Date(timestamp);
            // const year = date.getFullYear();
            // const month = String(date.getMonth() + 1).padStart(2, '0');
            // const day = String(date.getDate()).padStart(2, '0');
            // const hour = String(date.getHours()).padStart(2, '0');
            // const minute = String(date.getMinutes()).padStart(2, '0');

            // const folderName = `${year}${month}${day}${hour}${minute}`;
            const folderName = 'tmp'
            const filePath = path.join(`./${folderName}`, `${singleIterationData.search}_${singleIterationData.page}.html`);
            // 检查文件夹是否存在，如果不存在则创建它
            if (!fs.existsSync(folderName)) {
                fs.mkdirSync(folderName, {recursive: true});
            }
            // 写入文件
            fs.writeFile(filePath, responseBody, (err) => {
                if (err) {
                    console.error(err);
                } else {
                    console.log(`文件已保存到 ${filePath}`);
                }
            });
        } else {
            console.error('响应数据为空或无效，无法写入文件。');
        }
    }).on('done', (err, summary) => {
        // 完成时回调
        callback(err, summary);
    });
}, (err, results) => {
    // 所有任务完成后的回调
    if (err) {
        console.error('执行出错:', err);
    } else {
        // 记录结束时间
        const endTime = Date.now();
        // 计算耗时
        const duration = endTime - startTime;
        console.log(`总耗时：${duration} 毫秒`);
    }
});
