# coding=utf-8
import time
import Image
from selenium import webdriver
from PIL import Image
from pylab import *

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
        self._Nx = 1   # 采样倍率
        self._Ny = 1
        self._image_handle = None # img_init()

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

    def capture(self, url, capture_img):
        driver = webdriver.Firefox()
        driver.set_window_size(self._browse_window_width, self._browse_window_high)
        # driver.maximize_window()
        driver.implicitly_wait(1)
        driver.get(url)
        if self.is_jqueryLoaded(driver) is None:  # inject jquery
            driver.execute_script(self._loadJsFmt.format(self._jquery_cdn))

        # 上层的第一个Div
        js = '''
            $(document).ready(function(){

                $("a").css({"background":"black","color":"black"});
                $("a").each(function(){
                    $(this).find("img").removeAttr("src").css("background","black");
                    if($(this).closest("div").find("a").length>3){
                        $(this).closest("div").css({"background":"black","color":"black"});
                    }
                });
            });
            '''
        # 近上层为Div
        js1 = '''
            $(document).ready(function(){
                $("a").css({"background":"black","color":"black"});
                $("a").each(function(){
                    $(this).children("img").removeAttr("src").css("background","black");
                    if($(this).siblings("a").length>3){
                        $(this).parent("div").css({"background":"black","color":"black"});
                    }
                });
            });
            '''
        # 获取图片长宽，配置img的width，height
        js2 = '''
            $(document).ready(function(){
                $("p").css("font-weight":"bold","font-size":"xx-large";);
                $("img").each(function(i){
                    var img = $(this);
                    var realWidth;
                    var realHeight;
                    $(this).attr("src", $(this).attr("src")).load(function() {
                        realWidth = this.width;
                        realHeight = this.height;
                        $(img).css("width",realWidth+'px').css("height",realHeight+'px');
                        $(img).removeAttr("src").css("background","black");
                    });
                });
            });
        '''
        driver.execute_script(js2)

        # screen capture
        driver.get_screenshot_as_file(capture_img)
        driver.close()

    def img_init(self, capture_img, convert_img):
        # Multi-level quantization
        image = Image.open(capture_img).convert('L')  # 量化（黑：0，2,4,8,16,32,64，128，白：255）
        print "image.mode:", image.mode
        image.save(convert_img)
        self._image_handle = Image.open(convert_img)
        self._max_width,self._max_high = self._image_handle.size

    def img_quantization(self, pixelValue):
        if 0< pixelValue <=15:
            return 16
        elif 16< pixelValue <=3:
            return 8
        elif 32< pixelValue <=63:
            return 4
        elif 64< pixelValue <=127:
            return 2
        elif 128< pixelValue <=255:
            return 1
        else:
            return 0

    def img_parse(self):
        q_sum,q = 0,0
        x_list = self.sample_range(self._max_width, self._Nx)
        y_list = self.sample_range(self._max_high, self._Ny)
        sample_pixels = len(x_list) * len(y_list)
        print "picture width:", self._max_width, "high:", self._max_high, " sample_pixels :", sample_pixels

        for y in y_list:
            row_cnt = 0
            for x in x_list:
                val = self._image_handle.getpixel((x, y))
                q = self.img_quantization(val)
                # print x, y, val, q
                q_sum = q_sum + q

        print "q_sum:", q_sum

        print "black pixels/sample pixels :", q_sum / float(sample_pixels)


if __name__ == "__main__":
    start = time.clock()
    url = 'http://www.sina.com.cn/' # link full
    # url = 'http://zx.jiaju.sina.com.cn/2011571/' # list 大量图片 余白较多
    # url = 'http://jiaju.sina.com.cn/zt/sofaclub-project/' # list 大量图片
    # url = 'http://sports.sina.com.cn/basketball/nba/2016-05-23/doc-ifxsktkr5904181.shtml' # detail sport
    # url = 'http://news.sina.com.cn/' #list
    # url = 'http://auto.sina.com.cn/' # list 大量图片
    # url = 'http://corp.sina.com.cn/chn/copyright.html' # detail(3)
    # url = 'http://stock.finance.sina.com.cn/fundInfo/view/FundInfo_ZCFZ.php?symbol=000410' # detail(2)
    # url = 'http://slide.sports.sina.com.cn/g_pl/slide_2_61364_95215.html#p=1' # detail(3)
    # url = 'http://nba.sports.sina.com.cn/star/Luc%20Richard-Mbah%20a%20Moute.shtml' #detail(3) ???
    # url = 'http://sports.sina.com.cn/video/g/premierleaguemagiccube/15_12/#250441943' #detail(2) 去除视频才能识别
    # url = 'http://jl.sina.com.cn/news/2/2016-01-04/detail-ifxncyar6261978-p3.shtml' # detail(1) ??? 主识别区
    capture_img = 'd:\pageEyesMultiLevel_org.png'
    convert_img = 'd:\pageEyesMultiLevel_convert.png'

    myPageEyes = PageEyes()
    print "url:",url
    print "sample Nx:", myPageEyes._Nx, "Ny:", myPageEyes._Ny
    myPageEyes.capture(url, capture_img)
    myPageEyes.img_init(capture_img, convert_img)
    # myPageEyes.img_parse()

    # //div[contains(@class,'list')]
    end = time.clock()
    print "exec times is: %f s" % (end - start)
    # capture_img = "d:\pageEyesMultiLevel_convert.png"
    # 读取图像到数组中
    im = array(Image.open(capture_img).convert('L'))
    imshow(im)
    figure()
    gray()
    contour(im, origin='image')
    axis('equal')
    axis('off')

    figure()
    hist(im.flatten(), 256)
    show()
