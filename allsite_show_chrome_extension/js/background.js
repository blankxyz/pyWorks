var hostIP = "http://172.16.5.152:9000";

//----------------------------------------------------------------------
function editHubPage(action, hubPage) {
    alert('＞＞＞ editHubPage　＞＞＞\n' + action + '\n' + hubPage);

    $.ajax({
        url: hostIP + '/editHubPage',
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
            // chrome.browserAction.setBadgetext({text:'add ok!'});
            var notification = new Notification(hubPage, {
                body: "已经添加到全站爬虫",
                iconUrl: 'images/icon16.png',
                tag: {} // 可以加一个tag
            });
            notification.show();
        }
    });
}

function addUrl(info, tab) {
    var url = info.linkUrl;

    alert(url);

    editHubPage('add', url);
}

chrome.contextMenus.create(
    {
        type: 'normal',
        title: '作为 列表页 添加到全站爬虫结果中',
        contexts: ['link'],
        onclick: addUrl
    }
);

