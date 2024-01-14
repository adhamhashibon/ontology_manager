import os
import io
import pydotplus
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot
import copy
from rdflib import RDFS, Literal, Graph, BNode, Namespace, URIRef

# Initialize a global counter for the serial number
output_file_serial_number = 0


def next_serial():
    """
        used for automatic storing of the ontology images and dot fils from ontoVis,
        in the output folder, with image name seially incremented.
        TODO: could be a class parameter!
    """

    global output_file_serial_number
    output_folder = "OnoVis.Output"  # TODO: should be a class parameter
    # keep incrementing until we find a number we can use.
    while True:
        serial_filename = f"{output_folder}/OntoVis-{output_file_serial_number}.png"
        if not os.path.exists(serial_filename):
            return output_file_serial_number
        output_file_serial_number += 1


def vis(g, start_serial_number=None, max_string_length=None):
    """
    TODO: visualise a graph, should this be a class method or a separate function, or a method that
    has access to the class state?
    if we need an ontoVis instance for each visualisation of each graphm then yes.
    probably once I implement the proxy filter 9see below) this would make sense, as
    only one graph usually is needed,

    then I can procy graphs like so:

    gfilterred = Proxy(g, filter)
    and then path the filter obejct, .. instead of making copites of g..
    """
    global output_file_serial_number  # TODO: should be a class parameter
    output_folder = "OnoVis.Output"  # TODO: should be a class parameter
    # Create a copy of the graph
    g_copy = copy.deepcopy(g)
    # TODO: we could skip this and put in a filter function in place,
    # TODO: that checks if the a predicate should be included or not based on pre set hueristics.

    # Remove triples with rdfs:comment or long literals, ( this is the heuristics basically)
    for s, p, o in g:
        if p == RDFS.comment or (isinstance(o, Literal) and len(str(o)) > max_string_length):
            g_copy.remove((s, p, o))  # would be skiped, in the filter above. (checl a Px=Proxy(x, filter) generator);

    # get the next available serial number of the output
    if start_serial_number is None:
        serial = next_serial()

    # from teh pydotplut example..
    stream = io.StringIO()
    rdf2dot(g_copy, stream)

    dg = pydotplus.graph_from_dot_data(stream.getvalue())
    png = dg.create_png()

    # Create the "output" folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    filename = f"{output_folder}/OntoVis-{serial}.png"  # TODO: use from class instance
    dot_filename = f"{output_folder}/OntoVis-{serial}.dot"  # TODO: use from class instance

    # Display the image in the notebook
    display(Image(png))

    # Save the image and dot file to the filenames in the output folder
    with open(filename, "wb") as f:
        f.write(png)

    with open(dot_filename, "w") as dot_file:
        dot_file.write(stream.getvalue())


