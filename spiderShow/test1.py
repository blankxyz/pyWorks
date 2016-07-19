import os,time
import subprocess
# cmd = os.popen('''which op xdg-open exo-open gnome-open kfmclient open | head -n1 |  sed "s/$/ '%s' /&/; s/kfmclient/kfmclient exec/"''').read()
print subprocess.Popen(['/bin/sh','-c' ,'./test.sh'])

print os.system('ps -a')
