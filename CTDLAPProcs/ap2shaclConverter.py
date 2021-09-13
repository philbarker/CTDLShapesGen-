from .ap import AP
from .propertyStatement import PropertyStatement
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib import SH, RDF, RDFS, XSD
from uuid import uuid4
from urllib.parse import quote


def make_property_shape_id(ps):
    """Return a URI id based on a property statement label & shape."""
    # TODO: allow user to set preferences for which labels to use.
    if ps.shapes == []:
        sh = "_"
    else:
        # using first shld be enough to dismbiguate
        # need to avoid unnecessary #s
        sh = quote(ps.shapes[0].replace("#", "").replace(" ", "").lower())
    if ps.labels == {}:
        id = "#" + sh + URIRef(str(uuid4()).lower())
        return id
    else:
        languages = ps.labels.keys()
        if "en" in languages:
            label = ps.labels["en"]
        elif "en-US" in languages:
            label = ps.labels["en-US"]
        else:  # just pull the first one that's found
            label = list(ps.labels.values())[0]
        label = label[0].upper() + label[1:]  # lowerCamelCase
        id = URIRef("#" + sh + quote(label.replace(" ", "")))
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


def convert_nodeKind(node_types):
    """Return a shacl nodeKind IRI based on list of permitted node types."""
    if ("IRI" in node_types) and ("BNode" in node_types) and ("Literal" in node_types):
        return None
    if ("IRI" in node_types) and ("BNode" in node_types):
        return SH.BlankNodeOrIRI
    elif ("IRI" in node_types) and ("Literal" in node_types):
        return SH.IRIOrLiteral
    elif ("BNode" in node_types) and ("Literal" in node_types):
        return SH.BlankNodeOrLiteral
    elif "BNode" in node_types:
        return SH.BlankNode
    elif "IRI" in node_types:
        return SH.IRI
    elif "Literal" in node_types:
        return SH.Literal
    else:
        return None


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
                self.sg.add((shape_uri, SH.name, label))
            if shapeInfo[shape]["comment"]:
                comment = Literal(shapeInfo[shape]["comment"])
                self.sg.add((shape_uri, SH.description, comment))
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
            severity = self.convert_severity(ps.severity)
            ps_kind_uri = URIRef(ps_id + "_value")
            self.sg.add((ps_kind_uri, RDF.type, SH.PropertyShape))
            for lang in ps.labels:
                name = Literal(ps.labels[lang], lang=lang)
                self.sg.add((ps_kind_uri, SH.name, name))
            for property in ps.properties:
                path = str2URIRef(self.ap.namespaces, property)
                self.sg.add((ps_kind_uri, SH.path, path))
            self.sg.add(((ps_kind_uri, SH.severity, severity)))
            if ps.valueNodeTypes != []:
                nodeKind = convert_nodeKind(ps.valueNodeTypes)
                self.sg.add((ps_kind_uri, SH.nodeKind, nodeKind))
            if ps.valueDataTypes != []:
                for valueDataType in ps.valueDataTypes:
                    datatypeURI = str2URIRef(self.ap.namespaces, valueDataType)
                    self.sg.add((ps_kind_uri, SH.datatype, datatypeURI))
            if ps.valueConstraints != []:
                sh_constraint_type, constraint = self.convert_valueConstraints(ps)
                self.sg.add((ps_kind_uri, sh_constraint_type, constraint))
            if ps.valueShapes != []:
                for shape in ps.valueShapes:
                    self.sg.add((ps_kind_uri, SH.node, URIRef(shape)))
            if ps.mandatory or not ps.repeatable:
                # Need separate property shape check that property is used correct number of times.
                # Has to separated from other checks as failing ones of those might lead to wrong result on uniqueness.
                ps_count_uri = URIRef(ps_id + "_count")
                self.sg.add((ps_count_uri, RDF.type, SH.PropertyShape))
                for property in ps.properties:
                    path = str2URIRef(self.ap.namespaces, property)
                    self.sg.add((ps_count_uri, SH.path, path))
                if ps.mandatory:
                    self.sg.add((ps_count_uri, SH.minCount, Literal(1)))
                if not ps.repeatable:
                    self.sg.add((ps_count_uri, SH.maxCount, Literal(1)))
                for sh in ps.shapes:
                    self.sg.add((URIRef(sh), SH.property, ps_count_uri))
                self.sg.add(((ps_count_uri, SH.severity, severity)))

    def convert_severity(self, severity):
        """Return SHACL value for severity based on string."""
        if severity == "":
            return Literal("Info")
        elif severity.lower() == "info":
            return SH.Info
        elif severity.lower() == "warning":
            return SH.Warning
        elif severity.lower() == "violation":
            return SH.Violation
        else:
            msg = "severity not recognised: " + ps.severity
            raise Exception(msg)

    def convert_valueConstraints(self, ps):
        """Return SHACL value constraint type and constraint from property statement."""
        constraints = ps.valueConstraints
        constraint_type = ps.valueConstraintType
        node_kind = convert_nodeKind(ps.valueNodeTypes)
        if (len(constraints) > 1) or constraint_type == "picklist":
            # TODO: process as sh:OR
            pass
        elif constraint_type == "":
            if "Literal" in ps.valueNodeTypes:
                constraint = Literal(constraints[0])
            elif "IRI" in ps.valueNodeTypes:
                constraint = str2URIRef(self.ap.namespaces, constraints[0])
            else:
                raise Exception("Incompatible node kind and constraint.")
            return (SH.hasValue, constraint)
        elif constraint_type == "pattern":
            return (SH.pattern, Literal(constraints[0]))
        elif constraint_type == "minLength":
            min_length = int(constraints[0])
            return (SH.minLength, Literal(min_length))
        elif constraint_type == "maxLength":
            min_length = int(constraints[0])
            return (SH.maxLength, Literal(min_length))
        else:
            msg = "unknown type of value constraint: " + constraint_type
            raise Exception(msg)

    def dump_shacl(self):
        """Print the SHACL Graph in Turtle."""
        print("SHACL Dump:")
        print(self.sg.serialize(format="turtle"))
