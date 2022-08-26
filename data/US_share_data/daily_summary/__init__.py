# import requests
# from bs4 import BeautifulSoup
# import pip
#
# pip.main(['install', 'urllib2'])
# import urllib
#
# import ssl
# # from requests.packages.urllib3.exceptions import InsecureRequestWarning
# #
# # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#
# ssl._create_default_https_context = ssl._create_unverified_context  # ignore ssl certificate errors
#
#
# url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
# response = urllib.request.urlopen(url)
# html_doc = response.read()
#
# # Parse the html file
# soup = BeautifulSoup(html_doc, 'html.parser')
#
# strhtm = soup.prettify()
#
# for x in soup.find_all('b'): print(x.string)
#
#
#
#
# df_list = pd.read_html(html, flavor='bs4')
