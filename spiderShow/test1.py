import os

p = os.popen("find ./ -name '*.py'")
print p.read()
