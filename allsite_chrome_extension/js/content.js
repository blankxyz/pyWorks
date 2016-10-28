var g_detail = new Array();
var g_list = new Array();

function is_list(url, rubbish_regexs, list_regexs, detail_regexs) {

}

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    var regexs_list = new Array();
    var regexs_detail = new Array();

    console.log("request.opt:" + request.opt);

    for (var i = 0; i < request.list_regexs.length; i++) {
        regexs_list.push(request.list_regexs[i].regex);
        g_list.push(request.list_regexs[i]);
        // console.log(request.list_regexs[i].regex);
    }
    for (var i = 0; i < request.detail_regexs.length; i++) {
        regexs_detail.push(request.detail_regexs[i].regex);
        g_detail.push(request.detail_regexs[i]);
        // console.log(request.detail_regexs[i].regex);
    }

    patrn_list = new RegExp("/" + regexs_list.join("|") + "/");
    patrn_detail = new RegExp("/" + regexs_detail.join("|") + "/");
    //console.log(patrn_list);
    //console.log(patrn_detail);

    if (request.opt == "change") {
        //window.location.reload();
        $("a").each(function () {
            var link = $(this).attr("href");
            $(this).css({"border-style": "dashed", "border-color": "black"});
            //if (patrn_rubbish.exec(link)) {
            //    $(this).css({ "border-style": "solid", "border-color": "orange" });
            //    //$(this).css({ "border-style": "solid", "border-color": "orange", "color": "orange" });
            //}
            if (patrn_detail.exec(link)) {
                $(this).css({"border-style": "solid", "border-color": "green"});
                //$(this).css({ "border-style": "solid", "border-color": "green", "color": "green" });
            }
            if (patrn_list.exec(link)) {
                $(this).css({"border-style": "solid", "border-color": "blue"});
                //$(this).css({ "border-style": "solid", "border-color": "blue", "color": "blue" });
            }
        });
    }
});
