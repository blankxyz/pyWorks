#coding=gbk
import time
from pywinauto import application
app = application.Application.start('notepad.exe')
app.Notepad.MenuSelect('����->���ڼ��±�'.decode('gb2312'))
time.sleep(.5)

#���������ַ������Խ��ж�λ�����ڼ��±����ĶԻ���
#top_dlg = app.top_window_() ���Ƽ����ַ�ʽ����Ϊ���ܵõ��Ĳ���������Ҫ��
about_dlg = app.window_(title_re = u"����", class_name = "#32770")#������Խ�������ƥ��title
#about_dlg.print_control_identifiers()
app.window_(title_re = u'���ڡ����±���').window_(title_re = u'ȷ��').Click()
app.Notepad.MenuSelect('����->���ڼ��±�'.decode('gb2312'))
time.sleep(.5) #ͣ0.5s �����㶼�����������Ƿ񵯳����ˣ�
ABOUT = u'���ڡ����±���'
OK = u'ȷ��'
#about_dlg[OK].Click()
#app[ABOUT][OK].Click()
app[u'���ڡ����±���'][u'ȷ��'].Click()

app.Notepad.TypeKeys(u"������")
dig = app.Notepad.MenuSelect("�༭(E)->�滻(R)".decode('gb2312'))
Replace = u'�滻'
Cancle = u'ȡ��'
time.sleep(.5)
app[Replace][Cancle].Click()
dialogs = app.windows_()