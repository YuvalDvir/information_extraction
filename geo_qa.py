import ontology
import rdflib
import re
import csv
from termcolor import colored
import enum
import sys

from ontology import links_by_country

wikipedia_prefix = "https://en.wikipedia.org/wiki"
example_prefix = "http://example.org"


class QueryType(enum.Enum):
    regular = 0
    who_is = 1

def tester():
    questions = []
    answers = []
    success = 0
    fails = 0
    file = open('qa _27.4.csv')
    csvreader = csv.reader(file)
    rows = []
    for i, row in enumerate(csvreader):
        if i == 0:
            continue
        questions.append(row[0])
        answers.append(row[1])


    g2 = rdflib.Graph()
    g2.parse('ontology.nt', format='nt')
    #question = 'What is the form of government in Sweden?'

    for i, question in enumerate(questions):
        quer, query_type = create_query(question)
        if not quer:
            continue
        query_result = g2.query(quer)
        ans = decode_query_result(list(query_result), query_type)
        if ans == answers[i]:
            print('[', colored('success', 'green'), '] ', question, colored('got: ', 'magenta'), "\'" + ans + "\'", colored('expected: ', 'magenta'), "\'" + answers[i] + "\'")
            success += 1
        else:
            print('[', colored('fail', 'red'), '] ', question, colored('got: ', 'magenta'), "\'" + ans + "\'", colored('expected: ', 'magenta'), "\'" + answers[i] + "\'")
            fails += 1
    print('\n')
    print("Total:")
    print(colored('%d', 'green') % success, '/' ,colored('%d', 'red') % fails)


def create_query(input):
    query = None
    query_type = QueryType.regular

    # What is the <form of government in> <country>?
    if re.search('What is the form of government in (\w+)?', input):
        predicate = example_prefix + '/' + 'form_of_government_in'
        country = wikipedia_prefix + '/' + re.search('What is the form of government in (.*)\?', input).group(1).replace(" ", "_")

        query = """
        SELECT *
        WHERE
        {
            ?a <%s> <%s> .
        }
        """ % (predicate, country)

    # What is the <area\population\capital> of <country>?
    elif re.search('What is the (.*?) \w+\?', input):
        predicate = example_prefix + '/' + re.search('What is the (\w+) of (.*?)\?', input).group(1).replace(" ", "_") + '_of'
        country = wikipedia_prefix + '/' + re.search('of (.*)\?', input).group(1).replace(" ", "_")

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
            country = wikipedia_prefix + '/' + re.search(' (\w+)\?', input).group(1).replace(" ", "_")

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
            SELECT ?a ?b
            WHERE
            {
                <%s> ?a ?b .
            }
            """ % subject
            query_type = QueryType.who_is

    elif re.search('When was the (.*?) \w+ born\?', input):
        predicate1 = example_prefix + '/' + re.search('When was the (.*) of (.*) born\?', input).group(1).replace(" ", "_") + '_of'
        predicate2 = example_prefix + '/' + 'birth_date_of'
        country = wikipedia_prefix + '/' + re.search('of (.*) born\?', input).group(1).replace(" ", "_")

        query = """
        SELECT ?b
        WHERE
        {
            ?a <%s> <%s> .
            ?b <%s> ?a
        }
        """ % (predicate1, country, predicate2)

    elif re.search('Where was the (.*?) \w+ born\?', input):
        predicate1 = example_prefix + '/' + re.search('Where was the (.*) of (.*) born\?', input).group(1).replace(" ", "_") + '_of'
        predicate2 = example_prefix + '/' + 'birth_place_of'
        country = wikipedia_prefix + '/' + re.search('of (.*) born\?', input).group(1).replace(" ", "_")

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
                filter contains(lcase(str(?a)), '%s')
            }
            """ % ('http://example.org/capital_of', string)

    elif re.search('How many (.*) are also', input):
        form1 = re.search('How many (.*) are', input).group(1).replace(" ", "_")
        form2 = re.search('also (.*)\?', input).group(1).replace(" ", "_")
        form_predicate = 'http://example.org/form_of_government_in'

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

    elif re.search('How many (.*) were born in', input):
        temp = re.search('How many (.*) were', input).group(1).replace(" ", "_")
        birth_place = re.search('born in (.*)\?', input).group(1).replace(" ", "_")

        if temp == 'presidents':
            predicate = 'president_of'
        elif temp == 'prime_ministers':
            predicate = 'prime_minister_of'


        query = """
            SELECT (COUNT (?a) AS ?count)
            WHERE
            {
                ?a <%s> ?b .
                <%s> <http://example.org/birth_place_of> ?a .
            }
            """ % (example_prefix + '/' + predicate, example_prefix + '/' + birth_place)

    return query, query_type

def decode_query_result(query_results, query_type):
    results = []
    result = ''

    if query_type == QueryType.who_is:
        result = query_results[0][0][query_results[0][0].rfind('/') + 1 :].replace('_', ' ').capitalize() + ' ' + \
                 query_results[0][1][query_results[0][1].rfind('/') + 1 :].replace('_', ' ')

    elif query_type == QueryType.regular:
        for i in range(len(query_results)):
            results.append((query_results[i][0][query_results[i][0].rfind('/') + 1:]).replace('_', ' '))

        sorted_list = sorted(results, key=lambda s: s.lower())

        for i in range(len(sorted_list)):
            result += sorted_list[i]
            if i < len(sorted_list) - 1:
                result += ', '

    return result.rstrip()

def ask_question(question):
    g2 = rdflib.Graph()
    g2.parse('ontology.nt', format='nt')


    quer, query_type = create_query(question)
    query_result = g2.query(quer)
    ans = decode_query_result(list(query_result), query_type)
    print(ans)

def test_question(question):
    g2 = rdflib.Graph()
    g2.parse('ontology.nt', format='nt')

    print("---------------------------------------------------------------------")
    print("question: ", question)
    print("---------------------------------------------------------------------")
    quer, query_type = create_query(question)
    query_result = g2.query(quer)
    ans = decode_query_result(list(query_result), query_type)
    print("answer:", "\'" + ans + "\'")
    print("---------------------------------------------------------------------")
    print("\n")
    print("---------------------------------------------------------------------")
    print(quer)

if __name__ == "__main__":


    list_of_arguments = sys.argv

    if len(list_of_arguments) < 2:
        print("invalid args")
        exit()

    if list_of_arguments[1] == 'create':
        ontology.create_ontology()

    if list_of_arguments[1] == 'test_question':
        test_question(list_of_arguments[2])

    if list_of_arguments[1] == 'question':
        ask_question(list_of_arguments[2])

    if list_of_arguments[1] == 'test':
        tester()




