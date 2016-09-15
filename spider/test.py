import subprocess
def match_page(url):
    cmd = '/Users/song/workspace/phantomjs/bin/phantomjs ./test.js "%s"' % url
    stdout, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print stdout
    print stderr

if __name__ == '__main__':
    match_page('http://bbs.tianya.cn')