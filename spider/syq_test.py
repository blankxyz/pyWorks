import requests
import htmlparser

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
           'Connection': 'keep-alive',
           'Cookie': 'PREF=f1=1222&cvdm=list',
           'Host': 'www.youtube.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
           }

resp = requests.get('https://www.youtube.com/results?sp=CAISAggC&q=china',
                    proxies=dict(http='socks5://127.0.0.1:1080',
                                 https='socks5://127.0.0.1:1080'),
                    headers=headers)

data = htmlparser.Parser(resp.content)
cnt_str = data.xpath('''//p[contains(@class,"num-results")]''')

print cnt_str.text()
