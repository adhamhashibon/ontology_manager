from ontology_manager.ontology_utils import OntologyManager
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import SKOS

"""

"""
def main():
    base_path = '/Users/adham/dev/ontology/ontology/github-emmo-repo-EMMO/'
    catalog_file = 'catalog-v001.xml'

    manager = OntologyManager(base_path, catalog_file)
    manager.parse_catalog()
    manager.load_ontology()

    print("fixing the emmo IRI horror\n")

    manager.replace_iri2()

    for k, v in manager.ontology_graphs.items():
        print(v.serialize())

if __name__ == "__main__":
    main()
