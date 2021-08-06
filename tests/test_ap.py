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

def test_load_namespaces(test_AP):
    ap = test_AP
    ns_file = "InputData/namespaces.csv"
    ap.load_namespaces(ns_file)
    assert ap.namespaces["ceterms:"] == "https://purl.org/ctdl/terms/"


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
