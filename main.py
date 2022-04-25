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

    elif re.search('List all countries whose capital name contains the string \w+', input):
        string = re.search('the string (\w+)', input).group(1)

        query = """
            SELECT ?b
            WHERE
            {
                ?a <%s> ?b .
                filter contains(str(?a), '%s')
            }
            """ % ('http://example.org/capital_of', string)

    elif re.search('How many (.*) are also', input):
        form1 = re.search('How many (.*) are', input).group(1).replace(" ", "_")
        form2 = re.search('also (.*)\?', input).group(1).replace(" ", "_")
        form_predicate = 'http://example.org/form_of_government_in'

        print(form1, form2)
        query = """
            SELECT (COUNT (*) AS ?count)
            WHERE
            {
                ?a1 <%s> ?b .
                ?a2 <%s> ?b .
                filter contains(str(?a1), '%s')
                filter contains(str(?a2), '%s')
            }
            """ % (form_predicate, form_predicate, form1, form2)
    return query


if __name__ == "__main__":
    #ontology.create_ontology()

    """
    """
    g2 = rdflib.Graph()
    g2.parse('ontology.nt', format='nt')

    quer = create_query("How many dictatorship are also Presidential?")
    print(quer)


    qres = g2.query(quer)
    print(list(qres))
