import urllib.request
import bs4 as bs

# Create countries url's list
urls = []
source = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)').read()
soup = bs.BeautifulSoup(source, features="html.parser")
results = soup.findAll("span", {"class": "flagicon"})
for tag in results:
    url_postfix = tag.parent.find("a")['href']
    urls.append('https://en.wikipedia.org' + url_postfix)


