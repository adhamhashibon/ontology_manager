from ontology_manager.ontology_utils import OntologyManager
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import SKOS, OWL, FOAF

"""
"""
def main():
    base_path = '/Users/adham/dev/ontology/ontology/github-emmo-repo-EMMO/'
    catalog_file = 'catalog-v001.xml'

    manager = OntologyManager(base_path, catalog_file)
    manager.parse_catalog()
    manager.load_ontology()
    
    print("find all elucidations\n")

    for k, g in manager.ontology_graphs.items():
        #print(g.serialize())
        for s, p, o in g.triples( (None, None, OWL['AnnotationProperty']) ):
            print(f"{s} {p} {o}")
        for s, p, o in g:
            if isinstance(o, Literal):
                print(s, p, o)
if __name__ == "__main__":
    main()


