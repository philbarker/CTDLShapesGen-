import pytest
from CTDLAPProcs import AP, PropertyStatement, AP2SHACLConverter


@pytest.fixture(scope="module")
def simple_ap():
    ap = AP()
    ap.load_namespaces("InputData/namespaces.csv")
    ap.add_metadata("dct:title", "Test application profile")
    ap.add_metadata("dct:date", "2021-08-09")
    p_shapeInfo = {
        "label": "Person shape",
        "comment": "Just a shape for tests",
        "target": "schema:Person",
        "targetType": "class",
        "mandatory": True,
        "severity": "Warning",
        "properties": ["name", "address"],
    }
    ap.add_shapeInfo("#Person", p_shapeInfo)
    p_type_ps = PropertyStatement()
    p_type_ps.add_shape("#Person")
    p_type_ps.add_property("rdf:type")
    p_type_ps.add_label("en", "Type")
    p_type_ps.add_mandatory(True)
    p_type_ps.add_repeatable(False)
    p_type_ps.add_valueNodeType("IRI")
    p_type_ps.add_valueConstraint("schema:Person")
    p_type_ps.add_severity("Violation")
    ap.add_propertyStatement(p_type_ps)
    name_ps = PropertyStatement()
    name_ps.add_shape("#Person")
    name_ps.add_property("schema:name")
    name_ps.add_label("en", "Name")
    name_ps.add_mandatory(True)
    name_ps.add_repeatable(False)
    name_ps.add_valueNodeType("Literal")
    name_ps.add_valueDataType("xsd:string")
    name_ps.add_severity("Violation")
    ap.add_propertyStatement(name_ps)
    address_ps = PropertyStatement()
    address_ps.add_shape("#Person")
    address_ps.add_property("schema:address")
    address_ps.add_label("en", "Address")
    address_ps.add_mandatory(False)
    address_ps.add_repeatable(True)
    address_ps.add_valueNodeType("IRI")
    address_ps.add_valueNodeType("BNode")
    address_ps.add_valueShape("#Address")
    address_ps.add_severity("Warning")
    ap.add_propertyStatement(address_ps)
    a_shapeInfo = {
        "label": "Address shape",
        "comment": "Just a shape for tests",
        "target": "schema:address",
        "targetType": "ObjectsOf",
        "mandatory": False,
        "severity": "Warning",
        "properties": [],
    }
    ap.add_shapeInfo("#Address", a_shapeInfo)
    a_type_ps = PropertyStatement()
    a_type_ps.add_shape("#Address")
    a_type_ps.add_property("rdf:type")
    a_type_ps.add_label("en", "Type")
    a_type_ps.add_mandatory(True)
    a_type_ps.add_repeatable(False)
    a_type_ps.add_valueNodeType("IRI")
    a_type_ps.add_valueConstraint("schema:Address")
    a_type_ps.add_severity("Violation")
    ap.add_propertyStatement(a_type_ps)

    return ap


def test_ap2shaclInit(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    assert converter.ap
    assert converter.ap.metadata["dct:title"] == "Test application profile"
    assert "dct" in converter.ap.namespaces.keys()
    assert "rdf" in converter.ap.namespaces.keys()
    assert "sh" in converter.ap.namespaces.keys()
    assert len(converter.ap.propertyStatements) == 4
    assert len(converter.ap.shapeInfo) == 2
