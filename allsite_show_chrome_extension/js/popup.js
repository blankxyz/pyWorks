var hostIP = "http://172.16.5.152:9000";

function editHubPage(action, hubPage) {
    alert('＞＞＞ editHubPage　＞＞＞\n' + action + '\n' + hubPage);

    $.ajax({
        url: 'http://172.16.5.152:9000/editHubPage',
        type: 'post',
        dataType: 'json', //不能使用否则servesr无法取值
        // contentType: "application/json; charset=UTF-8",
        // data: {
        //     action: action,
        //     hubPage: hubPage
        // },
        data: JSON.stringify({
            'action': action,
            'hubPage': hubPage
        }),
        error: function (xhr, err) {
            alert(err);
        },
        success: function (data, textStatus) {
            var resp = data['response'];
            alert('＞＞＞　editHubPage　＞＞＞\n' + resp);
        }
    });
}

function showHubpages() {
    html =
        '<input id=hubPage type=text size=40 placeholder="需要修改（重新学习）的 URL">' +
        '<a id=add href="#" type="button" class="btn btn-primary btn-sm">增加</a>' +
        '<a id=delete href="#" type="button" class="btn btn-primary btn-sm">删除</a>' +
        '<input id=regex type=text size=40 placeholder="查询 URL（支持正则）">' +
        '<a id=match href="#" type="button" class="btn btn-primary btn-sm">查询</a>';

    document.getElementById('hubPages_div').innerHTML = html;
}

//-----------------------------------------------------
showHubpages();

$('a').click(function () {
    var act = $(this).attr('id');

    if (act == 'add' || act == 'delete') {
        var hubPage = $('#hubPage').val();
        alert('act:' + act + '\nhubPage:' + hubPage);
        editHubPage(act, hubPage)
    }

    if (act == 'match') {
        var regex = $('#regex').val();
        var message = {"act": "match", "regex": regex};
        chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
            for (var i = tabs.length - 1; i >= 0; i--) {
                chrome.tabs.sendMessage(tabs[0].id, message);
            }
        });
    }
});