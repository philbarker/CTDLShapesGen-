from .core import AP, PropertyStatement
from csv import DictReader
from .readAPJSON import readJSONFile


class APConverter(AP):
    """Application profile with ability to load and write different formats"""

    def __init__(self):
        super().__init__()

    def load_CE_APs(self, fname):
        """load CE data from JSON."""
        self.ce_AP_data = readJSONFile(fname)
        self.ce_Primary_Types = []
        for c in self.ce_AP_data["Policy"]["Classes"]:
            self.ce_Primary_Types.append([c["URI"]])

    def convert_CE_AP(self, class_data):
        """Build an AP from the a class in the list ce_AP_data ["Classes"] list"""
        # need to hard-code some info not in AP data
        dont_repeat = ["ceterms:ctid", "ceterms:name"]
        # first, just the Required properties
        # ToDo: factor out functions rptd between req & rec
        # ToDo: serializer to iterate through all the classes

        self.add_metadata("dc:title", class_data["Label"] + " Requirements")
        self.add_metadata(
            "dc:description", "Required Properties for " + class_data["Definition"]
        )
        # add the "top level" shape
        top_shape_id = "#" + class_data["Label"].replace(" ", "")
        shape_info = {
            "targetType": "sh:NodeShape",
            "target": class_data["URI"],
            "properties": [],
            "mandatory": True,
        }
        self.add_shapeInfo(top_shape_id, shape_info)
        # add property statements for top level shape
        for p in class_data["PropertySets"]:
            ps = PropertyStatement()
            ps_id = "#" + p["Label"].replace(" ", "")
            if p["ImportanceLevel"] == "constraintType:RequiresProperty":
                ps.add_shape(top_shape_id)
                ps.add_severity("Violation")
                ps.add_repeatable(True)
                if len(p["PropertyURIs"]) > 1:
                    # do what is needed to get sh:or
                    pass
                else:
                    uri = p["PropertyURIs"][0]
                    ps.add_property(uri)
                    ps.add_mandatory(True)
                    if uri in dont_repeat:
                        ps.add_repeatable(False)
                    range = self.findRange(uri)
                    for uri in range:
                        y = self.processRange(range, p)

                ps.add_label("en-US", p["Label"])

    #    valueNodeTypes: list = field(default_factory=list)
    #    valueDataTypes: list = field(default_factory=list)
    #    valueShapes: list = field(default_factory=list)
    #    notes: dict = field(default_factory=dict)

    def findRange(self, uri):
        """Return range of property with uri as a list."""
        for propData in self.ce_AP_data["PropertyData"]:
            if uri == propData["URI"]:
                return propData["Range"]
            return []  # sometimes what is listed in the PropertyData is the type

    def processRange(self, uri, p):
        """Return value constraints for property p based on range uri."""
        prefix, name = uri.split(":")
        if prefix == "xsd" or uri == "rdf:langString":
            # range is a literal type
            valueNodeTypes = ["Literal"]
            valueDataTypes = [uri]
            valueShape = None
        elif prefix == "ceterms":  # need to process non-literal
            if uri in self.ce_Primary_Types:
                valueNodeTypes = ["IRI"]
                self.createSecondaryShape(uri, p)
            else:
                valueNodeTypes = ["IRI", "BNode"]

    def createSecondaryShape(self, uri, targetOf):
        """Create a target Node shape."""
        pass

    def load_namespaces(self, fname):
        """Load namespaces from a (csv) file."""
        # could add options for loading from other formats
        with open(fname, "r") as csv_file:
            csvReader = DictReader(csv_file)
            for row in csvReader:
                if row["prefix"] and row["URI"]:
                    self.add_namespace(row["prefix"], row["URI"])
                else:  # pass rows with missing data
                    pass


# def tap2AP(fname):
# idea: convert data from TAP to an AP object
