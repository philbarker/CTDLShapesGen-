from .ap import AP
from .propertyStatement import PropertyStatement
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib import SH, RDF, RDFS
from uuid import uuid4


def make_property_shape_id(ps):
    """Return a URI id based on a property statement label & shape."""
    # TODO: allow user to set preferences for which labels to use.
    # TODO: make sure label is IRI safe before using it in URIRef
    if ps.labels == {}:
        id = URIRef("#" + str(uuid4()).lower())
        return id
    else:
        languages = ps.labels.keys()
        if "en" in languages:
            label = ps.labels["en"]
        elif "en-US" in languages:
            label = ps.labels["en-US"]
        else:  # just pull the first one that's found
            label = list(ps.labels.values())[0]
        label = label[0].lower() + label[1:] # lowerCamelCase
        id = URIRef("#" + label.replace(" ", ""))
        return id


def str2URIRef(namespaces, str):
    """Return a URIRef from a string that may be a URI or a curie."""
    [pre, name] = str.split(":", 1)
    if pre == ("http" or "https"):
        return URIRef(str)
    elif pre in namespaces.keys():
        return URIRef(namespaces[pre] + name)
    else:
        # TODO logging/exception warning that prefix not known
        print("Waring: prefix ", pre, " not in namespace list.")
        return URIRef(str)


class AP2SHACLConverter:
    def __init__(self, ap):
        self.ap = ap
        self.sg = Graph()  # shacl graph
        self.convert_namespaces()
        self.convert_shapes()
        self.convert_propertyStatements()

    def convert_namespaces(self):
        """Bind the namespaces in the application profle to the SHACL graph."""
        for prefix in self.ap.namespaces.keys():
            ns_uri = URIRef(self.ap.namespaces[prefix])
            ns = Namespace(ns_uri)
            self.sg.bind(prefix, ns)

    def convert_shapes(self):
        """Add the shapes from the application profile to the SHACL graph."""
        shapeInfo = self.ap.shapeInfo
        sh = "http://www.w3.org/ns/shacl#"
        for shape in shapeInfo.keys():
            shape_uri = URIRef(shape)
            self.sg.add((shape_uri, RDF.type, SH.NodeShape))
            if shapeInfo[shape]["label"]:
                label = Literal(shapeInfo[shape]["label"])
                self.sg.add((shape_uri, RDFS.label, label))
            if shapeInfo[shape]["comment"]:
                comment = Literal(shapeInfo[shape]["comment"])
                self.sg.add((shape_uri, RDFS.comment, comment))
            if shapeInfo[shape]["target"] and shapeInfo[shape]["targetType"]:
                target = str2URIRef(self.ap.namespaces, shapeInfo[shape]["target"])
                if shapeInfo[shape]["targetType"].lower() == "class":
                    targetType = SH.targetClass
                elif shapeInfo[shape]["targetType"].lower() == "node":
                    targetType = SH.tagetNode
                elif shapeInfo[shape]["targetType"].lower() == "subjectsof":
                    targetType = SH.targetSubjectsOf
                elif shapeInfo[shape]["targetType"].lower() == "objectsof":
                    targetType = SH.targetObjectsOf
                self.sg.add((shape_uri, targetType, target))

    def convert_propertyStatements(self):
        """Add the property statements from the application profile to the SHACL graph as property shapes."""
        for ps in self.ap.propertyStatements:
            ps_id = make_property_shape_id(ps)
            if ps.repeatable:
                pass # nothing else to do
            else:
                pass # create Property shape to assert uniqueness


    def dump_shacl(self):
        """Print the SHACL Graph in Turtle."""
        print("SHACL Dump:")
        print(self.sg.serialize(format="turtle"))
