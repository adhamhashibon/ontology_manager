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

to do: 
-ontology session, which would use the ontology mapings to determined what is loaded,
- the self.graphs {} could be one that maps a name space to a file to a graph, or a map to multiple ontology managers, 
i.e., each ontology loaded, will have an ontology manager, which has metadata as 
described in the paper notebook.  the metadata stores the information about the path, and catalog file etc. 

QUESTION: Do we need another session that the one of rdflib? does rdflib provide a session?
QUESTION: we need a name for the ontology session, 
QUESTION: how can the session be updated with new ontology directly from the init of the ontology manager, i.e., instead of wrapping the ontology manager 
          with session, we call session to update it everytime something happens, in this way, the session is a data structure holding the needed information! 
          session: name of ontology, description, etc, could be itself managed ontologically, i.e., DOME eco system ontology will have a platform ontology which has a session 
                    class, which has an instance self.session, which has properties and relations to other elements... 
                    (has manager, manager has methods, etc, as manager is more than data structure, it is not created by ontology classes, 
                    the session can perhaps though, if it is a pure data structure) 

                This latter approach, storing the metadata also on the specific ontology manager,  is better, as handling all information centrally is not wise. 

                so we have ontology.session which has 
                a map of the ontologies loaded, each having an instance of ontology manager,

        QUESTION: do we need to close the session and remove from memory? if so, does this mean closing all ontologies loaded! of course, 
                    otherwise this is not a session!

                    TODO: This means we need a Session manager too! (i.e., data structures are from CUDS/ontology, but the managers are code)

