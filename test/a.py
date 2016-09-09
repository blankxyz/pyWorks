import time

fd = open("a.log", "w")
while True:
    time.sleep(1)
    print 'a print ...'
    fd.write('a write...')

fd.close()