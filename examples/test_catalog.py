from ontology_manager.ontology_utils import OntologyManager

def main():
    base_path = '/Users/adham/dev/ontology/ontology/github-emmo-repo-EMMO/'
    catalog_file = 'catalog-v001.xml'

    manager = OntologyManager(base_path, catalog_file)
    manager.parse_catalog()
    # Use other methods as needed
    manager.load_ontology()
    for _, __ in manager.ontology_graphs.items():
        print(_, __)#, manager.get_last_path_segment(_))

    print(80*'-')
    print("fixing the emmo horror\n")


    manager.fix_emmo_label()

if __name__ == "__main__":
    main()
