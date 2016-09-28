var patrn_rubbish = /uid|username|space|search|blog|group/;
var patrn_detail = /post|thread|detail/;
var patrn_list = /list|index|forum|fid/;

function is_list(url, rubbish_regexs, list_regexs, detail_regexs) {

}

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    var regexs_list = new Array();
    var regexs_detail = new Array();

    console.log("request.opt:" + request.opt);

    for (var i in request.list_regexs) {
        regexs_list.push(request.list_regexs[i].regex)
            // console.log(request.list_regexs[i].regex);
    }
    for (var i in request.detail_regexs) {
        regexs_detail.push(request.detail_regexs[i].regex)
            // console.log(request.detail_regexs[i].regex);
    }

    var patrn_rubbish = /uid|username|space|search|blog|group/;
    var patrn_list = new RegExp("/" + regexs_list.join("|") + "/");
    var patrn_detail = new RegExp("/" + regexs_detail.join("|") + "/");
    console.log(patrn_list);
    console.log(patrn_detail);

    if (request.opt == "change") {
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
