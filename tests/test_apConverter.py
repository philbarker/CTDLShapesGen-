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
    ap = converter.ap
    assert ap.metadata["dc:title"] == "Apprenticeship Certificate Requirements"
    assert (
        ap.metadata["dc:description"][0:42]
        == "Required Properties for Credential earned "
    )
    shInfo = ap.shapeInfo["#ApprenticeshipCertificate"]
    assert shInfo["targetType"] == "sh:Class"
    assert shInfo["mandatory"] == True
    assert shInfo["target"] == "ceterms:ApprenticeshipCertificate"
    assert shInfo["properties"] == []
    expected_props = [
        ["ceterms:credentialStatusType"],
        ["ceterms:ctid"],
        ["ceterms:description"],
        ["ceterms:inLanguage"],
        ["ceterms:name"],
        ["ceterms:subjectWebpage"],
        ["rdf:type"],
        [],
    ]
    assert len(ap.propertyStatements) == len(expected_props)
    props_found = []
    for ps in ap.propertyStatements:
        assert ps.properties in expected_props
        props_found.append(ps.properties)
        # pick some for further tests
        if ps.properties == ["ceterms:description"]:
            assert ps.shapes == ["#ApprenticeshipCertificate"]
            assert ps.labels == {"en-US": "Description"}
            assert ps.mandatory == True
            assert ps.repeatable == False
            assert ps.valueNodeTypes == ["Literal"]
            assert ps.valueDataTypes == ["rdf:langString"]
            assert ps.valueShapes == []
            assert ps.severity == "Violation"
        elif ps.properties == ["ceterms:credentialStatusType"]:
            assert ps.shapes == ["#ApprenticeshipCertificate"]
            assert ps.labels == {"en-US": "Credential Status Type"}
            assert ps.mandatory == True
            assert ps.repeatable == True
            assert ps.valueNodeTypes == ["IRI", "BNode"]
            assert ps.valueDataTypes == []
            assert ps.valueShapes == ["#CredentialAlignmentObject"]
            assert ps.severity == "Violation"
        elif ps.properties == ["ceterms:ctid"]:
            assert ps.shapes == ["#ApprenticeshipCertificate"]
            assert ps.labels == {"en-US": "CTID"}
            assert ps.mandatory == True
            assert ps.repeatable == False
            assert ps.valueNodeTypes == ["Literal"]
            assert ps.valueDataTypes == ["xsd:string"]
            assert ps.valueShapes == []
            assert ps.severity == "Violation"
    for p in props_found:
        # check we didn't get an props we shouldn't
        assert p in expected_props


def test_load_namespaces(converter):
    converter.ap.load_namespaces("InputData/namespaces.csv")
    assert converter.ap.namespaces["ceterms:"] == "https://purl.org/ctdl/terms/"
