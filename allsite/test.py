# coding=utf-8
import time
from selenium import webdriver

class PageEyes(object):
    def __init__(self):
        self._loadJsFmt = """
            var script = document.createElement('script');
            script.src = "{0}";
            document.body.appendChild(script);
        """
        self._jquery_cdn = "http://cdn.bootcss.com/jquery/2.2.3/jquery.min.js"

        self._browse_window_width = 800
        self._browse_window_high = 600

        self._space_window_rate = 0.1
        self._window_width = 400
        self._window_high = 200

        self._max_width = 800  # js 加载后从截图得到
        self._max_high = 600  # js 加载后从截图得到
        self._space_line_rate = 0.2
        self._Nx = 5  # 采样倍率
        self._Ny = 5
        self._image_handle = None


    def is_jqueryLoaded(self, driver):
        try:
            loaded = driver.executeScript("return " + "jQuery()!=null")
        except Exception:
            loaded = None
        return loaded

    def capture(self, url, capture_img):
        # system.setProperty("webdriver.chrome.driver",
        #                    "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome");
        driver = webdriver.Chrome()
        driver.set_window_size(self._browse_window_width, self._browse_window_high)
        # driver.maximize_window()
        driver.implicitly_wait(1)
        driver.get(url)
        # driver.execute_script("""
        #     (function () {
        #       var y = 0;
        #       var step = 100;
        #       window.scroll(0, 0);
        #
        #       function f() {
        #         if (y < document.body.scrollHeight) {
        #           y += step;
        #           window.scroll(0, y);
        #           setTimeout(f, 50);
        #         } else {
        #           window.scroll(0, 0);
        #           document.title += "scroll-done";
        #         }
        #       }
        #       setTimeout(f, 1000);
        #     })();
        #   """)
        # for i in xrange(30):
        #     if "scroll-done" in driver.title:
        #         break
        #     time.sleep(1)
        if self.is_jqueryLoaded(driver) is None:  # inject jquery
            driver.execute_script(self._loadJsFmt.format(self._jquery_cdn))

        js = '''
            var patrn_rubbish = /uid|username|space|search|blog|group/;
            var patrn_detail = /post|thread|detail/;
            var patrn_list = /list|index|forum|fid/;
            $("embed").removeAttr("src")
            $(document).ready(function(){
                $("a").css({"borderColor":"blue","color":"red"});
                $("a").each(function(){
                    $(this).children("img").removeAttr("src").css("background","black");
                    if($(this).siblings("a").length>3){
                        // alert($(this).siblings("a").length);
                        $(this).parent("div").css({"background":"black","color":"black"});
                    }
                });
            });
            '''
        driver.execute_script(js)

        # screen capture
        driver.get_screenshot_as_file(capture_img)
        driver.close()


if __name__ == "__main__":
    start = time.clock()
    url = 'http://bbs.tianya.cn/'  # link full
    # url = 'http://zx.jiaju.sina.com.cn/2011571/'  # 装修 list imageful
    # url = 'http://sports.sina.com.cn/basketball/nba/2016-05-23/doc-ifxsktkr5904181.shtml'  # sport detail
    # url = 'http://news.sina.com.cn/'
    capture_img = 'test.png'

    myPageEyes = PageEyes()
    myPageEyes.capture(url, capture_img)
