# -*- coding: utf-8 -*-

import os
import shutil
import unicodedata
import webbrowser
import re

import requests
from wox import Wox,WoxAPI
from bs4 import BeautifulSoup

ROOT_URL = 'http://weekly.manong.io/'
ISSUE_URL = 'http://weekly.manong.io/issues/'

def full2half(uc):
    """Convert full-width characters to half-width characters.
    """
    return unicodedata.normalize('NFKC', uc)


class Main(Wox):

    def request(self,url):
	#get system proxy if exists
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
	    proxies = {
		"http":"http://{}:{}".format(self.proxy.get("server"),self.proxy.get("port")),
		"https":"http://{}:{}".format(self.proxy.get("server"),self.proxy.get("port"))
	    }
	    return requests.get(url,proxies = proxies)
	return requests.get(url)

    def getLastestIssue(self,url):

        r = self.request(url)
        r.encoding = 'utf-8'
        bs = BeautifulSoup(r.content, 'html.parser')

        return bs.find('div', class_='menu').find('a')['href']

    def query(self, param):
        url = self.getLastestIssue(ROOT_URL)
        if re.match('^\d+$', param.strip()):
            url = ISSUE_URL + param.strip()

	r = self.request(url)
	r.encoding = 'utf-8'
	bs = BeautifulSoup(r.content, 'html.parser')
	posts = bs.select('h4')

	result = []
	for p in posts:
            ptitle = p.find('a').string
            plink = p.find('a')['href']
            user = p.find('small')
            psubtitle = p.next_sibling.next_sibling.string
            item = {
                'Title': u'{subject} by {user}'.format(subject=full2half(ptitle), user=user.string if user else ""),
                'SubTitle': psubtitle if psubtitle else "enter to open",
                'IcoPath': os.path.join('img', 'manong.png'),
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': [plink]
                }
            }
            result.append(item)

	return result

    def open_url(self, url):
	webbrowser.open(url)

if __name__ == '__main__':
    Main()
