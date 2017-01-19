var THEME = 'shine';

// -------------- detail_trend ------------------
var myChart_detail_trend = echarts.init(document.getElementById("detail_trend"), THEME);
var option_detail_trend = {
    title: {
        text: ''
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: ['前天', '昨天', '今天']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    },
    yAxis: {
        type: 'value'
    },
    series: [
        {
            name: '前天',
            type: 'line',
            stack: '前天采集量',
            data: [120, 132, 133, 134, 150, 200, 210, 220, 232, 233, 235, 260, 261, 262, 277, 278, 280, 290, 310, 330, 340, 350, 360,]
        },
        {
            name: '昨天',
            type: 'line',
            stack: '昨天采集量',
            data: [128, 142, 143, 144, 180, 220, 230, 250, 282, 273, 295, 290, 291, 292, 287, 291, 290, 292, 320, 330, 340, 350, 370,]
        },
        {
            name: '今天',
            type: 'line',
            stack: '今天采集量',
            data: [140, 162, 173, 184, 180, 220, 260, 270, 332, 333, 335, 360, 361, 362, 377, 378, 380, 390, 410, 430, 440, 450, 470,]
        }
    ]
};
myChart_detail_trend.setOption(option_detail_trend);


// ------------------ hubPage_trend  ------------------
var myChart_hubPage_trend = echarts.init(document.getElementById("hubPage_trend"), THEME);
option = {
    title: {
        text: '     扫描周期：20.6 小时'
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: ['今天']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    },
    yAxis: {
        type: 'value'
    },
    series: [
        {
            name: '今日',
            type: 'line',
            stack: '扫描量',
            data: [120, 132, 133, 134, 150, 200, 210, 220, 232, 233, 235, 260, 261, 262, 277, 278, 280, 290, 310, 330, 340, 350, 360]
        }]
};
myChart_hubPage_trend.setOption(option);

// ------------------ newDomain ------------------
var myChart_newDomain = echarts.init(document.getElementById('newDomain'), THEME);

var option_newDomain = {
    color: ['#39BCD1'],
    title: {
        text: ''
    },
    tooltip: {},
    legend: {
        data: ['新站数']
    },
    xAxis: {
        data: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    },
    yAxis: {},
    series: [{
        name: '新站数',
        barWidth: 10,
        type: 'bar',
        data: [500, 420, 360, 200, 1000, 900, 800]
    }]
};

myChart_newDomain.setOption(option_newDomain);

// ------------------ domain_rank ------------------
var myChart_domain_rank = echarts.init(document.getElementById('domain_rank'), THEME);

var option_domain_rank = {
    color: ['#39BCD1'],
    title: {
        text: ''
    },
    tooltip: {},
    legend: {
        data: ['采集详情页数']
    },
    xAxis: {
        data: ["No.1", "No.2", "No.3", "No.4", "No.5", "No.6", "No.7", "No.8", "No.9", "No.10"]
    },
    yAxis: {},
    series: [{
        name: '采集详情页数',
        barWidth: 10,
        type: 'bar',
        data: [50000, 42000, 36000, 20000, 10000, 9000, 8000, 6000, 3000, 1000]
    }]
};

myChart_domain_rank.setOption(option_domain_rank);

// ------------------ hubPage_rank ------------------
var myChart_hubPage_rank = echarts.init(document.getElementById('hubPage_rank'), THEME);

var option_hubPage_rank = {
    color: ['#348017'],
    title: {
        text: ''
    },
    tooltip: {},
    legend: {
        data: ['采集详情页数']
    },
    xAxis: {
        data: ["No.1", "No.2", "No.3", "No.4", "No.5", "No.6", "No.7", "No.8", "No.9", "No.10"]
    },
    yAxis: {},
    series: [{
        name: '采集详情页数',
        barWidth: 10,
        type: 'bar',
        data: [50000, 42000, 36000, 20000, 10000, 9000, 8000, 6000, 3000, 1000]
    }]
};

myChart_hubPage_rank.setOption(option_hubPage_rank);

// ------------------ redis_monitor ------------------
var myChart_redis_monitor = echarts.init(document.getElementById("redis_monitor"), THEME);

var base = 1;
var hour = [];

var data = [0];
var now = base;

function addData(shift) {
    hour.push(now);
    data.push(Math.random() * 60);

    if (shift) {
        hour.shift();
        data.shift();
    }
    if (now > 23) {
        now = 1;
    } else {
        now = now + 1;
    }
}

for (var i = 1; i < 24; i++) {
    addData();
}

var option_redis_monitor = {
    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: hour
    },
    yAxis: {
        boundaryGap: [0, '50%'],
        type: 'value',
        max: 100
    },
    series: [
        {
            name: 'redis',
            type: 'line',
            smooth: true,
            symbol: 'none',
            stack: 'a',
            areaStyle: {
                normal: {}
            },
            data: data
        }
    ]
};

setInterval(function () {
    addData(true);
    myChart_redis_monitor.setOption({
        xAxis: {
            data: hour
        },
        series: [{
            name: 'redis',
            data: data
        }]
    });
}, 1800);

if (option_redis_monitor && typeof option_redis_monitor === "object") {
    myChart_redis_monitor.setOption(option_redis_monitor, true);
}

// ------------------ crawlTime_part ------------------
var myChart_crawlTime_part = echarts.init(document.getElementById('crawlTime_part'), THEME);

var option_crawlTime_part = {
    tooltip: {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        orient: 'vertical',
        height: '240px',
        x: 'left',
        data: ['0-1分钟', '1-2分钟', '2-5分钟', '5-15分钟', '15-30分钟', '30-60分钟', '60-120分钟', '120-240分钟', '超过240分钟']
    },
    series: [
        {
            name: '采集时间差',
            type: 'pie',
            radius: '80%',
            center: ['50%', '50%'],
            data: [
                {value: 0, name: '0-1分钟'},
                {value: 0, name: '1-2分钟'},
                {value: 0, name: '2-5分钟'},
                {value: 222, name: '5-15分钟'},
                {value: 310, name: '15-30分钟'},
                {value: 234, name: '30-60分钟'},
                {value: 135, name: '60-120分钟'},
                {value: 1548, name: '120-240分钟'},
                {value: 222, name: '超过240分钟'}
            ],
            itemStyle: {
                normal: {
                    label: {show: false},
                    labelLine: {
                        show: false
                    }
                }
            }
        }
    ],
    color: ['#073f01', '#075f01', '#07a001', '#0fc005', '#20e010', '#b04020', '#800f05', '#5f0701', '#2f0000']
};

myChart_crawlTime_part.setOption(option_crawlTime_part);



