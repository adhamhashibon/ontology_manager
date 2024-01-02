'''
ontology_utils.py  Copyright (C) 2024 FSF, Adham Hashibon

utilities needed for the Materials Informatics Ontology (The Hashibon DDMD Research Group at UCL)

It assumes worst case scenario, meaning, emmo as given in https://github.com/emmo-repo/EMMO which uses complex import and a nasty local IRI fragment. The purpose here is to be able to load the ontology into RDFlib, so we can use it as the main vehicle for developing the ontology including emmo and MIO, more over, we would like to bring more sanity to emmo by being able to replace (reversibly) the UUID based IRI with the preflabel and back.

The roadmap includes reasoning support, initially as a service i.e., when loading create an inferred ontology, but any additions will have to be in the asserted state, hence the reasoner will need to be called often, and two version will have to be kept, similar to protege, `asserted` and `inferred`

1. parse_catalouge -->
2. print_vatalouge -->
3. load_ontology -->
4. reorganise_ontology --> organised_graph according to the last local subdomain
5. find_ontology('subdomain')--> a domain specific ontology
6. get last path
7. modify ontology creating mapping to preflabel and back
...
'''

from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import RDF, SKOS, RDFS,  FOAF,  OWL
import xml.etree.ElementTree as ET   
from urllib.parse import urlparse
import os

class OntologyManager:
    def __init__(self, base_path, catalog_file):
        self.base_path = base_path
        self.catalog_file = catalog_file
        self.catalog_path = os.path.join(self.base_path, self.catalog_file)
        self.catalog_mappings = {}
        self.ontology_graphs = {}
        self.organized_ontologies = {}

    def parse_catalog(self):
        # Implementation of catalog parsing

        """
        Parses an OWL catalog file to map ontology URIs to file paths or URLs as in the file.

        Args:
        catalog_path (str): Path to the catalog file.

        Returns:
        dict: A dictionary mapping ontology URIs to paths or URLs.

        

        Example: 
        manager = OntologyManager(base_path='/path/to/ontologies', catalog_file='catalog.xml')
        manager.parse_catalog()


        """
        catalog_file = os.path.join(self.base_path, self.catalog_file)

        mappings = {}
        try:
            # Parse the XML file
            tree = ET.parse(self.catalog_path)
            root = tree.getroot()

            # handle the default namespace, this is something found in the catalog... 
            namespaces = {'': 'urn:oasis:names:tc:entity:xmlns:xml:catalog'}
            for prefix, uri in namespaces.items():
                ET.register_namespace(prefix, uri)

            # Iterate through all 'uri' elements
            for uri_entry in root.findall('.//{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri'):
                name = uri_entry.get('name')
                uri = uri_entry.get('uri')
                if name and uri:
                    mappings[name] = uri
                    self.catalog_mappings[name] = uri

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
        except FileNotFoundError:
            print(f"File not found: {self.catalog_path}")

    def print_catalog(self):
        """
            Reads a file and prints its contents and print the catalog contents for debugging.
            
            Args:
            file_path (str): Path to the file, taken from the class instance attributes. 
        """
        try:
            with open(self.catalog_path, 'r') as file:
                contents = file.read()
                print(contents)
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except IOError as e:
            print(f"Error reading file: {e}")

        # Replace 'path/to/catalog.xml' with the actual path to your catalog file
        # print_file_contents('path/to/catalog.xml')

    def load_ontology(self):
        # Load ontologies into graphs
        pass

    def reorganize_ontology(self):
        # Reorganize ontologies
        pass

    def find_ontology(self, subdomain):
        # Find a specific ontology
        pass

    def get_last_path_segment(self, uri):
        # Extract the last path segment from a URI
        pass

    def modify_ontology_with_mapping(self):
        # Modify ontology creating mapping to prefLabel and back
        pass

    # Additional utility methods as needed

