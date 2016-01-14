/**
 * use by statusChange.html.
 */
var $SCRIPT_ROOT = { request.script_root | tojson | safe};
$(document).ready(function () {
    $("table").click(function () {
        var str = $(this).attr("id");
        var bugId = str.substr("tab_".length);
        var cnt = $("tr[id^=tr_c_" + bugId + "] > td").size() - 2;
        for (var i = 0; i < cnt; i++) {
            if ($("td[id^=td_c_" + bugId + "_" + i + "]").text().search("→REOPENED") > 0) {
                fontcolor = "red";
            } else {
                fontcolor = "black";
            }
            $("td[id^=td_m_" + bugId + "_" + i + "]").toggle("fast");
            $("td[id^=td_c_" + bugId + "_" + i + "]").toggle("normal");
            $("td[id^=td_c_" + bugId + "_" + i + "]").css("color",fontcolor);
            $("td[id^=td_t_" + bugId + "_" + i + "]").toggle("slow");

            $("td[id^=td_c_" + bugId + "_" + i + "] li").hover(function() {
                $(this).find("em[id$='comment']").animate({opacity: "show", top: "-175"}, "fast");
            }, function() {
                $(this).find("em[id$='comment']").animate({opacity: "hide", top: "-85"}, "fast");
            });
        }
        <!-- set last info allow show -->
        if ($("td[id^=td_c_" + bugId + "_" + cnt + "]").text().search("→CLOSED") > 0) {
            bgcolor = "Gray";
        } else {
            bgcolor = "red";
        }
        $("td[id^=td_c_" + bugId + "_" + cnt + "]").css("background-color",bgcolor);
    });
});
