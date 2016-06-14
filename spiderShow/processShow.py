from flask import Flask, render_template
# import matplotlib.pyplot as plt

app = Flask(__name__)


def convert_file_to_list():
    rule0_cnt = []
    rule1_cnt = []
    detail_cnt = []
    list_cnt = []
    list_done_cnt = []
    times = []

    fp = open("process.json", 'r')
    for line in fp.readlines():
        dic = eval(line)
        times.append(dic.get('times'))
        rule0_cnt.append(dic.get('rule0_cnt'))
        rule1_cnt.append(dic.get('rule1_cnt'))
        detail_cnt.append(dic.get('detail_cnt'))
        list_cnt.append(dic.get('list_cnt'))
        list_done_cnt.append(dic.get('list_done_cnt'))
    fp.close()
    return times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt

def convert_file_to_list_crumbs():
    crumbs_cnt = []
    hub_cnt = []
    hub_level_cnt = []
    hub_done_cnt = []
    times = []

    fp = open("process-crumbs.json", 'r')
    for line in fp.readlines():
        dic = eval(line)
        times.append(dic.get('times'))
        crumbs_cnt.append(dic.get('crumbs_cnt'))
        hub_cnt.append(dic.get('hub_cnt'))
        hub_level_cnt.append(dic.get('hub_level_cnt'))
        hub_done_cnt.append(dic.get('hub_done_cnt'))
    fp.close()
    return times, crumbs_cnt, hub_cnt, hub_level_cnt, hub_done_cnt

# def showInMatPlot():
#     rule0_cnt = []
#     rule1_cnt = []
#     detail_cnt = []
#     list_cnt = []
#     list_done_cnt = []
#     times = []
#
#     fp = open("process.json", 'r')
#     for line in fp.readlines():
#         dic = eval(line)
#         times.append(dic.get('times'))
#         rule0_cnt.append(dic.get('rule0_cnt'))
#         rule1_cnt.append(dic.get('rule1_cnt'))
#         detail_cnt.append(dic.get('detail_cnt'))
#         list_cnt.append(dic.get('list_cnt'))
#         list_done_cnt.append(dic.get('list_done_cnt'))
#     fp.close()
#
#     plt.figure(1)
#     plt.title('from redis')
#     plt.xlabel('times(min)')
#     plt.ylabel('counts')
#     plt.plot(range(len(times)), rule0_cnt, "b--", label='rule0_cnt')
#     plt.plot(range(len(times)), rule1_cnt, "c--", label='rule1_cnt')
#     plt.plot(range(len(times)), detail_cnt, "g-", label='detail_cnt')
#     plt.plot(range(len(times)), list_cnt, "m-", label='list_cnt')
#     plt.plot(range(len(times)), list_done_cnt, "r-", label='list_done_cnt')
#     plt.legend(bbox_to_anchor=(0.2,1))
#     plt.show()

@app.route('/')
def show():
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = convert_file_to_list()
    times = range(len(times))
    return render_template('processShow.html',
                           times=times,
                           rule0_cnt=rule0_cnt,
                           rule1_cnt=rule1_cnt,
                           detail_cnt=detail_cnt,
                           list_cnt=list_cnt,
                           list_done_cnt=list_done_cnt)

@app.route('/crumbs')
def show_crumbs():
    times, crumbs_cnt, hub_cnt, hub_level_cnt, hub_done_cnt = convert_file_to_list_crumbs()
    times = range(len(times))
    return render_template('processShow-crumbs.html',
                           times=times,
                           crumbs_cnt=crumbs_cnt,
                           hub_cnt=hub_cnt,
                           hub_level_cnt=hub_level_cnt,
                           hub_done_cnt=hub_done_cnt)

if __name__ == '__main__':
    # times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = convert_file_to_list()
    # print times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt
    # showInMatPlot()
    app.run()
