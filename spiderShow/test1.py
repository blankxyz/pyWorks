# import os,time
#
# if os.name=='posix':
#     cmd = os.popen('''which op xdg-open exo-open gnome-open kfmclient open | head -n1 |  sed "s/$/ '%s' /&/; s/kfmclient/kfmclient exec/"''').read()
# elif os.name=='nt':
#     os.startfile(r"D:\workspace\pyWorks\spiderShow\test.py")
import re

def modify(pyfile, start_urls , site_domain):
    try:
        lines = open(pyfile, 'r').readlines()
        # print type(lines)
        i = 0
        for line in lines:
            s = line.strip()
            i += 1
            if s !='' and s[0] == '#':
                continue
            else:
                if i<100 and re.search(r'self\.start_urls\s*?=',s):
                    lines[i-1] = line[:line.find('=')+1] + ' ' + start_urls + '\n'
                    print lines[i-1]

                if i < 100 and re.search(r'self\.site_domain\s*?=', s):
                    lines[i - 1] = line[:line.find('=') + 1] + ' ' + site_domain + '\n'
                    print lines[i - 1]

        open(pyfile, 'w').writelines(lines)

    except Exception, e:
        print e

if __name__ == '__main__':
    modify('test.py', start_urls = '\'http://www.k618.cn\'', site_domain='\'k618.cn\'')