import rdflib
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS
import random

# Define namespaces
domeES = rdflib.Namespace("http://dome40.eu/semantics/dome4.0_core#")
mio = rdflib.Namespace("http://www.ddmd.io/mio/")

# Create a Graph
g = rdflib.Graph()

# Add ontology prefixes to the graph
g.bind('domeES', domeES)
g.bind('mio', mio)
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)

# Define the number of data sets to generate
num_data_sets = 10

# Generate data sets and associated data
for i in range(1, num_data_sets + 1):

    data_set_uri = URIRef(f"http://example.com/dataset/{i}")
    data_uri = URIRef(f"http://example.com/data/{i}")

    # Add data set type
    g.add((data_set_uri, RDF.type, domeES.data_set))

    # Add random data set properties
    g.add((data_set_uri, domeES.type, Literal("Type" + str(i))))
    g.add((data_set_uri, domeES.platform_type, Literal("PlatformType" + str(i))))
    g.add((data_set_uri, domeES.label, Literal("Label" + str(i))))
    g.add((data_set_uri, domeES.comment, Literal("Comment" + str(i))))

    # Add hasPart relationship between DataSet and Data with specific value
    g.add((data_set_uri, domeES.hasPart, data_uri))
    g.add((data_uri, RDF.type, domeES.data))

    # Add random values for each property
    g.add((data_uri, domeES.hasValue, Literal(random.uniform(0.0, 10.0))))  # Adjust the range as needed
    g.add((data_set_uri, mio.hasPart, domeES.web_platform))
    g.add((data_set_uri, mio.hasPart, domeES.issued_date))
    g.add((data_set_uri, mio.hasPart, domeES.data_creator))
    g.add((data_set_uri, mio.hasPart, domeES.description))
    g.add((data_set_uri, mio.hasPart, domeES.license))
    g.add((data_set_uri, mio.hasPart, domeES.data_publisher))
    g.add((data_set_uri, mio.hasPart, domeES.title))
    g.add((data_set_uri, mio.hasPart, domeES.semantic_keyword))
    g.add((data_set_uri, mio.hasPart, domeES.syntactic_keyword))

# Serialize the graph to a TTL file
g.serialize(destination='output.ttl', format='turtle')

#
# from vv.data import add_ontology
# # Example usage:
# cuds_file_path = "output.ttl"
# ontology_file_path = "Ontology-matters/dome4.0_core_tbox.ttl"
# output_file_path = "output_2.ttl"
# result = add_ontology(cuds_file_path, ontology_file_path, output_file_path)

from data import upload_to_dataset, create_fuseki_dataset

fuseki = "http://localhost:3030"
dataset_name = "dome40"  # Replace with the name of your existing dataset
ttl_file_path = "output.ttl"
create_database = create_fuseki_dataset(fuseki, dataset_name)
add_data = upload_to_dataset(fuseki, dataset_name, ttl_file_path)

from ontodot.ontodot import OntoVis
from ontodot.ontodot import vis
from ontology_manager.ontology_utils import OntologyManager



base_path = './'
catalog_file = 'catalog-v001.xml'
#%%
mio_manager = OntologyManager(base_path, catalog_file)
mio_manager.parse_catalog()
mio_manager.load_ontology()
#%%
# there is one graph, we also know the name space,
g=mio_manager.ontology_graphs[domeES]
#%%
# plot, and check the OntoVis.Output folder for all images and dot files.
vis(g, max_string_length=5)



from rdflib import Graph, URIRef

# Load the RDF graph from the TTL file
g = Graph()
g.parse('output.ttl', format='turtle')

# Define the SPARQL query
query_str = """
    PREFIX domeES: <http://dome40.eu/semantics/dome4.0_core#>
    SELECT ?dataset ?value
    WHERE {
        ?dataset domeES:hasPart ?data .
        ?data domeES:hasValue ?value .
    }
"""

# Execute the query
results = g.query(query_str)

# Print the results
for row in results:
    dataset, value = row
    print(f"Dataset: {dataset}, Value: {value}")