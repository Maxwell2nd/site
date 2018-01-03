import lxml.html
from urllib.request import urlopen
import sys,requests

def check():
<<<<<<< HEAD
	data = requests.get('https://www.youtube.com/results?search_query=pumped+up+kicks').content
	return data.decode('utf-8', 'ignore');

doc = lxml.html.document_fromstring(check())
print (doc)
=======
	data = requests.get('https://www.youtube.com/results?search_query=pumped+up+kicks')
	return data.decode('utf-8', 'ignore');

doc = lxml.html.document_fromstring(check())
>>>>>>> bf119b970a764af3c481905a57bcd9fdf245cd59
el = doc.xpath('//a[@class="yt-uix-tile-link"]')
print(el)
