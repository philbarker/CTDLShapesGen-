from .ap import AP
from .propertyStatement import PropertyStatement
from csv import DictReader
from .readAPJSON import readJSONFile


class APConverter():
    """Application profile with ability to load and write different formats"""

    def __init__(self):
        self.ap = AP()

    def load_CE_APs(self, fname):
        """load CE data from JSON."""
        self.ce_AP_data = readJSONFile(fname)
        self.ce_Primary_Types = []
        for c in self.ce_AP_data["Policy"]["Classes"]:
            self.ce_Primary_Types.append([c["URI"]])

    def convert_CE_AP(self, class_data):
        """Build an AP from the a class in the list ce_AP_data ["Classes"] list"""
        # first, just the Required properties
        # ToDo: factor out functions rptd between req & rec
        # ToDo: serializer to iterate through all the classes
        # ToDo: cases of required, recommended, all properties

        self.ap.add_metadata("dc:title", class_data["Label"] + " Requirements")
        self.ap.add_metadata(
            "dc:description", "Required Properties for " + class_data["Definition"]
        )
        # add the "top level" shape
        top_shape_id = "#" + class_data["Label"].replace(" ", "")
        shape_info = {
            "targetType": "sh:Class",
            "target": class_data["URI"],
            "properties": [],
            "mandatory": True,
        }
        self.ap.add_shapeInfo(top_shape_id, shape_info)
        # add property statements for top level shape
        for p in class_data["PropertySets"]:
            ps = PropertyStatement()
            if p["ImportanceLevel"] == "constraintType:RequiresProperty":
                ps.add_shape(top_shape_id)
                ps.add_label("en-US", p["Label"])
                ps.add_severity("Violation")
                if len(p["PropertyURIs"]) > 1:
                    # do what is needed to get sh:or
                    # for now just let user know
                    # print("PropertyURIs")
                    pass
                else:
                    self.build_ps_constraints(p, ps)
                    self.ap.add_propertyStatement(ps)


    def build_ps_constraints(self, p, ps):
        """Compute and add contraints to property statement ps"""
        # need to hard-code some info not in AP data
        dont_repeat = ["ceterms:ctid", "ceterms:name"]
        uri = p["PropertyURIs"][0]
        ps.add_property(uri)
        ps.add_mandatory(True)
        if uri in dont_repeat:
            ps.add_repeatable(False)
        range = self.findRange(uri)
        for class_uri in range:
            (
                valueNodeTypes,
                valueDataTypes,
                valueShape,
                valueConstraint,
                valueConstraintType,
            ) = self.processRange(class_uri, p)
            if valueNodeTypes:
                for vnt in valueNodeTypes:
                    ps.add_valueNodeType(vnt)
            if valueDataTypes:
                for vdt in valueDataTypes:
                    ps.add_valueDataType(vdt)
            if valueShape:
                ps.add_valueShape(valueShape)
            if valueConstraint:
                ps.add_valueConstraint(valueConstraint)
            if valueConstraintType:
                ps.add_valueConstraintType(valueConstraintType)
        return ps

    def findRange(self, uri):
        """Return range of property with uri as a list."""
        for propData in self.ce_AP_data["PropertyData"]:
            if uri == propData["URI"]:
                return propData["Range"]
        return []  # sometimes what is listed in the PropertyData is the type

    def processRange(self, uri, p):
        """Return value constraints for property p based on range uri."""
        prefix, name = uri.split(":")
        print(prefix)
        if prefix == "xsd" or uri == "rdf:langString":
            # range is a literal type
            valueNodeTypes = ["Literal"]
            valueDataTypes = [uri]
            valueShape = None
            valueConstraint = None
            valueConstraintType = None
        elif prefix == "ceterms":  # need to process non-literal
            valueShape = "#" + name
            valueNodeTypes = ["IRI", "BNode"]
            valueDataTypes = None
            valueConstraint = None
            valueConstraintType = None
            self.createSecondaryShape(valueShape, uri, p)
        return (
            valueNodeTypes,
            valueDataTypes,
            valueShape,
            valueConstraint,
            valueConstraintType,
        )

    def createSecondaryShape(self, shape_id, type, property):
        """Create a shape for objects of property, with type."""
        # if requirements for target node are listed, then need a shape for it
        shape_info = {
            "targetType": "sh:ObjectsOf",
            "target": property,
            "properties": [],
            "mandatory": True,
        }
        self.ap.add_shapeInfo(shape_id, shape_info)
        # that shape should have correct type
        ps = PropertyStatement()
        ps.add_shape(shape_id)
        ps.add_property("rdf:type")
        ps.add_label("en-US", "member of class")
        ps.add_mandatory(True)
        ps.add_repeatable(False)
        ps.add_valueNodeType("IRI")
        ps.add_valueConstraint(type)
        ps.add_severity("Violation")
        if shape_id in self.ce_Primary_Types:
            # will need to add required properties
            # but for now let's see if there are any
            print(property, " has range ", shape_id, " which is primary type.")

    def load_namespaces(self, fname):
        """Load namespaces from a (csv) file."""
        # could add options for loading from other formats
        with open(fname, "r") as csv_file:
            csvReader = DictReader(csv_file)
            for row in csvReader:
                if row["prefix"] and row["URI"]:
                    self.ap.add_namespace(row["prefix"], row["URI"])
                else:  # pass rows with missing data
                    pass


# def tap2AP(fname):
# idea: convert data from TAP to an AP object
