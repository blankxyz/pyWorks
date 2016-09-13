import time

fd = open("a.log", "a")
for i in range(30):
    time.sleep(1)
    # print 'a print ...'
    fd.write('a write...%d\n' % i)
    fd.flush()

fd.close()
