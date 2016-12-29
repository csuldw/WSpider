# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import string
import socket
import random
import myconf
socket.setdefaulttimeout(3)

def fetch_xici(proxies=[]):
    header = {}
    page = 1
    url_prefix = "http://www.xicidaili.com/wt/"
    try:
        while page <= 1:
            url = url_prefix + str(page)
            header['User-Agent'] = random.choice(myconf.agent_list)
            req = urllib2.Request(url, headers=header)
            res = urllib2.urlopen(req).read()
            soup = BeautifulSoup(res, "html.parser")
            ips = soup.findAll('tr')
            for x in range(1, len(ips)):
                ip = ips[x]
                tds = ip.findAll("td")
                if(len(tds) == 10):
                    ip = tds[1].contents[0].strip().replace("\r\n","")
                    port = tds[2].contents[0].strip().replace("\r\n","")
                    proxy_type =  string.lower(tds[5].contents[0].strip().replace("\r\n","")).strip()
                    if proxy_type == "http":
                        proxy = "http://" + ip + ":" + port
                        proxies.append(proxy)
            page += 1
    except Exception, e:
        print "Something is Wrong!", e
    return proxies

def fetch_ip181(proxyes=[]):
    header = {}
    try:
        url = "http://www.ip181.com/"
        header['User-Agent'] = random.choice(myconf.agent_list)
        req = urllib2.Request(url, headers=header)
        res = urllib2.urlopen(req).read()
        soup = soup = BeautifulSoup(res, "html.parser")
        table = soup.find("table")
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tds = trs[i].find_all("td")
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text[:-2]
            if float(latency) < 1:
                proxyes.append("%s://%s:%s" % ("http", ip, port))
    except Exception as e:
        print "fail to fetch from ip181: %s" % e
    return proxyes

def img2port(img_url):
    code = img_url.split("=")[-1]
    if code.find("AO0OO0O")>0:
        return 80
    else:
        return None

def fetch_mimvp(proxies=[]):
    header = {}
    try:
        url = "http://proxy.mimvp.com/free.php?proxy=in_hp&sort=&page=1"
        header['User-Agent'] = random.choice(myconf.agent_list)
        req = urllib2.Request(url, headers=header)
        res = urllib2.urlopen(req).read()
        soup = soup = BeautifulSoup(res, "html.parser")
        table = soup.find("div", attrs={"id": "list"}).table
        tds = table.tbody.find_all("td")
        for i in range(0, len(tds), 10):
            ip = tds[i+1].text
            port = img2port(tds[i+2].img["src"])
            response_time = tds[i+7]["title"][:-1]
            if port is not None and float(response_time) < 1 :
                proxy = "%s://%s:%s" % ("http", ip, port)
                proxies.append(proxy)
    except Exception, e:
        print "fail to fetch from mimvp", e
    return proxies


def proxy_validate(proxies, outfile):
    print "proxies size is: ", len(proxies)
    f2 = open(outfile, "w")
    f2.write("http://127.0.0.1:8087\n")
    test_url = "http://ip.chinaz.com/getip.aspx"
    header = {}
    proxy_pool = []
    for proxy in proxies:
        try:
            proxy_support = urllib2.ProxyHandler({"http": proxy}) 
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            header['User-Agent'] = random.choice(myconf.agent_list)
            req = urllib2.Request(test_url, headers=header)
            res = urllib2.urlopen(req).read()
            print proxy, res
            proxy_pool.write(proxy)
            f2.write(proxy + "\n")
        except Exception,e:
            print e
    f2.close()
    return proxy_pool

if __name__ == "__main__":
    proxies = fetch_mimvp()
    fetch_xici(proxies)
    fetch_ip181(proxies)
    outfile="proxy.data"
    proxy_validate(proxies, outfile)
