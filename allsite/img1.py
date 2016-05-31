# -*- coding: utf-8 -*-

import Image
import ImageDraw


def showHist(im, w=512, h=512):
    hist = im.convert('L').histogram()

    hist = map(lambda i: h - h * i / max(hist), hist)  # 归一化, 之后会有误差

    w = w % 256 and 256 * (w / 256 + 1) or w  # 保证宽是256的倍数

    im2 = Image.new('L', (w, h), 255)

    draw = ImageDraw.Draw(im2)

    step = w / 256  # 每个矩形的宽度

    [draw.rectangle([i * step, hist[i], (i + 1) * step, h], fill=0)
     for i in range(256)]

    im2.show()


def aaaa():
    capture_img = 'd:\org.png'
    convert_img = 'd:\convert.png'
    image = Image.open(capture_img).convert(
        'L')  # 量化（黑：0，2,4,8,16,32,64，128，白：255）
    image.save(convert_img)
    _image_handle = Image.open(convert_img)  # 量化（黑：0 白：255）
    max_width, max_high = _image_handle.size
    for x in range(max_width):
        for y in range(max_high):
            # if 28<x<600 and 1315 < y< 1500 : # 文字
            if 0 < x and 1850 < y < 2400:  # 图片文字
                print x, y, _image_handle.getpixel((x, y))


def test():
    im = Image.open('d:/web-links.png')

    showHist(im, 512, 512)


if __name__ == '__main__':
    # test()
    aaaa()
