from .core import AP
from csv import DictReader
from .readAPJSON import readJSONFile


class APConverter(AP):
    """Application profile with ability to load and write different formats"""

    def __init__(self):
        super().__init__()

    def load_CE_APs(self, fname):
        """Convert data from JSON to an AP object"""
        # ToDo: currently implemented for data from a file, could also implement for data from web if suitable methods to read AP data added to readAPJSON
        json_AP = readJSONFile(fname)
        for shape in json_AP["RawShapes"]:
            sh = "#" + shape["ClassURI"].split(":")[1]
            props = []
            for propertySet in shape["PropertySets"]:
                props.extend(propertySet["PropertyURIs"])
            info = {
                "targetType": "sh:NodeShape",
                "target": shape["ClassURI"],
                "properties": props,
            }
            self.add_shapeInfo(sh, info)

    def load_namespaces(self, fname):
        """Load namespaces from a (csv) file"""
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
