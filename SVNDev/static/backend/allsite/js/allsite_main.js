var THEME = 'shine';

function ajaxError(err, msg) {
    alert('[错误信息]' + msg + err);
}

// ------------------ 域名总数 频道总数 详情页总数 今日新增域名  ------------------
//window.setInterval(function () {
$.ajax({
    url: '/allsite/dashBoardTopCnt/',
    type: 'get',
    contentType: "application/json; charset=UTF-8",
    error: function (xhr, err) {
        ajaxError(err, '域名总数 频道总数 详情页总数 今日新增域名');
    },
    success: function (data, textStatus) {
        $('#domainCnt').text(data["domain_cnt"]);
        $('#hubPageCnt').text(data["hubPage_cnt"]);
        $('#detailTodayAllCnt').text(data["detail_today_all_cnt"]);
        $('#detailTodayUserCnt').text(data["detail_today_user_cnt"]);
        $('#detailTodayUserPar').val(data["detail_today_user_per"]);
        $('#detailTodayDirectCnt').text(data["detail_today_direct_cnt"]);
        $('#detailTodayDirectPar').val(data["detail_today_direct_per"]);
        $('#newDoaminCnt').text(data["new_doamin_cnt"]);
        $('.knob').knob();
    }
});
//}, 600);

// -------------- 采集统计24小时 ------------------
function detailTrendFunc(THEME) {
    $.ajax({
        url: '/allsite/drawDetailTrend/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '采集统计24小时');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById("detail_trend"), THEME);
            var option = {
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
                    data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
                        '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: '前天',
                        type: 'line',
                        stack: '前天采集量',
                        data: data['beforeYesterday']
                    },
                    {
                        name: '昨天',
                        type: 'line',
                        stack: '昨天采集量',
                        data: data['yesterday']
                    },
                    {
                        name: '今天',
                        type: 'line',
                        stack: '今天采集量',
                        data: data['today']
                    }
                ]
            };
            myChart.setOption(option);
        }
    });
}
detailTrendFunc(THEME);


// ------------------ 频道探测速度  ------------------
function hubPageTrendFunc(THEME) {
    $.ajax({
        url: '/allsite/drawHubPageTrend/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '频道探测速度');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById("hubPage_trend"), THEME);
            var option = {
                title: {
                    text: '     扫描周期：' + data['period']
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: ['对列剩余']
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
                    data: data['times']
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: '今日',
                        type: 'line',
                        stack: '扫描量',
                        data: data['remainQueue']
                    }]
            };
            myChart.setOption(option);
        }
    });
}
hubPageTrendFunc(THEME);

// ------------------ 域名总数 ------------------
function newDomainOpt(THEME, opt) {
    $.ajax({
        url: '/allsite/drawNewDomain/',
        type: 'POST',
        data: {opt: opt},
        dataType: "json",
        error: function (xhr, err) {
            ajaxError(err, '域名总数');
        },
        success: function (data, textStatus) {
            $('#newDomain').remove();
            $('#newDomainParent').html('<div id="newDomain" style="width:100%;height:270px;"></div>');

            var obj = document.getElementById('newDomain');
            var myChart = echarts.init(obj, THEME);
            var option = {
                color: ['#39BCD1'],
                title: {
                    text: ''
                },
                tooltip: {
                    trigger: 'axis'
                },
                toolbox: {
                    feature: {
                        dataView: {show: false, readOnly: false},
                        magicType: {show: false, type: ['line']},
                        restore: {show: false},
                        saveAsImage: {show: false}
                    }
                },
                legend: {
                    // data: ['日增数','总数']
                    data: ['总数']
                },
                dataZoom: [
                    {
                        type: 'slider',
                        start: 1,
                        end: 100
                    },
                    {
                        type: 'inside',
                        start: 1,
                        end: 100
                    }
                ],
                xAxis: {
                    data: data['timeList'],
                    axisLabel: {
                        interval: data['interval'],
                        rotate: 60,
                        textStyle: {
                            color: "blue",
                            fontSize: 6
                        }
                    }
                },
                yAxis: [
                    // {
                    //     type: 'value',
                    //     name: '日增数',
                    //     axisLabel: {
                    //         formatter: '{value}'
                    //     }
                    // },
                    {
                        type: 'value',
                        name: '总数',
                        axisLabel: {
                            formatter: '{value}'
                        }
                    }
                ],
                series: [
                    // {
                    //     name: '日增数',
                    //     barWidth: 10,
                    //     type: 'bar',
                    //     data: data['domainDaysCnt']
                    // },
                    {
                        name: '总数',
                        type: 'line',
                        data: data['domainTotalCnt']
                    }
                ]
            };
            myChart.setOption(option);
        }
    });
}

