from AP import AP, PropertyStatement
from csv import DictReader
from .readAPJSON import readJSONFile


class CE2APConverter:
    """Class comprising AP and Cred Engine JSON data, and with methods to convert latter to former."""

    def __init__(self, fname):
        self.ap = AP()
        # need to hard-code some info not in AP data
        self.dont_repeat = [
            "ceterms:ctid",
            "ceterms:name",
            "ceterms:description",
            "ceterms:subjectWebpage",
        ]
        self.load_CE_APs(fname)

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
                elif p["PropertyURIs"] == [class_data["URI"]]:
                    # used to indicate need rdf:type
                    # to do: check it is always for class URI of top level shape
                    #        ... could be any class URI
                    if len(p["PropertyURIs"]) == 1:
                        self.build_ps_type_constraint(p["PropertyURIs"][0], ps)
                    else:
                        # to do: what is required for choice of types
                        pass
                else:
                    self.build_ps_constraints(p, ps)
                self.ap.add_propertyStatement(ps)

    def build_ps_type_constraint(self, class_uri, ps):
        """Add constraint that rdf:type must be uri provided."""
        ps.add_property("rdf:type")
        ps.add_mandatory(True)
        ps.add_repeatable(False)
        ps.add_valueNodeType("IRI")
        ps.add_valueConstraint(class_uri)

    def build_ps_constraints(self, p, ps):
        """Compute and add contraints to property statement ps"""
        prop_uri = p["PropertyURIs"][0]
        ps.add_property(prop_uri)
        ps.add_mandatory(True)
        if prop_uri in self.dont_repeat:
            ps.add_repeatable(False)
        else:
            ps.add_repeatable(True)
        range = self.findRange(prop_uri)
        for class_uri in range:
            (
                valueNodeTypes,
                valueDataTypes,
                valueShape,
                valueConstraint,
                valueConstraintType,
            ) = self.processRange(class_uri, prop_uri)
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

    def findRange(self, uri):
        """Return range of property with uri as a list."""
        for propData in self.ce_AP_data["PropertyData"]:
            if uri == propData["URI"]:
                return propData["Range"]
        return []  # sometimes what is listed in the PropertyData is the type

    def processRange(self, r_uri, p_uri):
        """Return value constraints for property p based on range uri."""
        prefix, name = r_uri.split(":")
        #        print("debug: processRange found prefix: ", prefix)
        if prefix == "xsd" or r_uri == "rdf:langString":
            # range is a literal type
            valueNodeTypes = ["Literal"]
            valueDataTypes = [r_uri]
            valueShape = None
            valueConstraint = None
            valueConstraintType = None
        elif prefix == "ceterms":  # need to process non-literal
            valueShape = "#" + name
            valueNodeTypes = ["IRI", "BNode"]
            valueDataTypes = None
            valueConstraint = None
            valueConstraintType = None
            self.createSecondaryShape(valueShape, r_uri, p_uri)
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


# def tap2AP(fname):
# idea: convert data from TAP to an AP object
