import lxml.html
from urllib.request import urlopen
import sys,requests

def check():
	data = requests.get('https://www.youtube.com/results?search_query=pumped+up+kicks')
	return data.decode('utf-8', 'ignore');

doc = lxml.html.document_fromstring(check())
el = doc.xpath('//a[@class="yt-uix-tile-link"]')
print(el)
