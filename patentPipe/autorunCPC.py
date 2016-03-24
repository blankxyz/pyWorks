#coding=gbk
import time
from pywinauto import application

app = application.Application.start('D:\gwssi\CPC客户端\CPC.exe'.decode('gb2312'))
MainDlg=app.top_window_()
#find_dlg = app.window_(title_re = 'WindowsForms10.Window.8.app.0.218f99c', class_name = u'官文同步导出')
#find_dlg.print_control_identifiers()
app.window_(title_re = u'批量接口').window_(title_re = u'通知书接口').Click()
#find_dlg.TypeKeys("^P")
time.sleep(.5)
#dialogs = app.windows_()