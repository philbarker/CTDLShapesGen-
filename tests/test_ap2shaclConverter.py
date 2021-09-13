import pytest
from CTDLAPProcs import AP, PropertyStatement, AP2SHACLConverter, make_property_shape_id
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, SH

schema = Namespace("https://schema.org/")
SDO = Namespace("https://schema.org/")  # "httpS"
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
# stoopid conflict of SH.in with python in
SH_in = URIRef("http://www.w3.org/ns/shacl#in")
expected_triples = []


@pytest.fixture(scope="module")
def name_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:name")
    ps.add_label("en", "Name")
    ps.add_label("es", "Nombre")
    ps.add_valueNodeType("Literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraintType("minLength")
    ps.add_valueConstraint("2")
    ps.add_mandatory(True)
    ps.add_repeatable(True)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#personName_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personName_value"), SH.name, Literal("Name", lang="en")),
            (URIRef("#personName_value"), SH.name, Literal("Nombre", lang="es")),
            (URIRef("#personName_value"), SH.datatype, XSD.string),
            (URIRef("#personName_value"), SH.minLength, Literal(2)),
            (URIRef("#personName_count"), RDF.type, SH.PropertyShape),
            (URIRef("#personName_count"), SH.minCount, Literal(1)),
            (URIRef("#personName_count"), SH.severity, SH.Violation),
            (URIRef("#personName_value"), SH.severity, SH.Violation),
        ]
    )
    return ps


