import pytest
from CTDLAPProcs import AP, PropertyStatement, AP2SHACLConverter, make_property_shape_id
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, SH

schema = Namespace("https://schema.org/")


@pytest.fixture(scope="module")
def name_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:name")
    ps.add_label("en", "Name")
    ps.add_label("es", "Nombre")
    ps.add_mandatory(True)
    ps.add_repeatable(True)
    ps.add_valueNodeType("Literal")
    ps.add_valueDataType("xsd:string")
    ps.add_severity("Violation")
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
    return ps


@pytest.fixture(scope="module")
def person_shapeInfo():
    shapeInfo = {
        "label": "Person shape",
        "comment": "Just a shape for tests",
        "target": "schema:Person",
        "targetType": "class",
        "mandatory": True,
        "severity": "Warning",
        "properties": ["name", "address"],
    }
    return shapeInfo


@pytest.fixture(scope="module")
def address_shapeInfo():
    shapeInfo = {
        "label": "Address shape",
        "comment": "Just a shape for tests",
        "target": "schema:address",
        "targetType": "ObjectsOf",
        "mandatory": False,
        "severity": "Warning",
        "properties": [],
    }
    return shapeInfo


@pytest.fixture(scope="module")
def simple_ap(
    person_shapeInfo,
    name_ps,
    person_type_ps,
    address_ps,
    address_shapeInfo,
    address_type_ps,
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
    expected_triples = [
        (URIRef("#Person"), RDF.type, SH.NodeShape),
        (URIRef("#Person"), RDFS.label, Literal("Person shape")),
        (URIRef("#Person"), RDFS.comment, Literal("Just a shape for tests")),
        (URIRef("#Person"), SH.targetClass, schema.Person),
        (URIRef("#Address"), RDF.type, SH.NodeShape),
        (URIRef("#Address"), RDFS.label, Literal("Address shape")),
        (URIRef("#Address"), RDFS.comment, Literal("Just a shape for tests")),
        (URIRef("#Address"), SH.targetObjectsOf, schema.address),
    ]
    for t in expected_triples:
        assert t in converter.sg
    assert False


# assert False
