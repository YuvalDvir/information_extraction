import ontology
import rdflib
import re
from ontology import links_by_country

wikipedia_prefix = "https://en.wikipedia.org/wiki"
example_prefix = "http://example.org"

def create_query(input):
    print(input)
    query = None

    # What is the <predicate> of <country>?
    if re.search('What is the (.*?) \w+\?', input):
        predicate = example_prefix + '/' + re.search('What is the (.*) \w+\?', input).group(1).replace(" ", "_")
        country = wikipedia_prefix + '/' + re.search('(\w+)\?', input).group(1).replace(" ", "_")

        query = """
        SELECT *
        WHERE
        {
            ?a <%s> <%s> .
        }
        """ % (predicate, country)

    # Who is the prime minister of <country>?
    elif re.search('Who is (.*?)\?', input):
        if re.search('Who is the (.*?) \w+\?', input):
            predicate = example_prefix + '/' + re.search('Who is the (.*) \w+\?', input).group(1).replace(" ", "_")
            print(predicate)
            country = wikipedia_prefix + '/' + re.search(' (\w+)\?', input).group(1).replace(" ", "_")
            print(country)
            query = """
            SELECT *
            WHERE
            {
                ?a <%s> <%s> .
            }
            """ % (predicate, country)

        else:
            subject = wikipedia_prefix + '/' + re.search('Who is (.*)\?', input).group(1).replace(" ", "_")

            query = """
            SELECT *
            WHERE
            {
                ?a ?b <%s> .
            }
            """ % subject

    elif re.search('When was the (.*?) \w+ born\?', input):
        predicate1 = example_prefix + '/' + re.search('When was the (.*) \w+ born\?', input).group(1).replace(" ", "_")
        predicate2 = example_prefix + '/' + 'birth_date_of'
        country = wikipedia_prefix + '/' + re.search(' (\w+) born\?', input).group(1).replace(" ", "_")

        query = """
        SELECT ?b
        WHERE
        {
            ?a <%s> <%s> .
            ?b <%s> ?a
        }
        """ % (predicate1, country, predicate2)

    elif re.search('Where was the (.*?) \w+ born\?', input):
        predicate1 = example_prefix + '/' + re.search('Where was the (.*) \w+ born\?', input).group(1).replace(" ", "_")
        predicate2 = example_prefix + '/' + 'birth_place_of'
        country = wikipedia_prefix + '/' + re.search(' (\w+) born\?', input).group(1).replace(" ", "_")

        query = """
            SELECT ?b
            WHERE
            {
                ?a <%s> <%s> .
                ?b <%s> ?a
            }
            """ % (predicate1, country, predicate2)



    return query


if __name__ == "__main__":
    #ontology.create_ontology()

    g2 = rdflib.Graph()
    g2.parse('ontology.nt', format='nt')

    quer = create_query("Where was the president of China born?")
    print(quer)


    qres = g2.query(quer)
    print(list(qres))
