SCRIPTS: 测试网页访问速度
2016年3月1日
15:57
 
#!/usr/bin/python
 
'''test access speed to the website indicated by url'''
 
 
import timeit
import urllib2
 
 
class UrlTestManager(object):
    def __init__(self, tested_url):
        self.tested_url = tested_url
 
    def url_open(self):
        return urllib2.urlopen(self.tested_url)
 
 
def main():
    setup_str = '''\
from __main__ import UrlTestManager
url_test_m = UrlTestManager(sys.argv[1])
    '''
    url_test_t = timeit.Timer('url_test_m.url_open()', setup=setup_str)
    print url_test_t.repeat(3, 1)
 
if __name__ == "__main__":
    main()
 
 
git source
============================================================
https://github.com/xiaotuanyu120/op-utility.git
