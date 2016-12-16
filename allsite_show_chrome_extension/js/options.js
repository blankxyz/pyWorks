//http://172.16.5.152:9000/
// var hostIP = localStorage.hostIP;

// var hostIP = hostIP ? hostIP : 'http://172.16.5.152:9000';

// document.getElementById('hostIP').value = hostIP;
document.getElementById('save').onclick = function () {
    var hostIP = document.getElementById('hostIP').value;
    // var hostIP = $('#hostIP').val();
    // $.cookie("hostIP", hostIP);
    chrome.cookies.set({
        'url': 'localhost',
        'name': 'hostIP',
        'value': hostIP,
        'secure': false,
        'httpOnly': false
    });
    alert("hostIP: " + localStorage.hostIP + " save ok!");
};