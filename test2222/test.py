import PIL

import Image
import ImageDraw

im = Image.open('1.png')
(width, hight) = im.size
print hight, width
if width > 1024:
    h = hight * 1024 / width
    new_img = im.resize((1024, h))
    new_img.save("1.png")
    new_img.show()

