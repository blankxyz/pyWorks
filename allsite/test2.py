from selenium import webdriver
import exescript

d = webdriver.PhantomJS("phantomjs")
d.get("http://www.cnblogs.com/")
exejs = exescript.ExeJs(d)
exejs.exeWrap('$(".post_item").length')
print exejs.getMsg()

jsstr = """
    (function(){
    var r=[];
    $(".post_item").each(function(){
      var $this=$(this);
      var $h3=$this.find("h3");
      r.push($h3.text());
    });
    return r.join(',');})()
"""
exejs.exeWrap(jsstr)
l = exejs.getMsg()
for title in l.split(','):
    print title
