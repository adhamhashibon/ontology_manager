from ontology_manager.ontology_utils import OntologyManager
from rdflib import Graph, URIRef, Namespace, Literal, BNode

"""
create and adapt for unit teting 
basically we need: 

a simple ontology for testing in the local folder, 

it should have various forms of the ontology URI with :, / and # 

it should have specific relations covering all possible relations

we check i each ontology is loaded properly 


we also later export the ontology and compare the files 

we then alter the ontology with individual and with a new class and check that it existisna comparing to the expected result 

"""
def main():
    base_path = '/Users/adham/dev/ontology/ontology/github-emmo-repo-EMMO/'
    catalog_file = 'catalog-v001.xml'

    manager = OntologyManager(base_path, catalog_file)
    manager.parse_catalog()
    # Use other methods as needed
    manager.load_ontology()
    #for _, __ in manager.ontology_graphs.items():
    #    print(_, __)#, manager.get_last_path_segment(_))

    #print(80*'-')
    uri=URIRef("http://emmo.info/emmo#EMMO_9be5fcc4_0d8b_481d_b984_6338d4b55588")
    
    parsed = manager.parse_uri(uri)

    print ("uri=", uri)
    print ("parsed_uri=", parsed)
if __name__ == "__main__":
    main()
