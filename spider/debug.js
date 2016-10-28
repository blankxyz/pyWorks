var page = require('webpage').create();
// var system = require('system');
page.open('http://bbs.tianya.cn', function () {
    page.includeJs("http://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js", function () {
        page.evaluate(function () {
            var patrn_rubbish = /uid|username|space|search|blog|group/;
            var patrn_detail = /post|thread|detail/;
            var patrn_list = /list|index|forum|fid/;
            $("a").each(function () {
                var link = $(this).attr("href");
                if (patrn_rubbish.exec(link)) {
                    $(this).css({"border-style": "solid", "border-color": "red", "color": "red"});
                }
                if (patrn_detail.exec(link)) {
                    $(this).css({"border-style": "solid", "border-color": "green", "color": "green"});
                }
                if (patrn_list.exec(link)) {
                    $(this).css({"border-style": "solid", "border-color": "blue", "color": "blue"});
                }
            });
        });
        var content = page.content;
        page.render('test.png');
        console.log("title:");
        console.log(content);
        console.log("end.");
        phantom.exit();
    });
});