class OntoVis:
    """
    provide some graph operatiosn to help visualisation, should change the name ...
    """
    def __init__(self, g: Graph):
        self.RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        self.OWL = Namespace("http://www.w3.org/2002/07/owl#")
        self.g = g

    def clean_graph(self):
        """
        clean the length of attributes etc, but could be costly if the graph is large!
        better use a classmethod based on the code in vis above.
        """
        pass

    def zoom_in_classes(self, root_class: URIRef, depth=(1, 1)):
        """
        TODO: add this to the rdflib Graph method? does this make sense, instead of
        duplicating the work here?

        Note, this can be merged with zoom_in for a general method with some options.
        """
        sub_graph = Graph()

        self._add_subclasses(URIRef(root_class), sub_graph, depth[1])
        self._add_superclasses(URIRef(root_class), sub_graph, depth[0])
        return sub_graph

    def _add_subclasses(self, class_uri, sub_graph, depth):
        if depth == 0:
            return
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?subclass
        WHERE {
            ?subclass rdfs:subClassOf <%s> .
        }
        """ % class_uri
        for row in self.g.query(query):
            print(row)
            subclass_uri = row.subclass
            sub_graph.add((subclass_uri, self.RDFS.subClassOf, class_uri))
            self._add_subclasses(subclass_uri, sub_graph, depth - 1)

    def _add_superclasses(self, class_uri, sub_graph, depth):
        if depth == 0:
            return
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?superclass
        WHERE {
            <%s> rdfs:subClassOf ?superclass .
        }
        """ % class_uri
        for row in self.g.query(query):
            print(row)
            superclass_uri = row.superclass
            sub_graph.add((class_uri, self.RDFS.subClassOf, superclass_uri))
            self._add_superclasses(superclass_uri, sub_graph, depth - 1)

    from rdflib import Graph, URIRef

    def zoom_in(self, root_uri, distance):
        """
        zoom into a class/individual, and give back all relations and triplets up to a distance
        which is how many relations in between.
        """
        zoom_in_graph = Graph()
        self._traverse_graph(root_uri, zoom_in_graph, distance, set())
        return zoom_in_graph

    def _traverse_graph2(self, uri, zoom_in_graph, distance, visited):
        if distance == 0 or uri in visited or uri == self.OWL.Class or uri == self.RDFS.Comment:
            return

        if isinstance(uri, Literal):
            return

        visited.add(uri)
        if isinstance(uri, BNode):
            # zoom_in_graph += self.zoom_in(uri, 1)
            print(f"hello: {uri}")

        # Query all related triples
        query = """
            SELECT ?s ?p ?o
            WHERE {
                {BIND (<%s> as ?s)
                { ?s ?p ?o  }} UNION
                {BIND (<%s> as ?o)
                { ?s ?p ?o  }} 
            }
        """ % (uri, uri)

        for s, p, o in self.g.query(query):
            zoom_in_graph.add((s, p, o))
            # Recursive exploration for subject and object
            if s != uri and s != self.OWL.Class and s != self.RDFS.comment:
                self._traverse_graph(s, zoom_in_graph, distance - 1, visited)
            if o != uri and o != self.OWL.Class or not isinstance(o, Literal):
                self._traverse_graph(o, zoom_in_graph, distance - 1, visited)

    def _traverse_graph(self, uri, zoom_in_graph, distance, visited):
        """
        this version uses rdflib utilities, rather than sparql as the later is blind to bnodes!
        """
        if distance == 0 or uri in visited or uri == self.OWL.Class or uri == self.RDFS.Comment:
            return

        if isinstance(uri, Literal):
            return

        visited.add(uri)
        if isinstance(uri, BNode):
            # zoom_in_graph += self.zoom_in(uri, 1)
            print(f"hello: {uri}")

        # Query all related triples

        for s, p, o in self.g:
            if s == uri or o == uri:
                zoom_in_graph.add((s, p, o))
                # Recursive exploration for subject and object
                if s != uri and s != self.OWL.Class and s != self.RDFS.comment:
                    self._traverse_graph(s, zoom_in_graph, distance - 1, visited)
                if o != uri and o != self.OWL.Class or not isinstance(o, Literal):
                    self._traverse_graph(o, zoom_in_graph, distance - 1, visited)

    @staticmethod
    def dig_into_bnode(g, node, depth=0):
        """
        just a simple function, probably not needed since we have a zoon in
        """
        for s, p, o in g.triples((node, None, None)):
            print(f"\t*depth {s} \t {p} \t {o}")
            if isinstance(o, BNode) and o != node:
                OntoVis.dig_into_bnode(g, o, depth + 1)
        """
        for s, p, o in g.triples((None, None, node)):
            if s != node:
                print(f"{indent}{s} \t {p} \t {o}")
                if isinstance(s, BNode):
                    recurse_bnode(g, s, depth + 1)
        """

    @staticmethod
    def explode_bnode(g: Graph, bnode: BNode):
        """
        expand a bnode (explode it) so that we see what it is composed from.
        TODO: move to ontoman
        Note: this could be a general one! we can use also the above zoom_in_graph to zoom on one side of
        a node, which just happenes to be a bnode!
        not sure if it needs access to self.graph! but I want to use it for any small graph too.

        """
        OntoVis.dig_into_bnode(g, bnode)

    @staticmethod
    def is_bnode(node):
        """
        utility function, check if bnode, if yes, return the uuid.

        """
        if isinstance(node, BNode):
            return str(node)  # Return the UUID of the BNode
        return None  # if it's not a BNode


class Filter_Proxy:
    """
    Proxy to wrap a data structure, e.g., note this is not really a proxy,
    but useful to filter graphs on teh fily.
            # Example filter function for triples
    def filter_triple(s, p, o):
        # Example condition: filter triples where predicate matches a certain criterion
        return p == "some_predicate"

    # Example usage with triples
    x = [("subject1", "some_predicate", "object1"),
         ("subject2", "another_predicate", "object2"),
         ("subject3", "some_predicate", "object3")]

    px = Proxy(x, filter_triple)
    for s, p, o in px:
        print(s, p, o)  # Prints triples that satisfy the filter_triple condition

    TODO: check alternative, proxy pattern with hooks for __getattr_...
    """
    def __init__(self, x, filter_func):
        self.x = x
        self.filter_func = filter_func

    def __iter__(self):
        return (item for item in self.x if self.filter_func(*item))

