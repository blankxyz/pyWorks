import os
import subprocess
def match_page(url):
    if os.name == 'nt':
        cmd = 'D:\phantomjs\\bin\phantomjs test.js'
    else:
        cmd = '/Users/song/workspace/phantomjs/bin/phantomjs ./test.js "%s"' % url
    stdout, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print stdout
    print stderr

if __name__ == '__main__':
    match_page('http://bbs.tianya.cn')
    # match_page('http://www.baidu.com')