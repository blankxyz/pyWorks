function httpRequest(url, callback){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    };
    xhr.send();
}

function showRegexs(result){
    result = JSON.parse(result);
    var list_regexs = JSON.parse(result).list_regexs;
    var detail_regexs = JSON.parse(result).detail_regexs;
    // list_regexs= [{"regex":"list-","weight":"1"},{"regex":"index","weight":"1"},{"regex":"aaaa","weight":"1"}];
    var table = '<table><tr><th>分类(列表/详情)</th><th>正则表达式</th><th>权重</th><th>采用</th></tr>';
    for(var i in list_regexs){
        table += '<tr>';
        table += '<td>列表</td>';
        table += '<td>'+list_regexs[i].regex+'</td>';
        table += '<td>'+list_regexs[i].weight+'</td>';
        table += '<td>use</td>';
        table += '</tr>';
    }
    for(var i in detail_regexs){
        table += '<tr>';
        table += '<td>详情</td>';
        table += '<td>'+detail_regexs[i].regex+'</td>';
        table += '<td>'+detail_regexs[i].weight+'</td>';
        table += '<td>use</td>';
        table += '</tr>';
    }
    table += '</table>';
    document.getElementById('regexs').innerHTML = table;
}

var city = localStorage.city;
city = city?city:'beijing';
var url = 'http://172.16.5.152:5000/regexs/list';
httpRequest(url, showRegexs);