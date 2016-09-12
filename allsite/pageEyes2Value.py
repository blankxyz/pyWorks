# coding=utf-8
import time
import Image
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
        self._Nx = 5   # 采样倍率
        self._Ny = 5
        self._image_handle = None

    def delete_advert(self):
        pass # todo 删除广告

    def filter_noice(self):
        pass # todo 保留(2)内容文字和图片

    def is_jqueryLoaded(self, driver):
        try:
            loaded = driver.executeScript("return " + "jQuery()!=null")
        except Exception:
            loaded = None
        return loaded

    def sample_range(self, size, n):
        return [i * n for i in range(1024) if i * n < size]

    # 在_window_width _window_high 范围内 黑色点数比例小于 _space_window_rate
    # 则被认定为空白区域
    def is_space_window(self, image, X, Y):
        global _max_width, _max_high

        x_list = self.sample_range(self._window_width, self._Nx)
        y_list = self.sample_range(self._window_high, self._Ny)
        rank = len(x_list) * len(y_list) * self._space_window_rate

        if X + self._window_width >= self._max_width or Y + self._window_high >= self._max_high:
            return None
        else:
            cnt = 0
            for x in x_list:
                for y in y_list:
                    flag = image.getpixel((X+x, Y+y))
                    if flag == 0:  # 黑色区域
                        cnt = cnt + 1

            # print X,Y,"is_space_window?:", "rank:", rank, cnt
            return True if cnt <= rank else False

    def get_space_window_pixel_cnt(self, set_xy):
        _set_in_window = set()
        for (X,Y) in set_xy: # (X,Y)为偏移量
            for x in self.sample_range(self._window_width, self._Nx):
                for y in self.sample_range(self._window_high, self._Ny):
                    _set_in_window.add((X+x,Y+y))
        return len(_set_in_window)

    def capture(self, url, capture_img):
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
            $("embed").removeAttr("src")
            $(document).ready(function(){
                $("a").css({"background":"black","color":"black"});
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

    def img_init(self, capture_img, convert_img):
        image = Image.open(capture_img).convert('1')  # 量化（黑：0 白：255）
        # print image.mode
        image.save(convert_img)
        self._image_handle = Image.open(convert_img)
        self._max_width,self._max_high = self._image_handle.size

    def img_parse(self):
        _set_xy_space_window = set()
        cnt = 0
        space_line_cnt = 0
        x_list = self.sample_range(self._max_width, self._Nx)
        y_list = self.sample_range(self._max_high, self._Ny)
        sample_pixels = len(x_list) * len(y_list)
        print "picture width:", self._max_width, "high:", self._max_high, " sample_pixels :", sample_pixels

        for y in y_list:
            row_cnt = 0
            for x in x_list:
                val = self._image_handle.getpixel((x, y))
                if val == 0:  # 黑色区域
                    cnt = cnt + 1
                else:  # 白色区域
                    row_cnt = row_cnt + 1

            print y, row_cnt, len(x_list) * self._space_line_rate
            if row_cnt < len(x_list) * self._space_line_rate:  # 少于行采样点数的5% 认为是空白行
                space_line_cnt = space_line_cnt + 1

        # print "space_line_cnt:", space_line_cnt
        # sample_pixels_nospace = sample_pixels - len(x_list) * space_line_cnt

        space_window_pixel_cnt = self.get_space_window_pixel_cnt(set_xy=_set_xy_space_window)
        sample_pixels_nospace = sample_pixels - space_window_pixel_cnt
        print "get_space_window_pixel_cnt:",space_window_pixel_cnt
        print "black pixels count:", cnt
        print "black pixels/sample pixels :", cnt / float(sample_pixels)
        print "black pixels/(sample sum no space) :", cnt / float(sample_pixels_nospace)
        # print image.histogram()
        # image.show()


if __name__ == "__main__":
    start = time.clock()
    url = 'http://www.sina.com.cn/' # link full
    url = 'http://zx.jiaju.sina.com.cn/2011571/' # 装修 list imageful
    url = 'http://sports.sina.com.cn/basketball/nba/2016-05-23/doc-ifxsktkr5904181.shtml' # sport detail
    # url = 'http://news.sina.com.cn/'
    capture_img = 'd:\pageEyes2Value_org.png'
    convert_img = 'd:\pageEyes2Value_convert.png'

    myPageEyes = PageEyes()
    print "sample Nx:", myPageEyes._Nx, "Ny:", myPageEyes._Ny
    myPageEyes.capture(url, capture_img)
    myPageEyes.img_init(capture_img, convert_img)
    myPageEyes.img_parse()
    # //div[contains(@class,'list')]
    end = time.clock()
    print "exec times is: %f s" % (end - start)