...
'''

from rdflib.namespace import RDF, SKOS, RDFS,  FOAF,  OWL
from rdflib import Graph, URIRef, Namespace, Literal, BNode
import xml.etree.ElementTree as ET  
from urllib.parse import urlparse
import os, warnings
import re, uuid



    
class OntologyManager:
    """
    OntologyManager manages an ontology using RDFLib. It supports multiple file import and will support reasoning later.
    
    Parameters and Arguments: 

    :param: ontology_base_path: Required, the path to the folder with the ontology 
    :param: catalog_filename:   Required, the filename of the catalog file, though we may make it optional, in the later case
                                we specify it as None. In this case, we need to scan the files for predicates which are imports and proceed. 

                        Note:   initially We require catalog file, as we did not yet implement loading from teh imports directive. 
                                it even for a simple ontology, see documentation for examples. 
    return: An instance to this ontology manager

    """
    
    def __init__(self, ontology_base_path, catalog_filename):  # add needed types etc. Could be for students 
        """
        self.catalog_map: a map from a name (in the catalog file, or the URI, if read from imports and no name defined) and the URI
        from which the ontology is loaded, could be a file path (local), or remote. (TODO)
        # self.catalog_map[name] = uri


         self.ontology_graphs[onto_uri] = g.  : maps a URI from teh catalog_map to an actual dflib graph

         TODO: we have a catalog map from name to path and a ontology to graphs maps which are separate, should not merge them? i.e, one 
                map [name] --> {path: path, graph: g} for example. with method to get(name), 

        """
        self.ontology_base_path = ontology_base_path
        self.catalog_filename   = catalog_filename 
        self.catalog_path       = os.path.join(self.ontology_base_path, self.catalog_filename)
        self.catalog_map = {}
        self.graphs = {}
        self.ontology_graphs = {}

    
    def parse_catalog(self):
        # Implementation of catalog parsing

        """
        Parse an XML ontology catalog file and retuen the mapping name --> URI (which could be a file), e.g., `self.catalog_map[name] = uri`

        Parses an OWL catalog file (if not None) to map ontology URIs to file paths or URLs as in the catalog file 
            TODO: is this fully implemented? we support now for sure actual files, and no loading from the internet.
 
        Make sure the main ontology file is in the catalog too, i.e., all ontology should be in the catalog from start. 
            TODO: load the main ontology file, even if not in the catalouge, here we would need to supply it. 

            Ideally, we would go for the main ontology file, then if there is an import, 
                    check the catalog mapping for the best strategy to load it, from local file or outside.
                    This could even be default TODO: make this an issue for later. 

        No need to provide the main ontology file in the arguments. see previous issue. 

        Parameters and Arguments:
        
        :param: catalog_path (str): Path to the catalog file.

        :param: catalog_filename: or None if no catalog (not implemented yet)
        
        Returns:
        
        dict: A dictionary mapping ontology URIs to paths or URLs.
            TODO: this should be enhanced to support fetching ontology from the URI, i.e., remote/local (as a new column?)

        : Example: 
        manager = OntologyManager(base_path='/path/to/ontologies', catalog_file='catalog.xml')
        TODO: when we have an ontology session, this call should be wrapped (or called from) the session, as the session will 
        have to store the entire metadata about the ontology.

        manager.parse_catalog()
        TODO: same, should move to session

        The XML information (on the catalog file) is at :  # https://docs.python.org/3/library/xml.etree.elementtree.html 

        """

        try:
            # Parse the XML file
            tree = ET.parse(self.catalog_path)
            root = tree.getroot()
            
            # I tried many options, but it seems that using .// as a general xpath works best, need to check if this is true in general.
            # this is rather voodoo...  
            for onto_uri in root.findall('.//'):
                # onto_uri is a structure returned by the ET library. 
                name = onto_uri.get('name') # name is then name in the catalog file. e.g. "http://emmo.info/emmo/1.0.0-beta5/mereocausality"
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
            Reads a file and prints its contents for debugging purposes, not really needed
            
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
        Load the ontology files based on the catalog, requires first that the class is initialized and that the catalog is read. 

        Returns: None 

        populates the self.ontology_graphs dict: A dictionary mapping ontology URIs to their respective RDFLib graphs.

        
        NOTE:   This should work even if the catalog file is not present ,as we should be able to also create teh map from 
                the local imports in the main ontology file if no catalog is needed. 
        """

        
        self.ontology_graphs = {} # change to ontograph? or onto? or graphs? 

        for onto_uri, relative_onto_path in self.catalog_map.items():    
            # Construct the full path to the ontology file
            ontology_path = os.path.join(self.ontology_base_path, relative_onto_path)

            # Create a new RDFLIB graph for this ontology
            g = Graph(bind_namespaces="rdflib")  # we  load all standard name spaces.  TODO: catch errors, and log into the session metadata for this ontology. 
            
                
            # Load the ontology into the graph
            try:
                # TODO: add check if it exists already! skip it, and each time uploaded, update the relevant data structure, for example 
                #       the registered ontology metadata with the session through the data manager instance.  
                g.parse(ontology_path, format='turtle') # todo support other ontology formats? also TODO: better handling of errors (e.g. remove or augment data in the session etc. )
                self.ontology_graphs[onto_uri] = g
                print(f"Loaded ontology: {onto_uri}")
            except Exception as e:
                print(f"Error loading ontology {onto_uri}: {e}")

    
    def find (self, some_keyword):
        """
        
        Find a specific ontology given some keyword (e.g., subdomain) in the URI 
        :params: keyword

        :return: list of URI for the ontology with relevant keywords
        The ontology may then be obtained from self.ontology[key] --> graph 
        
        """
        
        dict_keys = [key for key in self.ontology_graphs if some_keyword in key]
        # we may need to adapt if we merge catalog_map and ontology_graphs

        return dict_keys

    def parse_uri (self, uri):
        """
        Extracts the base and last path segment from a URI (the local fragment).

        :params: uri: Str: The URI to parse.

        :Returns: dict of  {"parsed_uri": parsed_uri, "base_uri": base_uri, "fragment_uri": fragment_uri}
        
        # this does not work, but keeping it for ref.
        # parsed_uri.path.strip('/')[-1] for the fragment (or replace '/' with ':')
        lets try it.  

        """
        
        if not isinstance (uri, URIRef):
            warnings.warn("The provided input is not a URIRef object", RuntimeWarning)
            return ""
        
        parsed_uri = urlparse(uri) # see examples for explanation, we want to cover all cases of 

        if '#' in str(uri):
            fragment_uri = parsed_uri.fragment
            base_uri=parsed_uri.scheme+'://'+parsed_uri.netloc+parsed_uri.path
        elif ':' in str(parsed_uri.path): 
            fragment_uri = parsed_uri.path.split(':')[-1]
            base_uri = URIRef(str(uri))[:-len(fragment_uri)]
        else:
            fragment_uri = parsed_uri.path.split('/')[-1]
            base_uri = URIRef(str(uri))[:-len(fragment_uri)]
        
        # various tests, keeping for ref.
        #base_url = urlunparse(parsed_uri._replace(path='/', fragment=''))
        #return parsed_uri.path.strip('/').split('/')[-1]
        #return { "base_uri": base_uri, "fragment_uri": fragment_uri}
        print ("parsed_uri", parsed_uri, "base_uri", base_uri, "fragment_uri", fragment_uri )
        return {"parsed_uri": parsed_uri, "base_uri": base_uri, "fragment_uri": fragment_uri}
        
    def fix_emmo_label(self, onto_prefix, onto_namespace):
        """
        Modify the label of ontology items produced by protege method for prefix+Global ID (a UUID with _) 
        to human friendly labels. 

        a mapping is created and is embedded into the modified ontology (added property hasUIDLabel with the old label). 
        this is so we can map it back if needed. 

        the reason for this is that using the label makes life much easier for working with the ontology, as
        the ontology is a sort of human-machine interface. Using code, is extremely prone to error and makes development very 
        uneasy. 


        parameters: 
        :onto_prefix: is the prefix used in the protege, see https://github.com/emmo-repo/EMMO/blob/master/doc/protege-setup.md
        the parameter should be set to PREFIX_ : a given prefix for the ontology in protege.

        :onto_namespace is the name space, e.g, http://emmo.info/emmo# that should be changed, the separator (#, /, :) is needed.



        : internal comments for devs
        pattern=rf'^{re.escape(prefix)}[0-9a-fA-F_\-]+'
        matched a prefix and any UID with _ or - in the name. 
        use: if re.match(pattern, sl): where sl is the local name extraxcted by parse_uri (also check the qname method of rdflib)

        Take EMMO which uses a local fragment like this: EMMO_<some UID> which makes it obscure to work with, 
        hence we have this utility that does the following: 

        - checks if there is a label (RDFS:label or SKOS:preflabel) 
        - extracts the obscure EMMO_<UID>` from each entity
        - adds a new data property to each entity : hasOriginalLocalLabel 
        - sets hasOriginalLocalLabel  to the Literal of the EMMO_<UID>
        - gets the part of the IRI without the fragment, 
        - replaces it with the new label

        TODO: 
        take an ontology management data structure and 
        define the onto_IRI_prefix that is used by protege, 
        and the digit count (should be 20 usually)
        and then build the query: 

        import re 
        uuid_pattern = re.compile(r"PREFIX_[0-9a-fA-F]{8}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{12}")
        or 
        (https://bukkit.org/threads/best-way-to-check-if-a-string-is-a-uuid.258625/)
        String uuid = ""; //define it!
        if (uuid.matches("[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")) {

        the above assumed UUID, but it seems protege uses something else. 
        
        (All UUID's are in the form of 8-4-4-4-12, with the numbers representing hexadecimals.)


        
        """
        print(80*'-')
        print(80*'-')
        print(80*'-')

        print("inside fix emmo label")
        #for _, g in self.ontology_graphs.items():
        #    if "properties" in _:
        #        for s,p, o in g:
        #            print('[', str(s), str(p), str(o),']', self.parse_uri(s), '\n')
        

        print("replacing the prefix ", onto_prefix, "with name space", onto_namespace)
        # find the properties ontology, just for testing. 
        k=self.find('properties')
        [print(i) for i in k]       

        print(k[0])
        for s, p, o in self.ontology_graphs[k[0]]:
            # check if the fragment (label), is of the form prefix+uuid then print. 
            #print (s, p, o)
            #guid_pattern = re.compile(r"onto_prefix[0-9a-fA-F]{8}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{12}")

            for e in [s, p, o]: 
                if isinstance(e, URIRef):
                #    print ("Eureka")
                #print (e, guid_pattern.search(str(e)))
                #print (self.is_valid_uuid())       
                    #print ("hello", type(self.parse_uri(e)),e, self.parse_uri(e)["fragment_uri"],"\n")
                    if self.is_valid_uuid( self.parse_uri(e)["fragment_uri"]):
                        print ("hello",  self.parse_uri(e)["fragment_uri"],"\n")
        """
          now that we know got the test ontology, lets loop and change each strange local fragment to something useful, 
          however note we cannot just simple replace the first occurrence, as the same fragment can appear in many subjects and subjects. 

          one option is to use a map store, we call it uid_label_map for example, then we need everytime to ask 
            - is this uri a uid type, if yes, do we have already a mapping, if yes use it, if not create one. 

            note though that the mapping could be part of the new ontology, if we are copting. need to check how rdflib updates graphs.      
        """
    
    def unfix_emmo_label(self):
        pass



    def is_valid_uuid(val):
        """
        see https://stackoverflow.com/questions/53847404/how-to-check-uuid-validity-in-python
        """
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False