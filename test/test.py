import subprocess

SHELL_DETAIL_CMD = 'a.bat'

# fd = open("test.log", "w")
# returncode = subprocess.call('python a.py')
p = subprocess.Popen(['python','a.py'],stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
process_id = p.pid
print 'process_id:',process_id
# print p.stdout.read()
# fd.write(p.stdout.read())
# fd.close()
# print returncode

# for _ in range(10):
print 'end....'