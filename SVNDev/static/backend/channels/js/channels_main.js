var THEME = 'shine';//dark infographic macarons roma shine vintage

function ajaxError(err, msg) {
    alert('[错误信息]' + msg + err);
}

// ------------------ 顶端数字栏  ------------------
function dashBoardTopCnt() {
    $.ajax({
        url: '/channels/mainTopCntAPI/',
        type: 'GET',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '顶端数字栏');
        },
        success: function (data, textStatus) {
            $('#domainCnt').text(data["domain_cnt"]);
            $('#channelCnt').text(data["channel_cnt"]);
        }
    });
}
dashBoardTopCnt();//先调用一次，加快显示。

// ------------------ InfoFlag统计 ------------------
function infoFlag(THEME) {
    $.ajax({
        url: '/channels/mainInfoFlagAPI/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, 'InfoFlag统计');
        },
        success: function (data, status) {
            var myChart = echarts.init(document.getElementById('InfoFlag'), THEME);
            var option = {
                color: ['#348017'],
                title: {
                    text: ''
                },
                legend: {
                    data: ['频道数']
                },
                xAxis: {
                    data: data["flag_list"],
                    axisLabel: {
                        interval: data['flag_list'],
                        rotate: 60,
                        textStyle: {
                            fontSize: 6
                        }
                    }
                },
                yAxis: {
                    interval:1
                },
                series: [{
                    name: '频道数',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["cnt_list"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
infoFlag(THEME);

// ------------------ 运行状态下的队列统计 ------------------
function taskQueue(THEME) {
    $.ajax({
        url: '/channels/mainTaskAPI/',
        type: 'GET',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '运行状态下的队列统计');
        },
        success: function (data, status) {
            var myChart = echarts.init(document.getElementById('TaskQueue'), THEME);
            var option = {
                color: ['#348017'],
                title: {
                    text: ''
                },
                legend: {
                    data: ['频道数']
                },
                xAxis: {
                    data: data["task_list"]
                },
                yAxis: {
                    interval:1
                },
                series: [{
                    name: '频道数',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["cnt_list"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
taskQueue(THEME);

// ------------------ 各个状态的分类统计 ------------------
function statusDraw(THEME) {
    $.ajax({
        url: '/channels/mainStatusAPI/',
        type: 'GET',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '各个状态的分类统计');
        },
        success: function (data, status) {
            var myChart = echarts.init(document.getElementById('Status'), THEME);
            var option = {
                color: ['#348017'],
                title: {
                    text: ''
                },
                legend: {
                    data: ['频道数']
                },
                xAxis: {
                    data: data["status_list"]
                },
                yAxis: {
                    interval:1
                },
                series: [{
                    name: '频道数',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["cnt_list"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
statusDraw(THEME);




