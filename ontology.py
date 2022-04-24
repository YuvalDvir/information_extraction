import requests
import lxml.html
import rdflib

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
wikipedia_prefix = "https://en.wikipedia.org/"
example_prefix = "http://example.org"
g = rdflib.Graph()

links_by_country = dict()
capital_by_country = dict()
area_by_country = dict()
population_by_country = dict()
govern_method_by_country = dict()
president_by_country = dict()
prime_minister_by_country = dict()
birth_date_by_name = dict()
birth_place_by_name = dict()

def add_triple_to_ontology(subject, predicate, object):
    subject_uri = rdflib.URIRef(f"{example_prefix}/{subject}")
    predicate_uri = rdflib.URIRef(f"{example_prefix}/{predicate}")
    object_uri = rdflib.URIRef(f"{example_prefix}/{object}")

    g.add((subject_uri, predicate_uri, object_uri))


def load_countries_from_url():
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)
    for t in doc.xpath("//span[contains(@class, 'flagicon')]/..//a"):
        country = t.attrib['title']
        link = t.attrib['href']
        links_by_country[country] = wikipedia_prefix + link


def find_birth_day(name, url):
    r = requests.get(wikipedia_prefix + url)
    doc = lxml.html.fromstring(r.content)

    bday = ''

    for t in doc.xpath("//tr[th[text() = 'Born']]//*[contains(@class, 'bday')]/."):
        bday = t.text

    birth_date_by_name[name] = bday


def find_birth_place(name, url):
    r = requests.get(wikipedia_prefix + url)
    doc = lxml.html.fromstring(r.content)

    birth_place = ''

    for t in doc.xpath("//tr[th[text() = 'Born']]//a"):
        birth_place += t.text + ", "

    birth_place_by_name[name] = birth_place.rstrip(", ")


def find_information_of_country_by_link(country, url):
    print(country)
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)

    # Find capital of given country
    capital = ''
    for t in doc.xpath("//tr[th[text() = 'Capital']]/td/a/text()"):
        capital += t
        capital_by_country[country] = capital
        print(capital)

    add_triple_to_ontology(capital, 'capital_of', country)

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

    # Find president method of given country
    president = ''
    for t in doc.xpath("//tr[th[div[a[text() = 'President']]]]/td//a"):
        president = t.text
        president_link = t.attrib['href']

        find_birth_day(president, president_link)
        find_birth_place(president, president_link)

    if president is not '':
        print("president: ")
        print("\t", president)
        print("\t", birth_date_by_name[president])
        print("\t", birth_place_by_name[president])

    # Find prime minister method of given country
    prime_minister = ''
    for t in doc.xpath("//tr[th[div[a[text() = 'Prime Minister']]]]/td//a"):
        prime_minister = t.text
        prime_minister_link = t.attrib['href']

        find_birth_day(prime_minister, prime_minister_link)
        find_birth_place(prime_minister, prime_minister_link)
    if prime_minister is not '':
        print("prime minister: ")
        print("\t", prime_minister)
        print("\t", birth_date_by_name[prime_minister])
        print("\t", birth_place_by_name[prime_minister])




    print('')

def iterate_countries():
    for country in links_by_country:
        url = links_by_country[country]
        find_information_of_country_by_link(country, url)


if __name__ == "__main__":
    # Load all countries names into the list
    load_countries_from_url()
    iterate_countries()
    #find_information_of_country_by_link('Portugal', 'https://en.wikipedia.org/wiki/Portugal')
    g.serialize("./ontology.nt", format="nt")
