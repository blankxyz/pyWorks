var hostIP = "http://172.16.5.152:9000";
// var hostIP = chrome.cookies.get({
//     'url': 'localhost',
//     'name': 'hostIP'
// });
var links = new Array();
var topPage = document.location.href;
// var hostIP = $.cookie('hostIP');

//window.location.reload();
// document.removeChild()
alert('--- 全站爬虫-页面数据展示-启动　---\n' + topPage + ' ' + hostIP);

$("a").each(function () {
    var link = $(this).attr("href");
    if (link.length > 0 && link.indexOf("#") == -1 &&
        link.indexOf("javascript") == -1 &&
        link.indexOf(".js") == -1 &&
        link.indexOf(":", 6) == -1) {
        links.push(link);
        //links.push(encodeURI(link));
    }
});

// var hrefs = document.getElementsByTagName("a");
// for (i = 0; i < hrefs.length; i++) {
//     link = hrefs[i].href.toString();
//         if (link.length > 0 && link.indexOf("#") == -1 &&
//         link.indexOf("javascript") == -1 &&
//         link.indexOf(".js") == -1 &&
//         link.indexOf(":", 6) == -1) {
//         links.push(link);
//     }
// }

function httpPost_XMLHttpRequest(hrefs) {
    var xmlhttp;
    var url = 'http://172.16.5.152:9000/matchHubpage';
    var sendData;
    alert('httpPost_XMLHttpRequest call');

    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url, false);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    xmlhttp.setRequestHeader("Content-Length", hrefs.length);

    sendData = {
        topPage: topPage,
        hrefList: hrefs
    };
    s1 = JSON.stringify(sendData);
    alert(s1);
    xmlhttp.send(s1);

    if (xmlhttp.Status = 200) {
        var resp = xmlhttp.responseText;
        var j = JSON.parse(resp);
        var respArr = j.response;
        alert(respArr);

        $("a").each(function () {
            var link = $(this).attr("href");
            for (var i = 0; i < respArr.length; i++) {
                if (link == respArr[i]) {
                    // alert(link);
                    $(this).css({"border-style": "solid", "border-color": "red"});
                }
            }
        });
        return resp;
    }
}

function httpPost_ajax(hrefs) {
    // var hostIP = localStorage.hostIP;
    // var hostIP = document.cookie.split(";")[0].split("=")[1];
    // var hostIP = document.cookie;

    alert('＞＞＞ 发送页面全部链接到服务器　＞＞＞\n' + hostIP + '\n' + topPage + '\n' + links);

    $.ajax({
        url: 'http://172.16.5.152:9000/matchHubPage',
        type: 'post',
        dataType: 'json', //不能使用否则servesr无法取值
        // contentType: "application/json; charset=UTF-8",
        data: {
            hrefList: hrefs,
            topPage: topPage
        },
        // data:JSON.stringify({
        //     'hrefList': hrefs,
        //     'topPage': topPage
        // }),
        error: function (xhr, err) {
            alert(err);
        },
        success: function (data, textStatus) {
            var respArr = data['response'];
            alert('＞＞＞　在全站爬虫中找到如下结果　＞＞＞\n' + respArr);
            $("a").each(function () {
                var link = $(this).attr("href");
                for (var i = 0; i < respArr.length; i++) {
                    if (link == respArr[i]) {
                        $(this).css({"border-style": "solid", "border-color": "red"});
                    }
                }
            });
        }
    });
}

// httpPost_XMLHttpRequest(links);
httpPost_ajax(links);

//------------------------------------------
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    var act = request.act;
    var regex = request.regex;
    var patrn = new RegExp(regex);

    alert('接收到:  ' + act + '  ' + regex);
    alert(patrn);

    if (act == "match") {
        // window.location.reload();
        $("a").each(function () {
            var link = $(this).attr("href");
            if (patrn.exec(link)) {
                $(this).css({"border-style": "solid", "border-color": "blue"});
            } else {
                $(this).css({"border-style": null, "border-color": null});
            }
        });
    }
});


