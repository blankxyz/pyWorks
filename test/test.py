# coding=utf-8
import sys, os
import time
import keyword
import ConfigParser
from selenium import webdriver
from selenium.webdriver import ActionChains

if __name__ == "__main__":
    # ----读取testConfig.ini文件------------------------------------------
    cf = ConfigParser.ConfigParser()
    cf.read("./testConfig.ini")
    host = cf.get("loginConf", "host")
    port = cf.getint("loginConf", "port")
    user = cf.get("loginConf", "user")
    pwd = cf.get("loginConf", "password")
    url = "http://" + host + ":" + str(port) + "/login"
    # ------------------------------------------------------------------
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.implicitly_wait(1)
    # Login------------------------------------------------------------
    driver.get(url)
    driver.find_element_by_id('uid').send_keys(user)
    driver.find_element_by_id('pwd').send_keys(pwd)
    inputs = driver.find_elements_by_tag_name('input')
    for input in inputs:
        if input.get_attribute('type') == 'checkbox':
            input.click()  # 勾选下次自动登录
    driver.find_element_by_id("btn-login").submit()
    # driver.implicitly_wait(1)
    # 切换至"人事基本信息"---------------------------------------------
    driver.switch_to.default_content()
    #driver.switch_to.frame("leftFrameset")
    driver.switch_to.frame('menu')
    driver.find_element_by_link_text(u"人事管理").click()
    driver.find_element_by_link_text(u"人事基本信息").click()
    #driver.find_element_by_id("1201").click()
    #driver.implicitly_wait(30)
    # 切换至"人事基本信息"tab-------------------------------------------
    driver.switch_to.default_content()
    driver.switch_to.frame('rtop')
    framelist = driver.find_elements_by_tag_name("iframe")  # 3件： 0首页、1人事管理、2人事基本信息
    print len(framelist)
    for f in framelist:
        print 'iframe style is:' + f.get_attribute('style')

    driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[2])  # 2:人事基本信息
    # links = driver.find_elements_by_tag_name("a")
    # print len(links)
    # for link in links:
    #      print link.get_attribute('class')
    #      print link.get_attribute('stype')
    # 点击"新增"----------------------------------------------
    time.sleep(5)  #等待人事信息列表显示完毕
    print 'wait for click ' + driver.find_element_by_id("add").text
    #driver.find_element_by_link_text(u'新增').click()
    driver.find_element_by_id("add").click()
    time.sleep(1)
    # 切换至"基本信息"tab-------------------------------------------
    #driver.find_element_by_id('sex').find_element_by_xpath("//option[@value='1']").click()
    driver.find_element_by_id("employeeName").send_keys(u"卫高俊")  # 姓名
    driver.find_element_by_css_selector("a.textbox-icon.combo-arrow").click()
    driver.find_element_by_id("_easyui_combobox_i1_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[2]/td[8]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i32_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[2]/td[8]/span[2]/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i35_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[3]/td[2]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i19_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[3]/td[4]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i38_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[3]/td[6]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i28_0").click()
    driver.find_element_by_id("No_id").send_keys("532628197407119174")  #身份证号码
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[4]/td[6]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i7_1").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[4]/td[8]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i8_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[5]/td[2]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i39_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div/table/tbody/tr[5]/td[4]/span/span/a").click()
    driver.find_element_by_xpath("//div/div[2]/table/tbody/tr[2]/td[4]").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div[3]/table/tbody/tr[2]/td[2]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i40_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div[3]/table/tbody/tr[2]/td[2]/span[2]/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i43_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div[3]/table/tbody/tr[3]/td[2]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i34_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div[3]/table/tbody/tr[3]/td[2]/span[2]/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i44_0").click()
    driver.find_element_by_xpath("//form[@id='basicInfoForm']/div[3]/table/tbody/tr[3]/td[4]/span/span/a").click()
    driver.find_element_by_id("_easyui_combobox_i42_1").click()
    driver.find_element_by_id("mobile").send_keys("13812345678")
    driver.find_element_by_name("urgentLinkMan").send_keys(u"朝阳大妈")
    driver.find_element_by_id("urgentPhone").send_keys("13812345678")
    driver.find_element_by_id("email").send_keys("123@163.com")
    # driver.find_element_by_id('nativeProvince').send_keys(u'福建省')
    # driver.find_element_by_id('nativeCity').send_keys(u'福州市')
    # driver.find_element_by_id('nation').send_keys(u'中国')
    # driver.find_element_by_id('idType').send_keys(u'身份证')
    # driver.find_element_by_id('No_id').send_keys('532628197407119174')
    # driver.find_element_by_id('birthday').send_keys('1974-07-11')
    # driver.find_element_by_id('age').send_keys('41')
    # driver.find_element_by_id('maritalStatus').send_keys(u'已婚')
    # driver.find_element_by_id('healthState').send_keys(u'良好')
    #
    # driver.find_element_by_id('registerCity').send_keys(u'福建省')
    # driver.find_element_by_id('registerArea').send_keys(u'福州市')
    # driver.find_element_by_id('liveCity').send_keys(u'福建省')
    # driver.find_element_by_id('liveArea').send_keys(u'福州市')
    # driver.find_element_by_id('registerKind').send_keys(u'本埠城镇')
    #
    # driver.find_element_by_id('mobile').send_keys('13812345678')
    # driver.find_element_by_name('urgentLinkMan').send_keys(u'张')
    # driver.find_element_by_id('urgentPhone').send_keys('13812345678')
    # driver.find_element_by_id('email').send_keys('13812345678@163.com')

    #driver.find_element_by_link_text(u'保存').click()
    #driver.quit()