import json


def readJSONFile(fname):
    """Read AP data from a json file and return it as a python object."""
    with open(fname, "r") as json_file:
        json_data = json_file.read()

    ap_data = json.loads(json_data)

    return ap_data
