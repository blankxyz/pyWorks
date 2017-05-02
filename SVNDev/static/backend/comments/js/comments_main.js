var THEME = 'shine';//dark infographic macarons roma shine vintage

function ajaxError(err, msg) {
    alert('[错误信息]' + msg + err);
}

// ------------------ 新闻总数 评论总数 趋势 今日新增  ------------------
function drawDashBoardTop() {
    $.ajax({
        url: '/comments/dashBoardTopCntAPI/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '新闻总数 评论总数 趋势 今日新增');
        },
        success: function (data, textStatus) {
            $('#newsCnt').text(data["news_cnt"]);
            $('#commentsCnt').text(data["comments_cnt"]);
            $('#newsCommentsCnt').text(data["news_comments_cnt"]);
        }
    });
}
drawDashBoardTop();//先调用一次，加快显示。
//window.setInterval(dashBoardTopFunc, 60 * 1000); // 60s

// ------------------ 评论采集任务队列 ------------------
function drawCommentsQueue(THEME) {
    $.ajax({
        url: '/comments/commentsQueueAPI/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '评论采集任务队列');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById('commentsQueue'), THEME);

            var option = {
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['队列长度']
                },
                xAxis: {
                    data: ["qq", "toutiao", "ifeng", "163", "tianya", "sina"]
                },
                yAxis: {},
                series: [{
                    name: '队列长度',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["queueSize"],
                    markLine: {
                        data: [
                            [
                                {name: '标线1起点', value: 10000, xAxis: 0, yAxis: 10000},      // 当xAxis为类目轴时，数值1会被理解为类目轴的index，通过xAxis:-1|MAXNUMBER可以让线到达grid边缘
                                {name: '标线1终点', xAxis: 'sina', yAxis: 10000}             // 当xAxis为类目轴时，字符串'周三'会被理解为与类目轴的文本进行匹配
                            ],
                            [
                                {name: '标线2起点', value: 100000, xAxis: 0, yAxis: 100000},      // 当xAxis为类目轴时，数值1会被理解为类目轴的index，通过xAxis:-1|MAXNUMBER可以让线到达grid边缘
                                {name: '标线2终点', xAxis: 'sina', yAxis: 100000}             // 当xAxis为类目轴时，字符串'周三'会被理解为与类目轴的文本进行匹配
                            ],
                            [
                                {name: '标线3起点', value: 1000000, xAxis: 0, yAxis: 1000000},      // 当xAxis为类目轴时，数值1会被理解为类目轴的index，通过xAxis:-1|MAXNUMBER可以让线到达grid边缘
                                {name: '标线3终点', xAxis: 'sina', yAxis: 1000000}             // 当xAxis为类目轴时，字符串'周三'会被理解为与类目轴的文本进行匹配
                            ]
                        ]
                    }
                }]
            };
            myChart.setOption(option);
        }
    });
}
drawCommentsQueue(THEME);

// ------------------ 评论采集任务队列 ------------------
function drawCommentsCacheQueue(THEME) {
    $.ajax({
        url: '/comments/commentsCacheQueueAPI/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '评论采集任务队列');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById('commentsCacheQueue'), THEME);

            var option = {
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['队列长度']
                },
                xAxis: {
                    data: ["60", "120", "300", "600", "1800", "3600", "7200", "14000", "28800", "57600", "86400"]
                },
                yAxis: {},
                series: [{
                    name: '队列长度',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["queueSize"],
                    markLine: {
                        data: [
                            [
                                {name: '标线1起点', value: 10000, xAxis: 0, yAxis: 10000},
                                {name: '标线1终点', xAxis: 'sina', yAxis: 10000}
                            ],
                            [
                                {name: '标线2起点', value: 100000, xAxis: 0, yAxis: 100000},
                                {name: '标线2终点', xAxis: 'sina', yAxis: 100000}
                            ],
                            [
                                {name: '标线3起点', value: 1000000, xAxis: 0, yAxis: 1000000},
                                {name: '标线3终点', xAxis: 'sina', yAxis: 1000000}
                            ]
                        ]
                    }
                }]
            };
            myChart.setOption(option);
        }
    });
}
drawCommentsCacheQueue(THEME);

// -------------- 新闻采集数据历史统计 ------------------
function drawDomainNewsCnt(THEME) {
    $.ajax({
        url: '/comments/mainDomainNewsCntAPI/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '新闻采集数据历史统计');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById("domainNewsCnt"), THEME);
            var option = {
                title: {
                    text: ''
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: ['qq', 'sina', 'ifeng', '163', 'toutiao']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '5%',
                    containLabel: true
                },
                xAxis: {
                    data: data['days'],
                    type: 'category',
                    boundaryGap: false,
                    axisLabel: {
                        interval: data['days'],
                        rotate: 0,
                        textStyle: {
                            //color: "blue",
                            fontSize: 6
                        }
                    }
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: 'qq',
                        type: 'line',
                        stack: '采集量',
                        data: data['qq']
                    },
                    {
                        name: 'sina',
                        type: 'line',
                        stack: '采集量',
                        data: data['sina']
                    },
                    {
                        name: 'ifeng',
                        type: 'line',
                        stack: '采集量',
                        data: data['ifeng']
                    },
                    {
                        name: '163',
                        type: 'line',
                        stack: '采集量',
                        data: data['163']
                    },
                    {
                        name: 'toutiao',
                        type: 'line',
                        stack: '采集量',
                        data: data['toutiao']
                    }
                ]
            };
            myChart.setOption(option);
        }
    });
}
drawDomainNewsCnt(THEME);





