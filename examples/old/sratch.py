# Rename class veh:Auto to veh:Car
# For each ?instance of ?oldClass
# Replace the triple <?instance rdf:type ?oldClass>
#               with <?instance rdf:type ?newClass>
DELETE {?instance rdf:type ?oldClass}
INSERT {?instance rdf:type ?newClass}
WHERE  {BIND (veh:Auto as ?oldClass)
        BIND (veh:Car as  ?newClass)
        ?instance rdf:type ?oldClass . }




        for s, p, o in g:
                for e in [s, p, o]: 
                    if isinstance(e, URIRef):
                        parsed_uri = self.parse_uri(e)
                        local_name  = parsed_uri["fragment_uri"]
                        name_space = parsed_uri["base_uri"]
                        iri_separator = parsed_uri["separator"]
                        assert (e, name_space+iri_separator+local_name)
                        if name_space.startswith(onto_namespace) and local_name.startswith(onto_prefix):
                            #print(onto_namespace, name_space, onto_prefix, local_name)
                            gid = local_name.split(onto_prefix)[-1] 
                            #print(gid, self.is_custom_uuid(gid))
                            #print(e)
                            #print(s,p,o)
                            print("old e", e)
                            print("new e", URIRef(name_space+iri_separator+"XX"))
                            print(f"new anno is {g.value(e, new_annotation)}")
                            print(f"new anno is {(e, URIRef(new_annotation))}")



"""

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