#coding=gbk
import time
from pywinauto import application
app = application.Application.start('notepad.exe')
app.Notepad.MenuSelect('帮助->关于记事本'.decode('gb2312'))
time.sleep(.5)

#这里有两种方法可以进行定位“关于记事本”的对话框
#top_dlg = app.top_window_() 不推荐这种方式，因为可能得到的并不是你想要的
about_dlg = app.window_(title_re = u"关于", class_name = "#32770")#这里可以进行正则匹配title
#about_dlg.print_control_identifiers()
app.window_(title_re = u'关于“记事本”').window_(title_re = u'确定').Click()
app.Notepad.MenuSelect('帮助->关于记事本'.decode('gb2312'))
time.sleep(.5) #停0.5s 否则你都看不出来它是否弹出来了！
ABOUT = u'关于“记事本”'
OK = u'确定'
#about_dlg[OK].Click()
#app[ABOUT][OK].Click()
app[u'关于“记事本”'][u'确定'].Click()

app.Notepad.TypeKeys(u"杨彦星")
dig = app.Notepad.MenuSelect("编辑(E)->替换(R)".decode('gb2312'))
Replace = u'替换'
Cancle = u'取消'
time.sleep(.5)
app[Replace][Cancle].Click()
dialogs = app.windows_()