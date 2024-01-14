"""
ontology_utils.py  Copyright (C) 2024 The Materials informatics and Data Driven Materials Discovery Group at UCL

Utilities needed for the Materials Informatics Ontology
Enables the development and maintenance of ontology in a
fully programmatic manner with out the need for protege or the like.

see Roadmap.md for planned features.

"""

from rdflib.namespace import RDF, SKOS, RDFS, FOAF, OWL
from rdflib import Graph, URIRef, Namespace, Literal, BNode
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import os, warnings
import re, uuid
from typing import Union


class OntologyManager:
    """
    OntologyManager manages an ontology using RDFLib.

    It supports multiple file import and will support reasoning later.

    This is the main class.
    """

    def __init__(self, ontology_base_path, catalog_filename):
        """
        # TODO:add needed types etc.
        params:

        ontology_base_path:  Required, the path to the folder with the ontology
        catalog_filename or ontology file:  Required, the filename of the catalog file
        or the ontology file name (if only one file, e.g, emmo inferred)

        return: An instance to this ontology manager

        defines attributes:

        self.catalog_map: a map from a name (in the catalog file, or the URI, if read from imports and no name defined) and the URI
        from which the ontology is loaded, could be a file path (local), or remote. (TODO)

        self.catalog_map[name] = uri


        self.ontology_graphs[onto_uri] = g.  : maps a URI from teh catalog_map to an actual dflib graph

        """
        self.ontology_base_path = ontology_base_path
        self.catalog_filename = catalog_filename
        self.catalog_path = os.path.join(self.ontology_base_path, self.catalog_filename)
        self.catalog_map = {}
        self.ontology_graphs = {}


    def parse_catalog(self):
        """

        Parse an XML ontology catalog file and return the mapping (ontology) name --> URI (which could be a file),
        e.g., `self.catalog_map[name] = uri`

        Example:

        manager = OntologyManager(base_path='/path/to/ontologies', catalog_file='catalog.xml')

        The XML information (on the catalogue file) is at :  # https://docs.python.org/3/library/xml.etree.elementtree.html

        """

        try:
            # Parse the XML file
            tree = ET.parse(self.catalog_path)
            root = tree.getroot()

            # I tried many options, but it seems that using .// as a general xpath works best,
            # need to check if this is true in general.
            # this is rather voodoo somewhat  ...
            for onto_uri in root.findall('.//'):
                # onto_uri is a structure returned by the ET library.
                name = onto_uri.get(
                    'name')  # name is then name in the catalog file. e.g. "http://emmo.info/emmo/1.0.0-beta5/mereocausality"
                uri = onto_uri.get('uri')
                # this reads the lines <uri name=... uri=.../>
                if name and uri:
                    self.catalog_map[name] = uri
                    print("name=", name, "uri=", uri)
        except ET.ParseError as e:
            print(f"Error parsing ontology catalog file: {e}")
        except FileNotFoundError:  # does this even work here?
            print(f"ops... File not found: {self.catalog_path}")


    def print_catalog(self):
        """
            Reads a file and prints its contents for debugging purposes, not really needed
            param: Nothing
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

        Load the ontology from the files/URL's based on the catalogue,
        requires first that the class is initialised and
        that the catalogue is read-in.

        Returns: None

        Populates the self.ontology_graphs dict: A dictionary mapping ontology URIs (names) to
        their respective RDFLib graphs.

        NOTE: TODO: This should work even if the catalogue file is not present, as we should be able to also create the map
        from the local imports in the main ontology file if no catalog is needed.
        """

        self.ontology_graphs = {}

        for onto_uri, relative_onto_path in self.catalog_map.items():
            ontology_path = os.path.join(self.ontology_base_path, relative_onto_path)
            g = Graph(bind_namespaces="rdflib")  #
            try:
                g.parse(ontology_path,
                        format='turtle')  # TODO #12 load-ontology: does not check if an ontology is already loaded.
                self.ontology_graphs[onto_uri] = g
                print(f"Loaded ontology: {onto_uri}")
            except Exception as e:
                print(f"Error loading ontology {onto_uri}: {e}")


    def find(self, some_keyword: str = ""):
        """
        Find a specific ontology given some keyword (e.g., subdomain) in the URI

        params: keyword

        return: list of URI for the ontology with relevant keywords
        The ontology may then be obtained from self.ontology[key] --> graph
        """

        dict_keys = [key for key in self.ontology_graphs if some_keyword in key]
        # we may need to adapt if we merge catalog_map and ontology_graphs

        return dict_keys


    def parse_uri(self, uri: URIRef = None):
        """

        Extracts the base and last path segment from a URI (the local fragment).

        params: uri: Str: The URI to parse.

        Returns: dict of  {"base_uri": base_uri, "separator": sepaarator. "fragment_uri": fragment_uri}
        e.g.
        uri= http://emmo.info/emmo#EMMO_9be5fcc4_0d8b_481d_b984_6338d4b55588
        parsed_uri= {separator: '#',
                    'base_uri': 'http://emmo.info/emmo',
                    'fragment_uri': 'EMMO_9be5fcc4_0d8b_481d_b984_6338d4b55588'}
        """
        if not isinstance(uri, URIRef):
            warnings.warn("The provided input is not a URIRef object", RuntimeWarning)
            return ""

        parsed_uri = urlparse(uri)

        if '#' in str(uri):
            fragment_uri = parsed_uri.fragment
            base_uri = parsed_uri.scheme + '://' + parsed_uri.netloc + parsed_uri.path
            separator = '#'
        elif ':' in str(parsed_uri.path):
            fragment_uri = parsed_uri.path.split(':')[-1]
            base_uri = URIRef(str(uri))[:-len(fragment_uri)]
            separator = ':'
        else:
            fragment_uri = parsed_uri.path.split('/')[-1]
            base_uri = URIRef(str(uri))[:-len(fragment_uri)]
            separator = '/'

        #return {"parsed_uri": parsed_uri, "separator": separator, "base_uri": base_uri, "fragment_uri": fragment_uri}
        # no need for parsed_uri, could add later if we need the query etc.
        return {"separator": separator, "base_uri": base_uri, "fragment_uri": fragment_uri}

    def emmo_to_label(self, onto_namespace: Union[URIRef, str] = None, onto_prefix: str = None, new_annotation: str = None):
        """
        Modify the label of ontology items produced by protege method for prefix+Global ID (a UUID with _)
        to human friendly/collaboration easy labels.

        a mapping is created and is embedded into the modified ontology (added property hasUIDLabel with the old label).
        this is so we can map it back if needed.


        parameters:
        :onto_prefix: is the prefix used in the protege, see https://github.com/emmo-repo/EMMO/blob/master/doc/protege-setup.md
        the parameter should be set to PREFIX_ : a given prefix for the ontology in protege.
        e.g. EMMO_ for emmo.

        :onto_namespace is the name space, e.g, http://emmo.info/emmo that should be changed, the separator (#, /, :) should not be provided.

        :new_annotation: is the new annotation property, e.g. skos:prefLabel, rdfs:label, ...

        Although designed for EMMO, it is intended to be general.

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
        # for _, g in self.ontology_graphs.items():
        #    if "properties" in _:
        #        for s,p, o in g:
        #            print('[', str(s), str(p), str(o),']', self.parse_uri(s), '\n')

        print("replacing the prefix ", onto_prefix, "with name space", onto_namespace)
        # find the properties ontology, just for testing.

        k = self.find('perceptual')
        print(k)
        # guid_pattern = re.compile(r"onto_prefix[0-9a-fA-F]{8}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{12}")

        g1 = self.ontology_graphs[k[0]]
        print(g1)

        for g in [g1]:  # in self.ontology_graphs.values():
            print(g)
            for s, p, o in g:
                for e in [s, p, o]:
                    if isinstance(e, URIRef):
                        parsed_uri = self.parse_uri(e)
                        local_name = parsed_uri["fragment_uri"]
                        name_space = parsed_uri["base_uri"]
                        iri_separator = parsed_uri["separator"]
                        assert (e == name_space + iri_separator + local_name)
                        if name_space.startswith(onto_namespace) and local_name.startswith(onto_prefix):
                            # print(onto_namespace, name_space, onto_prefix, local_name)
                            gid = local_name.split(onto_prefix)[-1]
                            # print(gid, self.is_custom_uuid(gid))
                            # print(e)

                            # print(s,p,o)
                            print("old e", e, f"({s, p, o})")
                            # print("new e", URIRef(name_space+iri_separator+"XX"))
                            if g.value(e, new_annotation) is not None:
                                print(f"new anno is {g.value(e, new_annotation)}")
                            # print(f"new anno is {(e, URIRef(new_annotation))}")

        # for s, p, o in self.ontology_graphs[k[0]]:
        # replace statements with s

        """
          now that we know got the test ontology, lets loop and change each strange local fragment to something useful, 
          however note we cannot just simple replace the first occurrence, as the same fragment can appear in many subjects and subjects. 
    
          one option is to use a map store, we call it uid_label_map for example, then we need everytime to ask 
            - is this uri a uid type, if yes, do we have already a mapping, if yes use it, if not create one. 
    
            note though that the mapping could be part of the new ontology, if we are copting. need to check how rdflib updates graphs.      
        """


    def unfix_emmo_label(self):
        pass


    def is_valid_uuid(self, val):
        """
        see https://stackoverflow.com/questions/53847404/how-to-check-uuid-validity-in-python
        """
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False


    @staticmethod
    def is_custom_uuid(s):
        pattern = r'\b[a-f0-9]{8}_[a-f0-9]{4}_[a-f0-9]{4}_[a-f0-9]{4}_[a-f0-9]{12}\b'
        return bool(re.fullmatch(pattern, s.lower()))


    # Test the function
    # test_string = "967080e5_2f42_4eb2_a3a9_c58143e835f9"
    # print(is_custom_uuid(test_string))  # This should return True if the string matches the pattern


    @staticmethod
    def emmo_to_label_graph(onto_namespace: Namespace, new_annotation: URIRef, g: Graph):
        """
        Scan the graph `g`, and replace annotation (the label) of any entity in `Namespace` using the property annotation
        `new_annotation`.

        onto_namespace: URIRef: the name space of the ontology we want to replace.
        new_annotation: URIRef: the new label should be an existing propery, e,g. skos:prefLabel
        g:              Graph


        return {"s_map": s_map, "o_map": o_map, "p_map": p_map}
                a dictionary of mapping old_iri to new_iri for each s, p, and o.
        """

        onto_namespace = Namespace(onto_namespace)

        s_map = {}
        o_map = {}
        p_map = {}

        # repetition, I know, but it works fine, verbatim is nice sometimes.
        # TODO:make issue and use a function/method instead
        for s, p, o in g:
            x = g.value(s, new_annotation)
            if x is not None:
                # print(f"value found of {type(x)} with value {x}")
                if s not in s_map:
                    print(f"adding map between {s} and {x}")
                    s_map[s] = onto_namespace[str(x)]

            x = g.value(o, new_annotation)
            if x is not None:
                # print(f"value found of {type(x)} with value {x}")
                if o not in o_map and o not in s_map:
                    print(f"adding map between {o} and {x}")
                    o_map[o] = onto_namespace[str(x)]

            x = g.value(p, new_annotation)
            if x is not None:
                # print(f"value found of {type(x)} with value {x}")
                if p not in p_map and p not in s_map and p not in o_map:
                    print(f"adding map between {p} and {x}")
                    p_map[p] = onto_namespace[str(x)]

        """     
        g2=Graph()
        g2+=g
        from itertools import chain 
        for old_iri, new_iri in chain(s_map.items(), p_map.items(), o_map.items()):
            for s, p, o in g:
                if s == old_iri:
                    g.remove((s, p, o))
                    g.add((new_iri, p, o))
                elif p == old_iri:
                    g.remove((s, p, o))
                    g.add((s, new_iri, o))
                elif o == old_iri:
                    g.remove((s, p, o))
                    g.add((s, p, new_iri))
            
        """
        return {"s_map": s_map, "o_map": o_map, "p_map": p_map}


    def replace_iri(self):
        """
        """

        mega_g = Graph()
        for ontology_name, g in self.ontology_graphs.items():
            mega_g += g

        sop_map = self.emmo_to_label_graph("http://emmo.info/emmo#", SKOS.prefLabel, mega_g)
        print("done mapping")

        total_graphs = len(self.ontology_graphs)
        done_so_far = 0
        for ontology_name, g in self.ontology_graphs.items():
            print(f"graph No. {done_so_far}/{total_graphs}")
            done_so_far = done_so_far + 1

            for k, v in sop_map.items():
                print(k, len(v))
                # loop over s, o, and p maps
                for old_iri, new_iri in v.items():
                    # print(f"old {old_iri}, new {new_iri}")
                    # for each map, loop over s/p/o and new IRI
                    for s, p, o in g:
                        if s == old_iri:
                            g.remove((s, p, o))
                            g.add((new_iri, p, o))
                        elif p == old_iri:
                            g.remove((s, p, o))
                            g.add((s, new_iri, o))
                        elif o == old_iri:
                            g.remove((s, p, o))
                            g.add((s, p, new_iri))


    def replace_iri2(self):
        """
        """

        mega_g = Graph()
        for ontology_name, g in self.ontology_graphs.items():
            mega_g += g

        sop_map = self.emmo_to_label_graph("http://emmo.info/emmo#", SKOS.prefLabel, mega_g)
        print("done mapping")

        total_graphs = len(self.ontology_graphs)
        done_so_far = 0
        for ontology_name, g in self.ontology_graphs.items():
            print(f"graph {ontology_name}: No. {done_so_far}/{total_graphs}")
            done_so_far = done_so_far + 1

            for k, v in sop_map.items():
                print(k, len(v))
                # loop over s, o, and p maps
                for old_iri, new_iri in v.items():
                    # SPARQL query to check for the IRI
                    query = """
                                ASK WHERE {
                                    { <%s> ?p ?o }
                                    UNION
                                    { ?s <%s> ?o }
                                    UNION
                                    { ?s ?p <%s> }
                                }
                                """ % (old_iri, old_iri, old_iri)
                    if g.query(query).askAnswer:
                        # print(f"old {old_iri}, new {new_iri}")
                        # for each map, loop over s/p/o and new IRI
                        for s, p, o in g:
                            if s == old_iri:
                                g.remove((s, p, o))
                                g.add((new_iri, p, o))
                            elif p == old_iri:
                                g.remove((s, p, o))
                                g.add((s, new_iri, o))
                            elif o == old_iri:
                                g.remove((s, p, o))
                                g.add((s, p, new_iri))


    def replace_iri3(self):
        """
        """

        mega_g = Graph()
        for ontology_name, g in self.ontology_graphs.items():
            mega_g += g

        sop_map = self.emmo_to_label_graph("http://emmo.info/emmo#", SKOS.prefLabel, mega_g)
        print("done mapping")

        total_graphs = len(self.ontology_graphs)
        done_so_far = 0
        for ontology_name, g in self.ontology_graphs.items():
            print(f"graph {ontology_name}: No. {done_so_far}/{total_graphs}")
            done_so_far = done_so_far + 1

            for k, v in sop_map.items():

                print(k, len(v))
                # loop over s, o, and p maps
                for old_iri, new_iri in v.items():
                    # SPARQL update query
                    update_query = """
                                DELETE {{ ?s ?p <{old_iri}> }} INSERT {{ ?s ?p <{new_iri}> }} WHERE {{ ?s ?p <{old_iri}> }};
                                DELETE {{ <{old_iri}> ?p ?o }} INSERT {{ <{new_iri}> ?p ?o }} WHERE {{ <{old_iri}> ?p ?o }};
                                DELETE {{ ?s <{old_iri}> ?o }} INSERT {{ ?s <{new_iri}> ?o }} WHERE {{ ?s <{old_iri}> ?o }};
                                    """.format(old_iri=old_iri, new_iri=new_iri)
                    # Execute the update query
                    g.update(update_query)
