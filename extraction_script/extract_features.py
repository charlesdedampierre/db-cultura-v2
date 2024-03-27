import csv
from time import sleep
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from multiprocessing import Pool


endpoint_url = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(endpoint_url)


def extract_values(data):
    """
    Extracts only the values from the given dictionary.

    Args:
        data (dict): Dictionary containing Wikidata information.

    Returns:
        dict: Dictionary containing only the values.
    """
    extracted_data = {}
    for key, value in data.items():
        if isinstance(value, dict) and "value" in value:
            extracted_data[key] = value["value"]
    return extracted_data


def extract_info(wiki_id):
    # Set query and retrieve results
    sparql.setQuery(get_metadata(wiki_id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results = results["results"]["bindings"]
    # results = [
    #         result["item"]["value"] for result in results["results"]["bindings"]
    #     ]

    results = [extract_values(result) for result in results]

    return results


def get_metadata(wiki_id):
    # Construct SPARQL query for the given batch of individuals
    sparql_query = """
    SELECT ?subject ?subjectLabel 
        ?occupation ?occupationLabel 
        ?dateOfBirth ?dateOfDeath 
        ?gender ?genderLabel 
        ?countryOfBirth ?countryOfBirthLabel 
        ?countryOfDeath ?countryOfDeathLabel 
        ?countryOfCitizenship ?countryOfCitizenshipLabel 
        ?birthCity ?birthCityLabel 
        ?deathCity ?deathCityLabel 
        ?birthCityPlace ?birthCityPlaceLabel 
        ?deathCityPlace ?deathCityPlaceLabel 
    WHERE {
    BIND(wd:%s AS ?subject)
    
    OPTIONAL { ?subject wdt:P106 ?occupation. }
    OPTIONAL { ?subject wdt:P569 ?dateOfBirth. }
    OPTIONAL { ?subject wdt:P570 ?dateOfDeath. }
    OPTIONAL { ?subject wdt:P21 ?gender. }
    OPTIONAL { ?subject wdt:P19 ?countryOfBirth. }
    OPTIONAL { ?subject wdt:P20 ?countryOfDeath. }
    OPTIONAL { ?subject wdt:P27 ?countryOfCitizenship. }
    OPTIONAL { ?subject wdt:P19 ?birthCity. }
    OPTIONAL { ?subject wdt:P20 ?deathCity. }
    OPTIONAL { ?subject wdt:P19 ?birthCityPlace. }
    OPTIONAL { ?subject wdt:P20 ?deathCityPlace. }
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }
    }
    """ % (
        wiki_id
    )

    return sparql_query


if __name__ == "__main__":

    chunk = ["Q859", "Q859"]

    with Pool(8) as p:
        results = list(tqdm(p.imap(extract_info, chunk), total=len(chunk)))

    with open(f"../raw_data/individuals_metadata/results_test.json", "w") as f:
        json.dump(results, f)
