import requests
import lxml.html
import rdflib
import re

url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
wikipedia_prefix = "https://en.wikipedia.org"
example_prefix = "http://example.org/"
g = rdflib.Graph()

links_by_country = dict()


def add_triple_to_ontology(subject, predicate, object):
    stripped_object = object.replace(" ", "_")
    stripped_predicate = predicate.replace(" ", "_")
    stripped_subject = subject.replace(" ", "_")

    """
    subject_uri = rdflib.URIRef(f"{example_prefix}/{stripped_subject}")
    predicate_uri = rdflib.URIRef(f"{example_prefix}/{predicate}")
    object_uri = rdflib.URIRef(f"{stripped_object}")
    """

    g.add((rdflib.URIRef(stripped_subject), rdflib.URIRef(stripped_predicate), rdflib.URIRef(stripped_object)))


def load_countries_from_url():
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)

    for t in doc.xpath("//span[contains(@class, 'flagicon')]/..//a"):
        country = t.attrib['title']
        link = t.attrib['href']
        links_by_country[country] = wikipedia_prefix + link


def find_birth_day(person_url):
    r = requests.get(wikipedia_prefix + person_url)
    doc = lxml.html.fromstring(r.content)

    bday = ''

    for t in doc.xpath("//tr[th[text() = 'Born']]//*[contains(@class, 'bday')]/."):
        bday = t.text

    add_triple_to_ontology(example_prefix + bday, example_prefix + 'birth_date_of', wikipedia_prefix + person_url)


def find_birth_place(person_url):
    r = requests.get(wikipedia_prefix + person_url)
    doc = lxml.html.fromstring(r.content)

    birth_place = []
    birth_place_string = ''
    for t in doc.xpath("//tr[th[text() = 'Born']]/td/text()"):
        birth_place.append(t)

    for t in doc.xpath("//tr[th[text() = 'Born']]/td/a/text()"):
        birth_place.append(t)

    if birth_place:
        birth_place_string = birth_place[-1].strip('\',').lstrip(' ')

    add_triple_to_ontology(example_prefix + birth_place_string, example_prefix + 'birth_place_of', wikipedia_prefix + person_url)


def find_capital(doc, country_url):
    capital = ''

    for t in doc.xpath("//tr[th[text() = 'Capital']]/td/a[1]/text()"):
        capital += t

    for t in doc.xpath("//tr[th[text() = 'Capital']]/td/div/ul/li[1]/a/text()"):
        capital += t

    add_triple_to_ontology(example_prefix + capital, example_prefix + 'capital_of', country_url)

def find_area(doc, country_url):
    area = ''
    for t in doc.xpath("""//*[contains(text(), 'Area')]
                          //ancestor::tr[1]
                          //following-sibling::tr[1]
                          //*[sup[contains(text(), '2')]]/text()"""):
        area += t
        break

    match = re.search(r'(\d+,)*\d+(.\d)', area)
    if match:
        numerical = match.group()

    else:
        numerical = ''

    numerical += ' km squared'
    add_triple_to_ontology(example_prefix + numerical, example_prefix + 'area_of', country_url)


def find_population(doc, country_url):
    population = ''
    for t in doc.xpath("//tr[th[a[text() = 'Population']]]/following-sibling::tr[1]/td/text()[1]"):
        population += t

    stripped = population.replace(".", ",")
    match = re.search(r'(\d+,)*\d+', stripped)
    if match:
        numerical = match.group()
    else:
        numerical = ''
    add_triple_to_ontology(example_prefix + numerical, example_prefix + 'population_of', country_url)


def find_govern_method(doc, country_url):
    for t in doc.xpath("//tr[th[a[text() = 'Government']]]/td/a"):
        method = t.attrib['title']
        add_triple_to_ontology(example_prefix + method, example_prefix + 'form_of_government_in', country_url)

    for t in doc.xpath("//tr[th[a[text() = 'Government']]]/td/span/a"):
        method = t.attrib['title']
        add_triple_to_ontology(example_prefix + method, example_prefix + 'form_of_government_in', country_url)

    for t in doc.xpath("//tr[th[text() = 'Government']]/td/a"):
        method = t.attrib['title']
        add_triple_to_ontology(example_prefix + method, example_prefix + 'form_of_government_in', country_url)



def find_president(doc, country_url):
    president = ''
    president_link = ''
    for t in doc.xpath("//tr[th[div[a[text() = 'President']]]]/td//a[1]"):
        president = t.text
        president_link = t.attrib['href']

    add_triple_to_ontology(wikipedia_prefix + president_link, example_prefix + 'president_of', country_url)

    if president != '':
        find_birth_day(president_link)
        find_birth_place(president_link)


def find_prime_minister(doc, country_url):
    prime_minister = ''
    prime_minister_link = ''

    for t in doc.xpath("//tr[th[div[a[text() = 'Prime Minister']]]]/td//a[1]"):
        prime_minister = t.text
        prime_minister_link = t.attrib['href']

    add_triple_to_ontology(wikipedia_prefix + prime_minister_link, example_prefix + 'prime_minister_of', country_url)

    if prime_minister != '':
        find_birth_day(prime_minister_link)
        find_birth_place(prime_minister_link)


def find_information_of_country_by_link(country, country_url):
    print(country)
    r = requests.get(country_url)
    doc = lxml.html.fromstring(r.content)

    # Find capital of given country
    find_capital(doc, country_url)

    # Find area of given country
    find_area(doc, country_url)

    # Find population of given country
    find_population(doc, country_url)

    # Find govern method of given country
    find_govern_method(doc, country_url)

    # Find president method of given country
    find_president(doc, country_url)

    # Find president method of given country
    find_prime_minister(doc, country_url)


def iterate_countries():
    for i, country in enumerate(links_by_country):
        url = links_by_country[country]
        find_information_of_country_by_link(country, url)



def create_ontology():    # Load all countries names into the list
    #load_countries_from_url()
    iterate_countries()
    find_information_of_country_by_link('Indonesia', 'https://en.wikipedia.org/wiki/Indonesia')
    g.serialize("./ontology.nt", format="nt")
    #g.serialize("./ontology_test.nt", format="nt")