function reDrawNewDoamin(opt) {
    var THEME = '';
    newDomainOpt(THEME, opt);
}
newDomainOpt(THEME, 'week');


// ------------------ 新站发现(日增量) ------------------
function newDomainOptDays(THEME, opt) {
    $.ajax({
        url: '/allsite/drawNewDomain/',
        type: 'POST',
        data: {opt: opt},
        dataType: "json",
        error: function (xhr, err) {
            ajaxError(err, '新站发现(日增量)');
        },
        success: function (data, textStatus) {
            $('#newDomainDays').remove();
            $('#newDomainParentDays').html('<div id="newDomainDays" style="width:100%;height:270px;"></div>');

            var obj = document.getElementById('newDomainDays');
            var myChart = echarts.init(obj, THEME);
            var option = {
                color: ['#39BCD1'],
                title: {
                    text: ''
                },
                tooltip: {
                    trigger: 'axis'
                },
                toolbox: {
                    feature: {
                        dataView: {show: false, readOnly: false},
                        magicType: {show: false, type: ['line']},
                        restore: {show: false},
                        saveAsImage: {show: false}
                    }
                },
                legend: {
                    data: ['日增数']
                },
                dataZoom: [
                    {
                        type: 'slider',
                        start: 1,
                        end: 100
                    },
                    {
                        type: 'inside',
                        start: 1,
                        end: 100
                    }
                ],
                xAxis: {
                    data: data['timeList'],
                    axisLabel: {
                        interval: data['interval'],
                        rotate: 60,
                        textStyle: {
                            color: "blue",
                            fontSize: 6
                        }
                    }
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '日增数',
                        axisLabel: {
                            formatter: '{value}'
                        }
                    },
                    // {
                    //     type: 'value',
                    //     name: '总数',
                    //     axisLabel: {
                    //         formatter: '{value}'
                    //     }
                    // }
                ],
                series: [
                    {
                        name: '日增数',
                        barWidth: 10,
                        type: 'bar',
                        data: data['domainDaysCnt']
                    },
                    // {
                    //     name: '总数',
                    //     type: 'line',
                    //     yAxisIndex: 1,
                    //     data: data['domainTotalCnt']
                    // }
                ]
            };
            myChart.setOption(option);
        }
    });
}

function reDrawNewDoaminDays(opt) {
    var THEME = '';
    newDomainOptDays(THEME, opt);
}
newDomainOptDays(THEME, 'week');

