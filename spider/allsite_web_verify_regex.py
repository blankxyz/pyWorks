# coding=utf-8
import os, time
from selenium import webdriver


class VerifyRegex(object):
    def __init__(self, patrn_rubbish, patrn_list, patrn_detail):
        # self._loadJsFmt = """
        #     var script = document.createElement('script');
        #     script.src = "{0}";
        #     document.body.appendChild(script);
        # """
        # self._jquery_cdn = "http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.3.js"

        self.inject_jquery = """
            var jq = document.createElement('script');
            jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js";
            document.getElementsByTagName('head')[0].appendChild(jq);
            jQuery.noConflict();
        """
        self.patrn_rubbish = patrn_rubbish
        self.patrn_detail = patrn_detail
        self.patrn_list = patrn_list
        # self._browse_window_width = 800
        # self._browse_window_high = 600

    def is_jqueryLoaded(self, driver):
        try:
            loaded = driver.executeScript("return " + "jQuery()!=null")
        except Exception:
            loaded = None
        return loaded

    def verify(self, url, capture_img=None):
        # system.setProperty("webdriver.chrome.driver",
        #                    "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome");
        if os.name == 'nt':  # windows
            driver = webdriver.Chrome('d:\\chromedriver.exe')
        else:  # linux
            driver = webdriver.Chrome('/usr/local/bin/chromedriver')

        # driver = webdriver.Firefox()
        # driver.set_window_size(self._browse_window_width, self._browse_window_high)
        driver.maximize_window()
        driver.implicitly_wait(1)
        driver.get(url)
        # driver.implicitly_wait(30)
        driver.execute_script("""
            (function () {
              var y = 0;
              var step = 100;
              window.scroll(0, 0);
              function f() {
                if (y < document.body.scrollHeight) {
                  y += step;
                  window.scroll(0, y);
                  setTimeout(f, 50);
                } else {
                  window.scroll(0, 0);
                  document.title += "scroll-done";
                }
              }
              setTimeout(f, 1000);
            })();
          """)
        for i in xrange(30):
            if "scroll-done" in driver.title:
                break
            time.sleep(1)
            # if self.is_jqueryLoaded(driver) is None:  # inject jquery
            # ret=driver.execute_script(self._loadJsFmt.format(self._jquery_cdn))
        ret = driver.execute_script(self.inject_jquery)  # inject jquery
        print ret
        js1 = '''
            jQuery(document).ready(function(){
                var patrn_rubbish = /uid|username|space|search|blog|group/;
                var patrn_detail = /post|thread|detail/;
                var patrn_list = /list|index|forum|fid/;
                jQuery("a").each(function () {
                    var link = jQuery(this).attr("href");
                    if (patrn_rubbish.exec(link)) {
                        jQuery(this).css({"border-style": "solid", "border-color": "orange", "color": "orange"});
                    }
                    if (patrn_detail.exec(link)) {
                        jQuery(this).css({"border-style": "solid", "border-color": "green", "color": "green"});
                    }
                    if (patrn_list.exec(link)) {
                        jQuery(this).css({"border-style": "solid", "border-color": "blue", "color": "blue"});
                    }
                });
            });
            '''
        js = '''
            jQuery(document).ready(function(){
                var patrn_rubbish = /uid|username|space|search|blog|group/;
                var patrn_detail = /''' + self.patrn_detail + '''/;
                var patrn_list = /''' + self.patrn_list + '''/;
                jQuery("a").each(function () {
                    var link = jQuery(this).attr("href");
                    if (patrn_rubbish.exec(link)) {
                        jQuery(this).css({"border-style": "solid", "border-color": "orange", "color": "orange"});
                    }
                    if (patrn_detail.exec(link)) {
                        jQuery(this).css({"border-style": "solid", "border-color": "green", "color": "green"});
                    }
                    if (patrn_list.exec(link)) {
                        jQuery(this).css({"border-style": "solid", "border-color": "blue", "color": "blue"});
                    }
                });
            });
            '''
        print '[info]VerifyRegex() javascript:', js
        driver.execute_script(js)
        time.sleep(60)
        # if capture_img:
        #     driver.get_screenshot_as_file(capture_img)
        driver.quit()


if __name__ == "__main__":
    url = 'http://bbs.tianya.cn/'  # link full
    capture_img = 'allsite_web_verify_regex.png'

    v = VerifyRegex()
    v.verify(url, capture_img)
