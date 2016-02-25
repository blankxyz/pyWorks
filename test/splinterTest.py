# -*- coding: utf-8 -*-
#encoding=utf-8
import sys, re
from splinter.browser import Browser

CLOASE_AFTER_TEST = False
reload(sys)
sys.setdefaultencoding('utf8')
encoding = lambda x:x.encode('gbk')

def testLogin(desc, username, password, result):
    output(desc)
    browser.fill('TPL_username',username.decode('utf8'))
    browser.fill('TPL_password',password.decode('utf8'))
    browser.find_by_value('登录').first.click()
    checkresult(result)

def output(x):
    print encoding(x)

def resultMsg(x):
    if x == True:
        print 'pass'
    else:
        print '[X]not pass'

def checkresult(x):
    """  check result message, x : the error message u want  """
    resultMsg(browser.is_text_present(x))

__testUrl = 'http://waptest.taobao.com/login/login.htm?tpl_redirect_url=http%3A%2F%2Fm.taobao.com%2F'

# chrome driver : http://code.google.com/p/selenium/wiki/ChromeDriver
browser = Browser()  # already support firefox
browser.visit(__testUrl)
output("测试页面:"+browser.title)

try:
    # test login
    testLogin('测试未输入用户名','songyq0509@163.com','','请输入会员名')
    testLogin('测试未输入密码','qd_test_001','','请输入密码')
    testLogin('测试帐户不存在','这是一个不存在的名字哦','xxxxxxx','该账户名不存在')
    testLogin('测试成功登录','qd_test_001','taobao1234','继续登录前操作')

    # test find password
    output("测试[找回密码]链接")
    browser.visit(__testUrl)
    backPasswordLink = browser.find_link_by_text('取回密码')
    if 1 == len(backPasswordLink):
        backPasswordLink.first.click()
        ru = re.findall(re.compile(".*(reg/gp.htm).*", re.IGNORECASE), browser.url)
        if ru is not None:
            checkresult('找回密码')
        else:
            output("测试找回密码链接失败")

except Exception,x:
    print x

if CLOASE_AFTER_TEST:
    browser.quit()