// ------------------ 采集入库统计（域名 top10） ------------------
function domainRankFunc(THEME) {
    $.ajax({
        url: '/allsite/drawDomainRank/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '采集入库统计（域名 top10）');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById('domain_rank'), THEME);

            var option = {
                color: ['#39BCD1'],
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['已入库', '未入库']
                },
                xAxis: {
                    data: ["No.1", "No.2", "No.3", "No.4", "No.5", "No.6", "No.7", "No.8", "No.9", "No.10"]
                },
                yAxis: {},
                series: [{
                    name: '已入库',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["domainRankUsed"]
                }, {
                    name: '未入库',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["domainRankUnUsed"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
domainRankFunc(THEME);

// ------------------ 采集入库统计（一周） ------------------
function crawlUsedFunc(THEME) {
    $.ajax({
        url: '/allsite/drawCrawlUsed/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '采集入库统计（一周）');
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById('crawlUsed'), THEME);

            var option = {
                color: ['#39BCD1'],
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['已采集', '已入库']
                },
                xAxis: {
                    data: data["days"]
                },
                yAxis: {},
                dataZoom: [
                    {
                        type: 'slider',
                        start: 1,
                        end: 100
                    },
                    {
                        type: 'inside',
                        start: 1,
                        end: 100
                    }
                ],
                series: [{
                    name: '已采集',
                    barWidth: 10,
                    type: 'bar',
                    data: data["crawled"]
                }, {
                    name: '已入库',
                    barWidth: 10,
                    type: 'bar',
                    data: data["unUsed"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
crawlUsedFunc(THEME);

// ------------------ 频道采集量排名 ------------------
function hubPageRankFunc(THEME) {
    $.ajax({
        url: '/allsite/drawHubPageRank/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '频道采集量排名');
        },
        success: function (data, textStatus) {

            var myChart = echarts.init(document.getElementById('hubPage_rank'), THEME);
            var urlList = data["hubPageUrl"];
            var crawledNumList = data["hubPageCrawledNum"];
            var option = {
                    color: ['#348017'],
                    title: {
                        text: ''
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: function (params) {
                            var x = params.name;
                            var i = parseInt(x.substring(3, x.length));

                            return crawledNumList[i - 1] + '页<br/>' + urlList[i - 1];
                        }
                    },
                    legend: {
                        data: ['已采集详情页数']
                    },
                    xAxis: {
                        //data: data["hubPageUrl"]
                        data: ['No.1', 'No.2', 'No.3', 'No.4', 'No.5', 'No.6', 'No.7', 'No.8', 'No.9', 'No.10']
                    },
                    yAxis: {},
                    series: [{
                        name: '已采集详情页数',
                        stack: '总量',
                        barWidth: 10,
                        type: 'bar',
                        data: data["hubPageCrawledNum"]
                    }]
                }
                ;
            myChart.setOption(option);
        }
    });
}
hubPageRankFunc(THEME);

// ------------------ redis_monitor ------------------
function redisMonitorFunc(THEME) {
    var myChart = echarts.init(document.getElementById("redis_monitor"), THEME);

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

    var option = {
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
        myChart.setOption({
            xAxis: {
                data: hour
            },
            series: [{
                name: 'redis',
                data: data
            }]
        });
    }, 1800);

    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
}
redisMonitorFunc(THEME);

// ------------------ 采集时间差 ------------------
function crawlTimePart(THEME) {
    $.ajax({
        url: '/allsite/drawCrawlTimePart/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err, '采集时间差');
        },
        success: function (data, textStatus) {
            var s = data['0-1'] + data['1-2'] + data['2-5'] + data['5-15'] + data['15-30'] +
                data['30-60'] + data['60-120'] + data['120-240'] + data['>240'];
            if (s == 0) {
                $('#crawlTime_part').html('<h1 style="color:red"> 采集时间差的d1-d9件数合计为0，无法显示。</h1>');
                return false;
            }

            var myChart = echarts.init(document.getElementById('crawlTime_part'), THEME);
            var option = {
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    height: '240px',
                    x: 'left',
                    data: ['0-1分钟', '1-2分钟', '2-5分钟', '5-15分钟', '15-30分钟', '30-60分钟',
                        '60-120分钟', '120-240分钟', '超过240分钟']
                },
                series: [
                    {
                        name: '采集时间差',
                        type: 'pie',
                        radius: '80%',
                        center: ['50%', '50%'],
                        data: [
                            {value: data['0-1'], name: '0-1分钟'},
                            {value: data['1-2'], name: '1-2分钟'},
                            {value: data['2-5'], name: '2-5分钟'},
                            {value: data['5-15'], name: '5-15分钟'},
                            {value: data['15-30'], name: '15-30分钟'},
                            {value: data['30-60'], name: '30-60分钟'},
                            {value: data['60-120'], name: '60-120分钟'},
                            {value: data['120-240'], name: '120-240分钟'},
                            {value: data['>240'], name: '超过240分钟'}
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
            myChart.setOption(option);
            myChart.on('click', function (params) {
                var p = params.name;
                window.location.href = "/allsite/crawlTimes/";
            });
        }
    });
}
crawlTimePart(THEME);

// ------------------ detail_diff  ------------------
function detailDiffFunc(THEME) {
    var myChart = echarts.init(document.getElementById("detail_diff"), THEME);
    var option = {
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
    myChart.setOption(option);
}
detailDiffFunc(THEME);





