from ontology_manager.ontology_utils import OntologyManager
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import SKOS

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
    manager.load_ontology()
    
    print("fixing the emmo IRI horror\n")

    k=manager.find('perceptual')
    print(f"{k}, {len(k)} ontologies match, they are:")
    [print(i) for i in k]


    g=manager.ontology_graphs[str(k[0])]

    #onto_properties_graph=manager.ontology_graphs[str(k[0])]
    #print (type(onto_properties_graph))
    #print(onto_properties_graph.serialize())


    so_map=manager.emmo_to_label_graph("http://emmo.info/emmo", "EMMO_", SKOS.prefLabel, g ) 
    
    print(len(so_map["s_map"]), len(so_map['o_map']), len(so_map['p_map']))
  
    g2=so_map["g"]
    print (g2.serialize(format='n3'))


if __name__ == "__main__":
    main()
