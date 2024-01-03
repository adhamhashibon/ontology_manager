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

from rdflib.namespace import RDF, SKOS, RDFS,  FOAF,  OWL
from rdflib import Graph, URIRef, Namespace, Literal, BNode
import xml.etree.ElementTree as ET  
from urllib.parse import urlparse
import os

class OntologyManager:
    """
    OntologyManager manages an ontology using RDFLib. It supports multiple file import and will support reasoning later.
    :param ontology_base_path: Required, the path to the folder with the ontology 
    : param catalog_filename: Required the filename of the catalog file, though we may make it optional 
      but now we require it even for a simple ontology, see documentation for examples. 
    return: 
    """
    def __init__(self, ontology_base_path, catalog_filename):
        self.ontology_base_path = ontology_base_path
        self.catalog_filename = catalog_filename 
        self.catalog_path = os.path.join(self.ontology_base_path, self.catalog_filename)
        self.catalog_map = {}
        self.graphs = {}
        self.ontology_graphs = {}

    def parse_catalog(self):
        # Implementation of catalog parsing

        """
        Parses an OWL catalog file to map ontology URIs to file paths or URLs as in the file.
        Make sure the main ontology file is in the catalog too, i.e., all ontology should be int eh catalog from start. 
        No need to provide the main ontology file in the arguments. 
        Args:
        catalog_path (str): Path to the catalog file.

        Returns:
        dict: A dictionary mapping ontology URIs to paths or URLs.

        : Example: 
        manager = OntologyManager(base_path='/path/to/ontologies', catalog_file='catalog.xml')
        manager.parse_catalog()

        The XML information is on :  # https://docs.python.org/3/library/xml.etree.elementtree.html 

        """
        
        try:
            # Parse the XML file
            tree = ET.parse(self.catalog_path)
            root = tree.getroot()
            
            # I tried many options, but it seems that using .// as a general xpath works best, need to check if this is true in general. 
            for onto_uri in root.findall('.//'):
                name = onto_uri.get('name')
                uri = onto_uri.get('uri')
                # this reads the lines <uri name=... uri=.../>
                if name and uri:
                    self.catalog_map[name] = uri
                    print("name=", name, "uri=", uri)    
        except ET.ParseError as e:
            print(f"Error parsing ontology catalog file: {e}")
        except FileNotFoundError: # does this even work here?
            print(f"ops... File not found: {self.catalog_path}")
        

    def print_catalog(self):
        """
            Reads a file and prints its contents and print the catalog contents for debugging purposes.
            
            :param: Nothing
        """
        try:
            with open(self.catalog_path, 'r') as file:
                contents = file.read()
                print(contents)
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except IOError as e:
            print(f"Error reading file: {e}")

    def load_ontology(self):
        """
        Load the ontology files based on the catalog, requires first that the class is initialised. 

        Returns:
        dict: A dictionary mapping ontology URIs to their respective RDFLib graphs.
        """
        
        self.ontology_graphs = {}
        for onto_uri, relative_onto_path in self.catalog_map.items():
            # Construct the full path to the ontology file
            ontology_path = os.path.join(self.ontology_base_path, relative_onto_path)

            # Create a new RDFLIB graph for this ontology
            g = Graph()

            # Load the ontology into the graph
            try:
                g.parse(ontology_path, format='turtle')
                self.ontology_graphs[onto_uri] = g
                print(f"Loaded ontology: {onto_uri}")
            except Exception as e:
                print(f"Error loading ontology {onto_uri}: {e}")

    
    def find (self, some_keyword):
        """
        Find a specific ontology given some keyword (e.g., subdomain)
        :params: keyword
        :return: list of URI for the ontology with relevant keywords
        The ontology may then be obtaubed from self.ontology[URI] --> graph 
        """
        dict_keys = [key for key in self.ontology if some_keyword in key]

        return dict_keys

    def parse_uri (self, uri):
        """
            Extracts the base and last path segment from a URI (the local fragment).

        :params: uri: Str: The URI to parse.

        :Returns: str: The base segment of the path in the URI.
        :Returns: str: The last segment of the path in the URI.

        Note this implementation works only for a IRI with #, i.e., it assumes the IRI is 
        http:/somethjng.com/emmo/blabla#fragment 

        however, if it is something like
        
        http:/somethjng.com/emmo/blabla/fragment

        or

        http:/something.com/emmo/blabla:fragment 

        this would not work and we would need to use the path option:


        parsed_uri.path.strip('/')[-1] for the fragment (or replace '/' with ':')
        lets try it.  


        
        """
        parsed_uri = urlparse(uri)
        #base_url = urlunparse(parsed_uri._replace(path='/', fragment=''))

        #return parsed_uri.path.strip('/').split('/')[-1]
        return parsed_uri
    

    def fix_emmo_label(self):
        """

        Take EMMO which uses a local fragment like this: EMMO_<some UID> which makes it obscure to work with, 
        hence we have this utility that does the following: 

        - checks if there is a label (RDFS:label or SKOS:preflabel) 
        - extracts the obscure EMMO_<UID>` from each entity
        - adds a new data property to each entity : hasOriginalLocalLabel 
        - sets hasOriginalLocalLabel  to the Literal of the EMMO_<UID>
        - gets the part of the IRI without the fragment, 
        - replaces it with the new label
        
        """
    
        for _, g in self.ontology_graphs.items():
             for s,p, o in g:
                print(str(s), self.parse_uri(s))
            
        

        
    
    def unfix_emmo_label(self):
        pass

