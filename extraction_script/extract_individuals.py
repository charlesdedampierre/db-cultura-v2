import csv
from time import sleep
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON


def get_individuals(start_offset, batch_size):
    # Initialize SPARQL endpoint
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)

    individuals = []

    # Loop through offsets until all individuals are retrieved
    while True:
        # Construct SPARQL query
        query = """
        SELECT ?item
        WHERE {
          ?item wdt:P31 wd:Q5.
        }
        LIMIT %d
        OFFSET %d
        """ % (
            batch_size,
            start_offset,
        )

        # Set query and retrieve results
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        # Extract individual items from results
        batch_individuals = [
            result["item"]["value"] for result in results["results"]["bindings"]
        ]
        individuals.extend(batch_individuals)

        return individuals


def save_individuals_to_csv(individuals, batch_number):
    filename = f"individuals/individuals_wikidata_individuals_batch_{batch_number}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Individual"])
        for individual in individuals:
            writer.writerow([individual])


# Example usage:
batch_size = 100000
start_offset = 10700000

# total_individuals = 12000000
# batches = total_individuals // batch_size + (
#     1 if total_individuals % batch_size != 0 else 0
# )

batches = 30
for batch_number in tqdm(range(109, 139, 1)):
    individuals = get_individuals(start_offset, batch_size)
    save_individuals_to_csv(individuals, batch_number + 1)
    start_offset += batch_size
