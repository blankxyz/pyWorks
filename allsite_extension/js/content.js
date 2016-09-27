var patrn_rubbish = /uid|username|space|search|blog|group/;
var patrn_detail = /post|thread|detail/;
var patrn_list = /list|index|forum|fid/;

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    var list_regexs = request.list_regexs;
    var detail_regexs = request.detail_regexs;

    console.log("recv:" + request.status);

    for (var i in list_regexs) {
        console.log(list_regexs[i]);
    }
    for (var i in detail_regexs) {
        console.log(detail_regexs[i]);
    }
    
    if (request.status == "change") {
        $("a").each(function() {
            var link = $(this).attr("href");
            if (patrn_rubbish.exec(link)) {
                $(this).css({ "border-style": "solid", "border-color": "orange", "color": "orange" });
            }
            if (patrn_detail.exec(link)) {
                $(this).css({ "border-style": "solid", "border-color": "green", "color": "green" });
            }
            if (patrn_list.exec(link)) {
                $(this).css({ "border-style": "solid", "border-color": "blue", "color": "blue" });
            }
        });
    }
});
