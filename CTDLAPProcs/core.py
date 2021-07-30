from dataclasses import dataclass, field, asdict
import pprint


@dataclass
class AP:
    """Data to define an Application Profile."""

    propertyStatements: list = field(default_factory=list)
    namespaces: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    shapeInfo: dict = field(default_factory=dict)

    def add_namespace(self, ns, uri):
        """Adds (over-writes) the ns: URI, key value pair to the namespaces dict."""
        if (type(ns) == str) and (type(uri) == str):
            self.namespaces[ns] = uri
        else:
            msg = "Both ns and URI must be strings."
            raise TypeError(msg)
        return

    def add_metadata(self, prop, value):
        """Adds (over-writes) the ns: URI, key value pair to the namespaces dict."""
        if (type(prop) == str) and (type(value) == str):
            self.metadata[prop] = value
        else:
            msg = "Both ns and URI must be strings."
            raise TypeError(msg)
        return

    def add_shapeInfo(self, sh, value):
        """Adds (over-writes) the shape info to the shape dict."""
        if (type(sh) == str) and (type(value) == dict):
            self.shapeInfo[sh] = value
        elif type(value) != dict:
            msg = "Shape info must be a dictionary."
            raise TypeError(msg)
        return

    def add_propertyStatement(self, ps):
        """Adds PropertyStatement object to the list of property statements."""
        if ps in self.propertyStatements:
            pass
        elif type(ps) == PropertyStatement:
            self.propertyStatements.append(ps)
        else:
            msg = "Statement must be of PropertyStatement type."
            raise TypeError(msg)

    def dump(self):
        """Print all the AP data."""
        pp = pprint.PrettyPrinter(indent=2)
        print("\n\n=== Metadata ===")
        pp.pprint(self.metadata)
        print("\n\n=== Namespaces ===")
        pp.pprint(self.namespaces)
        print("\n\n=== Shapes ===")
        pp.pprint(self.shapeInfo)
        print("\n\n=== propertyStatements ===")
        pp.pprint(self.propertyStatements)
        return


@dataclass
class PropertyStatement:
    """Data to define a Property Statement."""

    shapes: list = field(default_factory=list)
    properties: list = field(default_factory=list)
    labels: dict = field(default_factory=dict)
    mandatory: bool = False
    repeatable: bool = True
    valueNodeTypes: list = field(default_factory=list)
    valueDataTypes: list = field(default_factory=list)
    valueShapes: list = field(default_factory=list)
    notes: dict = field(default_factory=dict)
    severity: str = ""

    def add_property(self, propertyID):
        """Append propertyID to class properties list"""

        if type(propertyID) == str:
            if propertyID in self.properties:
                pass
            else:
                self.properties.append(propertyID)
        else:
            msg = "Property identifier must be a string."
            raise TypeError(msg)

    def add_shape(self, shapeID):
        """Append propertyID to class properties list"""

        if type(shapeID) == str:
            if shapeID in self.shapes:
                pass
            else:
                self.shapes.append(shapeID)
        else:
            msg = "Shape identifier must be a string."
            raise TypeError(msg)

    def add_label(self, lang, label):
        """Append {lang: label} to labels dict."""

        if (type(lang) == str) and (type(label) == str):
            self.labels[lang] = label
        else:
            msg = "Language identifier and label must be strings."
            raise TypeError(msg)

    def add_mandatory(self, man):
        """Set boolean value of mandatory to man."""
        if type(man) == bool:
            self.mandatory = man
        else:
            msg = "Mandatory must be set as boolean."
            raise TypeError(msg)

    def add_repeatable(self, rpt):
        """Set boolean value of repeatable to rpt."""
        if type(rpt) == bool:
            self.repeatable = rpt
        else:
            msg = "Repeatable must be set as boolean."
            raise TypeError(msg)

    def add_valueNodeType(self, vNT):
        """Append vNT to class valueNodeTypes list"""
        if type(vNT) == str:
            if vNT in self.valueNodeTypes:
                pass
            else:
                self.valueNodeTypes.append(vNT)
        else:
            msg = "Value node type must be a string."
            raise TypeError(msg)

    def add_valueDataType(self, vDT):
        """Append vDT to class valueDataTypes list"""
        if type(vDT) == str:
            if vDT in self.valueDataTypes:
                pass
            else:
                self.valueDataTypes.append(vDT)
        else:
            msg = "Value data type must be a string."
            raise TypeError(msg)

    def add_valueShape(self, shapeID):
        """Append shapeID to class valueShapes list"""
        if type(shapeID) == str:
            if shapeID in self.valueShapes:
                pass
            else:
                self.valueShapes.append(shapeID)
        else:
            msg = "Value data type must be a string."
            raise TypeError(msg)

    def add_note(self, lang, note):
        """Append {lang: note} to notes dict."""
        if (type(lang) == str) and (type(note) == str):
            self.notes[lang] = note
        else:
            msg = "Language identifier and note must be strings."
            raise TypeError(msg)

    def add_severity(self, s):
        if type(s) == str:
            self.severity = s
        else:
            msg = "Severity value must be a string."
            raise TypeError(msg)
