function httpRequest(url, callback){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    }
    xhr.send();
}

function showWeather(result){
    result = JSON.parse(result);
    var list = result.list;
    var table = '<table><tr><th>列表/详情</th><th>正则</th><th>权重</th><th>采用</th></tr>';
    for(var i in list){
        table += '<tr>';
        table += '<td>'+list[i].regexType+'</td>';
        table += '<td>'+list[i].regex+'</td>';
        table += '<td>'+list[i].weight+'</td>';
        table += '<td>'+use+'</td>';
        table += '</tr>';
    }
    table += '</table>';
    document.getElementById('regexList').innerHTML = table;
}

var city = localStorage.city;
city = city?city:'beijing';
var url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q='+city+',china&lang=zh_cn';
httpRequest(url, showWeather);