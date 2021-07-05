import pytest
from CTDLAPProcs import AP, PropertyStatement


@pytest.fixture(scope="module")
def test_AP():
    ap = AP()
    return ap


@pytest.fixture(scope="module")
def test_PropertyStatement():
    ps = PropertyStatement()
    return ps


def test_init_defaults(test_AP):
    assert test_AP
    assert test_AP.metadata == {}
    assert test_AP.namespaces == {}
    assert test_AP.shapeInfo == {}
    assert test_AP.propertyStatements == []


def test_add_namespace(test_AP):
    ap = test_AP
    ap.add_namespace("dct", "http://purl.org/dc/terms/")
    ap.add_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    assert ap.namespaces["dct"] == "http://purl.org/dc/terms/"
    assert ap.namespaces["rdf"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    with pytest.raises(TypeError):
        ap.add_namespace(27, "http://purl.org/dc/terms/")
    with pytest.raises(TypeError) as e:
        ap.add_namespace("dct", ["http://purl.org/dc/terms/"])
    assert str(e.value) == "Both ns and URI must be strings."


def test_add_metadata(test_AP):
    ap = test_AP
    ap.add_metadata("dct:title", "this is the title")
    ap.add_metadata("dct:date", "2021-07-01")
    assert ap.metadata["dct:title"] == "this is the title"
    assert ap.metadata["dct:date"] == "2021-07-01"
    with pytest.raises(TypeError) as e:
        ap.add_namespace("dct:title", 22)
    assert str(e.value) == "Both ns and URI must be strings."


def test_add_shapeInfo(test_AP):
    # not fully testing this b/c I suspect shall use dataclass not dict for shapeInfo
    ap = test_AP
    shapeInfo = {
        "label": "test shape",
        "comment": "just a shape for tests",
        "target": "Person",
        "targetType": "class",
        "mandatory": False,
        "severity": "Warning",
        "properties": ["p1", "p2"],
    }
    ap.add_shapeInfo("sh1", shapeInfo)
    assert ap.shapeInfo["sh1"]["label"] == "test shape"
    with pytest.raises(TypeError) as e:
        ap.add_shapeInfo("sh1", "just the label")
    assert str(e.value) == "Shape info must be a dictionary."


def test_init_defaults(test_PropertyStatement):
    assert test_PropertyStatement
    assert test_PropertyStatement.shapes == []
    assert test_PropertyStatement.labels == {}
    assert test_PropertyStatement.properties == []
    assert test_PropertyStatement.mandatory == False
    assert test_PropertyStatement.repeatable == True
    assert test_PropertyStatement.valueNodeTypes == []
    assert test_PropertyStatement.valueDataTypes == []
    assert test_PropertyStatement.valueShapes == []
    assert test_PropertyStatement.notes == {}


def test_add_property(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_property("dct:description")
    assert ps.properties == ["dct:description"]
    ps.add_property("dct:title")
    assert ps.properties == ["dct:description", "dct:title"]
    ps.add_property("dct:title")  # don't list same prop twice
    assert ps.properties == ["dct:description", "dct:title"]
    with pytest.raises(TypeError) as e:
        ps.add_property(["sdo:description", "sdo:name"])
    assert str(e.value) == "Property identifier must be a string."
    assert ps.properties == ["dct:description", "dct:title"]  # unchanged


def test_add_shape(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_shape("aShapeID")
    assert ps.shapes == ["aShapeID"]
    ps.add_shape("anotherShapeID")
    assert ps.shapes == ["aShapeID", "anotherShapeID"]
    ps.add_shape("anotherShapeID")  # don't list same shape twice
    assert ps.shapes == ["aShapeID", "anotherShapeID"]
    with pytest.raises(TypeError) as e:
        ps.add_shape(["ShapeID", "ShapeID2"])
    assert str(e.value) == "Shape identifier must be a string."
    assert ps.shapes == ["aShapeID", "anotherShapeID"]  # unchanged


def test_add_label(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_label("en", "aLabel")
    assert ps.labels == {"en": "aLabel"}
    ps.add_label("es", "unaEtiqueta")
    assert ps.labels == {"en": "aLabel", "es": "unaEtiqueta"}
    ps.add_label("es", "unaEtiqueta")  # don't add same label twice
    assert ps.labels == {"en": "aLabel", "es": "unaEtiqueta"}
    ps.add_label("en", "newLabel")  # replace label
    assert ps.labels == {"en": "newLabel", "es": "unaEtiqueta"}
    with pytest.raises(TypeError) as e:
        ps.add_label({"de": "ein Etikett"}, {"fr": "une étiquette "})
    assert str(e.value) == "Language identifier and label must be strings."
    assert ps.labels == {"en": "newLabel", "es": "unaEtiqueta"}  # unchanged


def test_add_mandatory(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_mandatory(True)
    assert ps.mandatory == True
    ps.add_mandatory(False)
    assert ps.mandatory == False
    with pytest.raises(TypeError) as e:
        ps.add_mandatory("False")
    assert str(e.value) == "Mandatory must be set as boolean."
    assert ps.mandatory == False  # unchanged


def test_add_repeatable(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_repeatable(False)
    assert ps.repeatable == False
    ps.add_repeatable(True)
    assert ps.repeatable == True
    with pytest.raises(TypeError) as e:
        ps.add_repeatable("False")
    assert str(e.value) == "Repeatable must be set as boolean."
    assert ps.repeatable == True  # unchanged


def test_add_valueNodeType(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_valueNodeType("IRI")
    assert ps.valueNodeTypes == ["IRI"]
    ps.add_valueNodeType("Literal")
    assert ps.valueNodeTypes == ["IRI", "Literal"]
    ps.add_valueNodeType("Literal")  # can't add same valueNodeType twice
    assert ps.valueNodeTypes == ["IRI", "Literal"]
    with pytest.raises(TypeError) as e:
        ps.add_valueNodeType(27)
    assert str(e.value) == "Value node type must be a string."
    assert ps.valueNodeTypes == ["IRI", "Literal"]  # unchanged


def test_add_valueDataType(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_valueDataType("xsd:date")
    assert ps.valueDataTypes == ["xsd:date"]
    ps.add_valueDataType("xsd:string")
    assert ps.valueDataTypes == ["xsd:date", "xsd:string"]
    ps.add_valueDataType("xsd:string")  # can't add same valueDataType twice
    assert ps.valueDataTypes == ["xsd:date", "xsd:string"]
    with pytest.raises(TypeError) as e:
        ps.add_valueDataType(27)
    assert str(e.value) == "Value data type must be a string."
    assert ps.valueDataTypes == ["xsd:date", "xsd:string"]  # unchaged


def test_add_valueShape(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_valueShape("aShapeID")
    assert ps.valueShapes == ["aShapeID"]
    ps.add_valueShape("anotherShapeID")
    assert ps.valueShapes == ["aShapeID", "anotherShapeID"]
    ps.add_valueShape("anotherShapeID")  # can't add same shape id twice
    assert ps.valueShapes == ["aShapeID", "anotherShapeID"]
    with pytest.raises(TypeError) as e:
        ps.add_valueShape(["ShapeID1", "ShapeID2"])
    assert str(e.value) == "Value data type must be a string."
    assert ps.valueShapes == ["aShapeID", "anotherShapeID"]


def test_add_note(test_PropertyStatement):
    ps = test_PropertyStatement
    ps.add_note("en", "a note")
    assert ps.notes == {"en": "a note"}
    ps.add_note("es", "una nota")
    assert ps.notes == {"en": "a note", "es": "una nota"}
    ps.add_note("es", "una nota")  # don't add same label twice
    assert ps.notes == {"en": "a note", "es": "una nota"}
    ps.add_note("en", "new note")  # replace label
    assert ps.notes == {"en": "new note", "es": "una nota"}
    with pytest.raises(TypeError) as e:
        ps.add_note({"de": "ein note"}, {"fr": "une remarque"})
    assert str(e.value) == "Language identifier and note must be strings."
    assert ps.notes == {"en": "new note", "es": "una nota"}  # unchanged


def test_add_propertyStatement(test_PropertyStatement, test_AP):
    ap = test_AP
    ps = test_PropertyStatement
    # these fixtures are defined with module scope, so test_PropertyStatement still has properties set when testing them, above
    ap.add_propertyStatement(ps)
    assert ap.propertyStatements[0].properties == ["dct:description", "dct:title"]
    ap.add_propertyStatement(ps)  # don't add same ps twice
    assert len(ap.propertyStatements) == 1
    with pytest.raises(TypeError) as e:
        ap.add_propertyStatement("dct:description")
    assert str(e.value) == "Statement must be of PropertyStatement type."
    assert len(ap.propertyStatements) == 1  # unchanged
    assert ap.propertyStatements[0].properties == ["dct:description", "dct:title"]
