var patrn_rubbish = /uid|username|space|search|blog|group/;
var patrn_detail = /post|thread|detail/;
var patrn_list = /list|index|forum|fid/;
$("a").each(function () {
    var link = $(this).attr("href");
    if (patrn_rubbish.exec(link)) {
        $(this).css({"border-style": "solid", "border-color": "orange", "color": "orange"});
    }
    if (patrn_detail.exec(link)) {
        $(this).css({"border-style": "solid", "border-color": "green", "color": "green"});
    }
    if (patrn_list.exec(link)) {
        $(this).css({"border-style": "solid", "border-color": "blue", "color": "blue"});
    }
});
