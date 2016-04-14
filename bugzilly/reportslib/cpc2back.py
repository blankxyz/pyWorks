# -*- coding: UTF-8 -*-
import os
import json
import xlwt,xlrd
import Queue
import threading

try:
    import xml.etree.cElementTree as element_tree
except ImportError:
    import xml.etree.ElementTree as element_tree

folder_list = {}  # task_list
root_path = '../cpc-export/'
# notices type:12
college_dict = {u'缴费通知书': [], u'办理登记手续通知书': [], u'手续合格通知书': [], u'第一次审查意见通知书': [],
                u'第N次审查意见通知书': [], u'第N次补正通知书': [], u'发明专利申请初步审查合格通知书': [],
                u'视为撤回通知书': [], u'费用减缓审批通知书': [], u'专利申请受理通知书': [], u'补正通知书': [],
                u'专利权终止通知书': []}

thread_list = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10", "t11"]
queue_lock = threading.Lock()
work_queue = Queue.Queue(len(college_dict))


class parse_thread(threading.Thread):
    def __init__(self, thread_id, notice_type, queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.notice_type = notice_type
        self.queue = queue

    def run(self):
        print "Starting " + self.notice_type
        # process_data(self.notice_type, self.queue)
        print "Exiting " + self.notice_type


# old_encoding='gbk' new_encoding='utf-8':list.xml -> list.xml.tmp
def replace_xml_encoding(file_path):
    file_xml = open(file_path, "r").read()
    file_xml = file_xml.replace('<?xml version="1.0" encoding="GBK"?>', '<?xml version="1.0" encoding="utf-8"?>')
    file_xml = unicode(file_xml, encoding='GBK').encode('utf-8')
    temp_file = open(file_path + '.tmp', mode='w')
    temp_file.write(file_xml)
    temp_file.close()
    return file_path + '.tmp'


# folder_list:{'GA000107254973':u'缴费通知书','GA000107499252':u'办理登记手续通知书'...}
def scan_dir(directory):
    global folder_list
    for folder in os.listdir(directory):
        tmp_path = replace_xml_encoding(root_path + folder + '/list.xml')
        tree = element_tree.parse(tmp_path)
        root = tree.getroot()
        folder_list[folder] = root.findall('TONGZHISXJ/SHUXINGXX/TONGZHISMC')[0].text
    print u'通知书共计：%d件' % len(folder_list)
    return folder_list


# return GA000108137330/list.xml
def find_detail_xml(folder):
    for xml_file in os.listdir(root_path + folder + '/' + folder + '/'):
        if xml_file.endswith('.xml') == True and xml_file.startswith(folder):
            return root_path + folder + '/' + folder + '/' + xml_file
    return ''


def college_list():
    # reformat_dict= dict((v,k) for k,v in d.iteritems())
    global college_dict
    global folder_list
    for notice_type, notice_id in college_dict.items():
        new_list = []
        for k, v in folder_list.items():
            if v == notice_type:
                new_list.append(k)
        new_dict = {notice_type: new_list}
        college_dict.update(new_dict)

    cnt = 0
    for notice_type, notice_id in college_dict.items():
        cnt += len(notice_id)
    print u'扫描通知书共：%d件' % cnt


def read_list_xml(folder):
    ret_list = {u'通知书类型': '', u'专利名称': '', u'申请号': '', u'发文日': '', u'类型': '',
                u'档案号': '', u'申请日': ''}
    try:
        replace_xml_encoding(root_path + folder + '/list.xml')
        # file_xml = open(path,"r").read()
        # file_xml = file_xml.replace('<?xml version="1.0" encoding="GBK"?>','<?xml version="1.0" encoding="utf-8"?>')
        # str = unicode(file_xml,encoding='GBK').encode('utf-8')
        # tree  = ET.fromstring(str)
        tree = element_tree.parse(root_path + folder + '/list.xml.tmp')
        root = tree.getroot()

        ret_list[u'通知书类型'] = root.findall('TONGZHISXJ/SHUXINGXX/TONGZHISMC')[0].text
        ret_list[u'专利名称'] = root.findall('TONGZHISXJ/SHUXINGXX/FAMINGMC')[0].text
        ret_list[u'申请号'] = root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGH')[0].text
        ret_list[u'发文日'] = root.findall('TONGZHISXJ/SHUXINGXX/FAWENR')[0].text
        ret_list[u'类型'] = root.findall('TONGZHISXJ/SHUXINGXX/FAMINGLX')[0].text
        ret_list[u'档案号'] = root.findall('TONGZHISXJ/SHUXINGXX/NEIBUBH')[0].text
        ret_list[u'申请日'] = root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGR')[0].text

        print ret_list
    except Exception, e:
        print "parse error:%s " % e.message + folder + '/list.xml.tmp'
    return ret_list


# 办理登记手续通知书
def register_fee_detail(folder):
    ret_list = {u'CPC档案号': '', u'通知书类型': '', u'专利名称': '', u'申请人名称': '', u'申请号': '', u'发文日': '',
                u'类型': '', u'档案号': '', u'申请日': '', u'登记费': '', u'年费': '', u'印花费': '', u'已缴费用': '',
                u'应缴费用': '', u'缴纳年费年度': '', u'截止日期': '', u'减缓标记': '', u'代理人': ''}
    try:
        # file_xml = open(path,"r").read()
        # file_xml = file_xml.replace('<?xml version="1.0" encoding="GBK"?>','<?xml version="1.0" encoding="utf-8"?>')
        # str = unicode(file_xml,encoding='GBK').encode('utf-8')
        # tree  = ET.fromstring(str)
        tree = element_tree.parse(root_path + folder + '/list.xml.tmp')
        root = tree.getroot()
        ret_list[u'CPC档案号'] = folder
        ret_list[u'通知书类型'] = root.findall('TONGZHISXJ/SHUXINGXX/TONGZHISMC')[0].text
        ret_list[u'专利名称'] = root.findall('TONGZHISXJ/SHUXINGXX/FAMINGMC')[0].text
        ret_list[u'申请号'] = root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGH')[0].text
        ret_list[u'发文日'] = root.findall('TONGZHISXJ/SHUXINGXX/FAWENR')[0].text
        ret_list[u'类型'] = root.findall('TONGZHISXJ/SHUXINGXX/FAMINGLX')[0].text
        ret_list[u'档案号'] = root.findall('TONGZHISXJ/SHUXINGXX/NEIBUBH')[0].text
        ret_list[u'申请日'] = root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGR')[0].text

        detail_xml_path = find_detail_xml(folder)
        if detail_xml_path != '':
            detail_tree = element_tree.parse(detail_xml_path)
            detail_root = detail_tree.getroot()
            fee_list = {}
            for fee in detail_root.findall('fee_info_all/fee_info/fee'):
                fee_name = fee.findall('fee_name')[0].text
                fee_list[fee_name] = fee.findall('fee_amount')[0].text

            ret_list[u'登记费'] = fee_list[u'登记费']
            ret_list[u'年费'] = fee_list[u'年费']
            ret_list[u'印花费'] = fee_list[u'印花费']

            ret_list[u'应缴费用'] = detail_root.findall('fee_info_all/fee_payable')[0].text  # 合计
            ret_list[u'已缴费用'] = detail_root.findall('fee_info_all/fee_paid')[0].text
            ret_list[u'缴纳年费年度'] = detail_root.findall('fee_info_all/annual_year')[0].text
            ret_list[u'截止日期'] = detail_root.findall('pay_deadline_date')[0].text
            ret_list[u'减缓标记'] = detail_root.findall('fee_info_all/cost_slow_flag')[0].text
            ret_list[u'代理人'] = detail_root.findall('patent_agency/agent_info/agent_name')[0].text
            names = ''
            for name in detail_root.findall('applicant_info/applicant_name'):  # Todo 申请人N
                names = names + name.text + ','
            ret_list[u'申请人名称'] = names[:-1]
    except Exception, e:
        print "parse error:%s " % e.message + folder + '/list.xml.tmp'

    return ret_list


# 缴费通知书
def annual_fee_detail(folder):
    ret_list = {u'CPC档案号': '', u'通知书类型': '', u'专利名称': '', u'申请人名称': '', u'申请号': '', u'发文日': '',
                u'类型': '', u'档案号': '', u'申请日': '', u'代理人': '', u'缴费年费年度': '', u'缴费截止日期': '',
                u'费用总金额明细': []}
    try:
        # file_xml = open(path,"r").read()
        # file_xml = file_xml.replace('<?xml version="1.0" encoding="GBK"?>','<?xml version="1.0" encoding="utf-8"?>')
        # str = unicode(file_xml,encoding='GBK').encode('utf-8')
        # tree  = ET.fromstring(str)
        tree = element_tree.parse(root_path + folder + '/list.xml.tmp')
        root = tree.getroot()
        ret_list[u'CPC档案号'] = folder
        ret_list[u'通知书类型'] = root.findall('TONGZHISXJ/SHUXINGXX/TONGZHISMC')[0].text
        ret_list[u'专利名称'] = root.findall('TONGZHISXJ/SHUXINGXX/FAMINGMC')[0].text
        ret_list[u'申请号'] = root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGH')[0].text
        ret_list[u'发文日'] = root.findall('TONGZHISXJ/SHUXINGXX/FAWENR')[0].text
        ret_list[u'类型'] = root.findall('TONGZHISXJ/SHUXINGXX/FAMINGLX')[0].text
        if len(root.findall('TONGZHISXJ/SHUXINGXX/NEIBUBH')) != 0:
            ret_list[u'档案号'] = root.findall('TONGZHISXJ/SHUXINGXX/NEIBUBH')[0].text
        if len(root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGR')) != 0:
            ret_list[u'申请日'] = root.findall('TONGZHISXJ/SHUXINGXX/SHENQINGR')[0].text

        detail_xml_path = find_detail_xml(folder)
        if detail_xml_path != '':
            detail_tree = element_tree.parse(detail_xml_path)
            detail_root = detail_tree.getroot()
            names = ''
            for name in detail_root.findall('applicant_info/applicant_name'):
                names = names + name.text + ','
            ret_list[u'申请人名称'] = names[:-1]  # Todo 申请人N
            ret_list[u'代理人'] = detail_root.findall('patent_agency/agent_info/agent_name')[0].text
            ret_list[u'缴费年费年度'] = detail_root.findall('annual_year')[0].text
            ret_list[u'缴费截止日期'] = detail_root.findall('pay_deadline_date')[0].text

            fee_list = []
            for fee in detail_root.findall('fee_info/fee'):
                pay_start_time = fee.findall('pay_start_time')[0].text  # 缴费开始时间
                pay_end_time = fee.findall('pay_end_time')[0].text  # 缴费截止时间
                annual_fee = fee.findall('annual_fee')[0].text  # 年费
                late_fee = fee.findall('late_fee')[0].text  # 滞纳金额
                totle_fee = fee.findall('totle_fee')[0].text  # 费用总金额
                fee_list.append([pay_start_time, pay_end_time, annual_fee, late_fee, totle_fee])
            ret_list[u'费用总金额明细'] = fee_list

    except Exception, e:
        print "parse error:%s " % e.message + folder + '/list.xml.tmp'

    return ret_list


# 缴费通知书
def export_annual_fee(excel_file):
    reg_sheet = excel_file.add_sheet(u'缴费通知书', cell_overwrite_ok=True)
    title = [u'CPC档案号', u'通知书类型', u'发文日', u'档案号', u'类型', u'专利名称', u'申请人', u'申请号', u'申请日',
             u'年度', u'年费', u'最高滞纳金', u'合计', u'截止日期', u'代理人']
    types = [u'发明', u'新型', u'外观']

    # write title to excel
    for j in range(0, len(title)):
        reg_sheet.write(0, j, title[j])

    # write grid data to excel
    row_num = 1
    for folder in folder_list.keys():
        if folder_list[folder] != u'缴费通知书':
            continue
        parse_detail = annual_fee_detail(folder)
        # common
        reg_sheet.write(row_num, 0, parse_detail[u'CPC档案号'])
        reg_sheet.write(row_num, 1, parse_detail[u'通知书类型'])
        reg_sheet.write(row_num, 2, parse_detail[u'发文日'])
        reg_sheet.write(row_num, 3, parse_detail[u'档案号'])
        reg_sheet.write(row_num, 4, types[int(parse_detail[u'类型'])])
        reg_sheet.write(row_num, 5, parse_detail[u'专利名称'])
        reg_sheet.write(row_num, 6, parse_detail[u'申请人名称'])
        reg_sheet.write(row_num, 7, parse_detail[u'申请号'])
        reg_sheet.write(row_num, 8, parse_detail[u'申请日'])
        # detail
        reg_sheet.write(row_num, 9, parse_detail[u'缴费年费年度'])
        detail = parse_detail[u'费用总金额明细']
        annual_fee = detail[4][2]  # 年费
        late_fee = detail[4][3]  # 最高滞纳金
        totle_fee = detail[4][4]  # 费用总金额
        reg_sheet.write(row_num, 10, annual_fee)
        reg_sheet.write(row_num, 11, late_fee)
        reg_sheet.write(row_num, 12, totle_fee)
        reg_sheet.write(row_num, 13, parse_detail[u'缴费截止日期'])
        reg_sheet.write(row_num, 14, parse_detail[u'代理人'])
        row_num += 1


# 办理登记手续通知书
def export_register_fee(excel_file):
    reg_sheet = excel_file.add_sheet(u'办理登记手续通知书', cell_overwrite_ok=True)
    title = [u'CPC档案号', u'通知书类型', u'发文日', u'档案号', u'类型', u'专利名称', u'申请人', u'申请号', u'申请日',
             u'专利登记费', u'年费', u'印花税', u'合计', u'年度', u'截止日期', u'已缴费用', u'减缓标记',
             u'代理人']
    types = [u'发明', u'新型', u'外观']

    # write title
    for j in range(0, len(title)):
        reg_sheet.write(0, j, title[j])

    # write grid data
    row_num = 1
    for folder in folder_list.keys():
        if folder_list[folder] != u'办理登记手续通知书':
            continue
        parse_detail = register_fee_detail(folder)
        reg_sheet.write(row_num, 0, parse_detail[u'CPC档案号'])
        reg_sheet.write(row_num, 1, parse_detail[u'通知书类型'])
        reg_sheet.write(row_num, 2, parse_detail[u'发文日'])
        reg_sheet.write(row_num, 3, parse_detail[u'档案号'])
        reg_sheet.write(row_num, 4, types[int(parse_detail[u'类型'])])
        reg_sheet.write(row_num, 5, parse_detail[u'专利名称'])
        reg_sheet.write(row_num, 6, parse_detail[u'申请人名称'])
        reg_sheet.write(row_num, 7, parse_detail[u'申请号'])
        reg_sheet.write(row_num, 8, parse_detail[u'申请日'])
        reg_sheet.write(row_num, 9, parse_detail[u'登记费'])
        reg_sheet.write(row_num, 10, parse_detail[u'年费'])
        reg_sheet.write(row_num, 11, parse_detail[u'印花费'])
        reg_sheet.write(row_num, 12, parse_detail[u'应缴费用'])
        reg_sheet.write(row_num, 13, parse_detail[u'缴纳年费年度'])
        reg_sheet.write(row_num, 14, parse_detail[u'截止日期'])
        reg_sheet.write(row_num, 15, parse_detail[u'已缴费用'])
        reg_sheet.write(row_num, 16, parse_detail[u'减缓标记'])
        reg_sheet.write(row_num, 17, parse_detail[u'代理人'])
        row_num += 1

def get_annual_fee_json():
    rd=xlrd.open_workbook('reportslib/jzph.xls')
    sheet = rd.sheet_by_name(u'缴费通知书')
    ret_list = {u'CPC档案号': '', u'通知书类型': '', u'专利名称': '', u'申请人名称': '', u'申请号': '', u'发文日': '',
                u'类型': '', u'档案号': '', u'申请日': '', u'代理人': '', u'缴费年费年度': '', u'缴费截止日期': '',
                u'费用总金额明细': []}
    arrs = []
    #{'CPCID','TONGZHISMC','FAMINGMC','SHENQINGH','FAWENR','FAMINGLX','NEIBUBH','SHENQINGR','agent_name','annual_year','pay_deadline_date','pay_detail'}

    value=''
    for i in range(1,12):
        if sheet.cell(i,0).value=='':
            break
        arr=[]
        for j in range(14):
            print i,'  ',j,'  :',sheet.cell(i,j).value
            value=sheet.cell(i,j).value
            arr.append(value)
            j+=1
        arrs.append(arr)
        i+=1

    json_str = json.dumps(arrs)
    f=open("annual.json","w")
    f.write(json_str)
    f.close()
    return json_str

def get_register_fee_json():
    rd=xlrd.open_workbook('reportslib/jzph.xls')
    sheet = rd.sheet_by_name(u'办理登记手续通知书')
    for i,j in range(100):
        value=sheet.cell(i,j).value

if __name__ == '__main__':
    scan_dir(root_path)
    college_list()
    f = xlwt.Workbook()
    export_register_fee(f)
    export_annual_fee(f)
    f.save('reportslib/jzph.xls')
    get_annual_fee_json()
