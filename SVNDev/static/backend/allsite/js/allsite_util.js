if (typeof window.sessionStorage == 'undefined') {
    alert("浏览不支持sessionStorage");
}

function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        return decodeURI(r[2]);
    }
    return null;
}
function gotoPage() {
    var link = $('#firstPage').attr("href");
    var page = $("#gotoPageNum").val();
    link = link.substring(0, link.length - 1);
    page = page.replace(/[_]/g, "");
    //alert(link + page);
    if (1 <= page && page <= window.sessionStorage.getItem("total_pages")) {
        window.location.href = link + page;
    }
}

function setPaginator(searchCnt, search, selectCond, times, currentPage, totalPages) {
    if (currentPage == null || totalPages == null) return;
    if (searchCnt == 0) return;

    var current = parseInt(currentPage);
    var total = parseInt(totalPages);
    var hasPrev = current > 1;
    var hasNext = current < total;
    var link = "?";

    if (search.length > 0) {
        link += "search=" + search;
    }
    if (selectCond.length > 0) {
        link += "&selectCond=" + selectCond;
    }
    if (times.length > 0) {
        link += "&times=" + times;
    }
    link += "&page=";

    $('#firstPage').attr("href", link + "1");
    if (hasPrev) {
        var p = current - 1;
        $('#prevPage').attr("href", link + p);
    } else {
        $('#prevPage').attr("href", "#");
    }
    $('#pageNum').text("共 " + total + " 页");
    if (hasNext) {
        var n = current + 1;
        $('#nextPage').attr("href", link + n);
    } else {
        $('#nextPage').attr("href", "#");
    }
    $('#lastPage').attr("href", link + total);

    $('#pageDiv').show();
}
