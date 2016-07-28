import subprocess

p = subprocess.Popen(['/bin/bash', '-c', 'tail -10 ./startWeb.log'],stdout=subprocess.PIPE)
m =  p.stdout.readlines()
for msg in m:
    print msg
