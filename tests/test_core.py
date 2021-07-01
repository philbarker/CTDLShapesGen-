import pytest
from CTDLAPProcs import AP

@pytest.fixture(scope="function")
def empty_AP():
    ap = AP()
    return ap

def test_init_defaults(empty_AP):
    assert empty_AP
    assert empty_AP.metadata == {}
    assert empty_AP.namespaces == {}
    assert empty_AP.shapeInfo == {}
    assert empty_AP.propertyStatements == []

def test_add_namespace(empty_AP):
    ap = empty_AP
    ap.add_namespace("dct", "http://purl.org/dc/terms/")
    ap.add_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    assert ap.namespaces["dct"] == "http://purl.org/dc/terms/"
    assert ap.namespaces["rdf"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    with pytest.raises(TypeError):
        ap.add_namespace(27, "http://purl.org/dc/terms/")
    with pytest.raises(TypeError) as e:
        ap.add_namespace("dct", ["http://purl.org/dc/terms/"])
    assert str(e.value) == "Both ns and URI must be strings."

def test_add_metadata(empty_AP):
    ap = empty_AP
    ap.add_metadata("dct:title", "this is the title")
    ap.add_metadata("dct:date", "2021-07-01")
    assert ap.metadata["dct:title"] == "this is the title"
    assert ap.metadata["dct:date"] == "2021-07-01"
    with pytest.raises(TypeError) as e:
        ap.add_namespace("dct:title", 22)
    assert str(e.value) == "Both ns and URI must be strings."

def test_add_shapeInfo(empty_AP):
    #not fully testing this b/c I suspect shall use dataclass not dict for shapeInfo
    ap = empty_AP
    shapeInfo = {
        "label": "test shape",
        "comment": "just a shape for tests",
        "target": "Person",
        "targetType": "class",
        "mandatory": False,
        "severity": "Warning",
        "properties": ["p1", "p2"]
    }
    ap.add_shapeInfo("sh1", shapeInfo)
    assert ap.shapeInfo["sh1"]["label"] == "test shape"
    with pytest.raises(TypeError) as e:
        ap.add_shapeInfo("sh1", "just the label")
    assert str(e.value) == "Shape info must be a dictionary."
