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
    assert converter.ap
    assert converter.ap.metadata == {}
    assert converter.ap.namespaces == {}
    assert converter.ap.shapeInfo == {}
    assert converter.ap.propertyStatements == []


def test_load_CE_APs(converter):
    converter.load_CE_APs("InputData/policyBrowserData.json")
    ce_AP_data = converter.ce_AP_data
    assert len(ce_AP_data["RawShapes"]) == 42
    assert ce_AP_data["RawShapes"][0]["ClassURI"] == "ceterms:ApprenticeshipCertificate"


def test_convert_CE_AP(converter):
    class_data = converter.ce_AP_data["Policy"]["Classes"][0]
    converter.convert_CE_AP(class_data)
    assert converter.ap.metadata["dc:title"] == "Apprenticeship Certificate Requirements"
    assert (
        converter.ap.metadata["dc:description"][0:42]
        == "Required Properties for Credential earned "
    )
    shInfo = converter.ap.shapeInfo["#ApprenticeshipCertificate"]
    assert shInfo["targetType"] == "sh:Class"
    assert shInfo["mandatory"] == True
    assert shInfo["target"] == "ceterms:ApprenticeshipCertificate"
    assert shInfo["properties"] == []



def test_load_namespaces(converter):
    converter.load_namespaces("InputData/namespaces.csv")
    assert converter.ap.namespaces["ceterms:"] == "https://purl.org/ctdl/terms/"