def description_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:description")
    ps.add_valueNodeType("Literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraintType("maxLength")
    ps.add_valueConstraint("1024")
    ps.add_mandatory(False)
    ps.add_repeatable(False)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#personName_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personName_value"), SH.datatype, XSD.string),
            (URIRef("#personName_value"), SH.maxLength, Literal(1024)),
            (URIRef("#personName_count"), RDF.type, SH.PropertyShape),
            (URIRef("#personName_count"), SH.maxCount, Literal(1)),
            (URIRef("#personName_count"), SH.severity, SH.Violation),
            (URIRef("#personName_value"), SH.severity, SH.Violation),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def person_type_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("rdf:type")
    ps.add_label("en", "Type")
    ps.add_mandatory(True)
    ps.add_repeatable(False)
    ps.add_valueNodeType("IRI")
    ps.add_valueConstraint("schema:Person")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#personType_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personType_value"), SH.name, Literal("Type", lang="en")),
            (URIRef("#personType_value"), SH.nodeKind, SH.IRI),
            (URIRef("#personType_value"), SH.hasValue, SDO.Person),
            (URIRef("#personType_count"), RDF.type, SH.PropertyShape),
            (URIRef("#personType_count"), SH.minCount, Literal(1)),
            (URIRef("#personType_count"), SH.maxCount, Literal(1)),
            (URIRef("#personType_count"), SH.severity, SH.Violation),
            (URIRef("#personType_value"), SH.severity, SH.Violation),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def address_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:address")
    ps.add_label("en", "Address")
    ps.add_mandatory(False)
    ps.add_repeatable(True)
    ps.add_valueNodeType("IRI")
    ps.add_valueNodeType("BNode")
    ps.add_valueShape("#Address")
    ps.add_severity("Warning")
    expected_triples.extend(
        [
            (URIRef("#personAddress_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personAddress_value"), SH.name, Literal("Address", lang="en")),
            (URIRef("#personAddress_value"), SH.nodeKind, SH.BlankNodeOrIRI),
            (URIRef("#personAddress_value"), SH.node, URIRef("#Address")),
            (URIRef("#personAddress_value"), SH.severity, SH.Warning),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def address_type_ps():
    ps = PropertyStatement()
    ps.add_shape("#Address")
    ps.add_property("rdf:type")
    ps.add_label("en", "Type")
    ps.add_mandatory(True)
    ps.add_repeatable(False)
    ps.add_valueNodeType("IRI")
    ps.add_valueConstraint("schema:Address")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#addressType_value"), RDF.type, SH.PropertyShape),
            (URIRef("#addressType_value"), SH.name, Literal("Type", lang="en")),
            (URIRef("#addressType_value"), SH.nodeKind, SH.IRI),
            (URIRef("#addressType_value"), SH.hasValue, SDO.Address),
            (URIRef("#addressType_count"), RDF.type, SH.PropertyShape),
            (URIRef("#addressType_count"), SH.minCount, Literal(1)),
            (URIRef("#addressType_count"), SH.maxCount, Literal(1)),
            (URIRef("#addressType_count"), SH.severity, SH.Violation),
            (URIRef("#addressType_value"), SH.severity, SH.Violation),
        ]
    )
    return ps

@pytest.fixture(scope="module")
def address_option_ps():
    ps = PropertyStatement()
    ps.add_shape("#Address")
    ps.add_property("rdf:type")
    ps.add_label("en", "Contact Option")
    ps.add_mandatory(False)
    ps.add_repeatable(True)
    ps.add_valueNodeType("IRI")
    ps.add_valueConstraint("schema:HearingImpairedSupported")
    ps.add_valueConstraint("schema:TollFree")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#addressOption_value"), RDF.type, SH.PropertyShape),
            (URIRef("#addressOption_value"), SH.name, Literal("Contact Option", lang="en")),
            (URIRef("#addressOption_value"), SH.nodeKind, SH.IRI),
            (URIRef("#addressOption_value"), SH_in, SDO.HearingImpairedSupported),
            (URIRef("#addressOption_value"), SH_in, SDO.TollFree),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def person_shapeInfo():
    shapeInfo = {
        "label": "Person shape",
        "comment": "A shape for tests",
        "target": "schema:Person",
        "targetType": "class",
        "mandatory": True,
        "severity": "Warning",
        "properties": ["name", "address", "description"],
    }
    expected_triples.extend(
        [
            (URIRef("#Person"), RDF.type, SH.NodeShape),
            (URIRef("#Person"), SH.name, Literal("Person shape")),
            (URIRef("#Person"), SH.description, Literal("A shape for tests")),
            (URIRef("#Person"), SH.targetClass, schema.Person),
        ]
    )
    return shapeInfo


@pytest.fixture(scope="module")
def address_shapeInfo():
    shapeInfo = {
        "label": "Address shape",
        "comment": "A shape for tests",
        "target": "schema:address",
        "targetType": "ObjectsOf",
        "mandatory": False,
        "severity": "Warning",
        "properties": [],
    }
    expected_triples.extend(
        [
            (URIRef("#Address"), RDF.type, SH.NodeShape),
            (URIRef("#Address"), SH.name, Literal("Address shape")),
            (URIRef("#Address"), SH.description, Literal("A shape for tests")),
            (URIRef("#Address"), SH.targetObjectsOf, SDO.address),
        ]
    )
    return shapeInfo


@pytest.fixture(scope="module")
def simple_ap(
    person_shapeInfo,
    name_ps,
    person_type_ps,
    address_ps,
    address_shapeInfo,
    address_type_ps,
    address_option_ps
):
    ap = AP()
    ap.load_namespaces("InputData/namespaces.csv")
    ap.add_metadata("dct:title", "Test application profile")
    ap.add_metadata("dct:date", "2021-08-09")
    ap.add_shapeInfo("#Person", person_shapeInfo)
    ap.add_propertyStatement(person_type_ps)
    ap.add_propertyStatement(name_ps)
    ap.add_propertyStatement(address_ps)
    ap.add_shapeInfo("#Address", address_shapeInfo)
    ap.add_propertyStatement(address_type_ps)
    ap.add_propertyStatement(address_option_ps)

    return ap


def test_make_property_shape_id():
    ps = PropertyStatement()
    id = make_property_shape_id(ps)
    assert type(id) == URIRef
    ps.add_label("fr", "Coleur")
    id = make_property_shape_id(ps)
    assert id == URIRef("#_Coleur")
    ps.add_label("en-US", "Color Property")
    id = make_property_shape_id(ps)
    assert id == URIRef("#_ColorProperty")
    ps.add_label("en", "Colour Property")
    id = make_property_shape_id(ps)
    assert id == URIRef("#_ColourProperty")


def test_ap2shaclInit(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    converter.dump_shacl()
    assert type(converter.ap) == AP
    assert converter.ap.metadata["dct:title"] == "Test application profile"
    assert "dct" in converter.ap.namespaces.keys()
    assert "rdf" in converter.ap.namespaces.keys()
    assert "sh" in converter.ap.namespaces.keys()
    assert len(converter.ap.propertyStatements) == 4
    assert len(converter.ap.shapeInfo) == 2
    assert type(converter.sg) == Graph
    all_ns = [n for n in converter.sg.namespace_manager.namespaces()]
    assert ("schema", URIRef("https://schema.org/")) in all_ns
    assert ("sh", URIRef("http://www.w3.org/ns/shacl#")) in all_ns
    for t in expected_triples:
        assert t in converter.sg
    assert False
