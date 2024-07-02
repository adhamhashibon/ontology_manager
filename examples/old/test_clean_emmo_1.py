from ontology_manager.ontology_utils import OntologyManager
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import SKOS


from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt


"""

"""
def main():
    base_path = '/Users/adham/dev/ontology/ontology/github-emmo-repo-EMMO/'
    catalog_file = 'catalog-v001.xml'

    manager = OntologyManager(base_path, catalog_file)
    manager.parse_catalog()
    manager.load_ontology()

    print("fixing the emmo IRI horror\n")

    manager.replace_iri()

    for k, v in manager.ontology_graphs.items():
        print(v.serialize())
        #G = rdflib_to_networkx_multidigraph(v)
        #nt = Network('500px', '1000px', notebook=True)
        ## populates the nodes and edges data structures
        #nt.from_nx(G)
        #nt.show('nx.html')
if __name__ == "__main__":
    main()
