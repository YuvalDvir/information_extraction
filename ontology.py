import requests
import lxml.html


url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
wikipedia_prefix = "https://en.wikipedia.org/"

links_by_country = dict()
capital_by_country = dict()
area_by_country = dict()
population_by_country = dict()
govern_method_by_country = dict()

def load_countries_from_url():
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)
    for t in doc.xpath("//span[contains(@class, 'flagicon')]/..//a"):
        country = t.attrib['title']
        link = t.attrib['href']
        links_by_country[country] = wikipedia_prefix + link


def find_information_of_country_by_link(country, url):
    print(country)
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)

    # Find capital of given country
    for t in doc.xpath("//tr[th[text() = 'Capital']]/td/a/text()"):
        capital = t
        capital_by_country[country] = capital
        print(capital)

    # Find area of given country
    for t in doc.xpath("//tr[th[a[text() = 'Area ']]]/following-sibling::tr[1]/td/text()[1]"):
        area = t
        area_by_country[country] = area
        print(area)

    # Find population of given country
    for t in doc.xpath("//tr[th[a[text() = 'Population']]]/following-sibling::tr[1]/td/text()[1]"):
        population = t
        population_by_country[country] = population
        print(population)

    # Find govern method of given country
    method = ''
    for t in doc.xpath("//tr[th[a[text() = 'Government']]]/td/a"):
        method += t.text + ", "

    govern_method_by_country[country] = method.rstrip(", ")
    print(govern_method_by_country[country])

    print('')


def iterate_countries():
    for country in links_by_country:
        url = links_by_country[country]
        find_information_of_country_by_link(country, url)


if __name__ == "__main__":
    # Load all countries names into the list
    load_countries_from_url()
    iterate_countries()
