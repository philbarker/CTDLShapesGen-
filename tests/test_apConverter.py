import pytest
from CTDLAPProcs import APConverter, readJSONFile

@pytest.fixture(scope="module")
def converter():
    converter = APConverter()
    return converter


def test_readJSONFile():
    ap_data = readJSONFile("InputData/policyBrowserData.json")
    assert len(ap_data["RawShapes"]) == 42
    assert ap_data["RawShapes"][0]["ClassURI"] == "ceterms:ApprenticeshipCertificate"

def test_initAP(converter):
    assert converter
    assert converter.metadata == {}
    assert converter.namespaces == {}
    assert converter.shapeInfo == {}
    assert converter.propertyStatements == []

def test_load_JSON_AP(converter):
    converter.load_json_AP("InputData/policyBrowserData.json")
    shInfo = converter.shapeInfo
    assert len(shInfo) == 42
    assert shInfo["#ApprenticeshipCertificate"]["targetType"] == "sh:NodeShape"
    assert shInfo["#ApprenticeshipCertificate"]["target"] == "ceterms:ApprenticeshipCertificate"
    assert "ceterms:credentialStatusType" in shInfo["#ApprenticeshipCertificate"]["properties"]

def test_load_namespaces(converter):
    converter.load_namespaces("InputData/namespaces.csv")
    assert converter.namespaces["ceterms:"] == "https://purl.org/ctdl/terms/"
