"""
Convert Google Cloud Platform log in json to postgresql log
"""
import ijson
import os


def get_psql_log_from_gcp_json(gcp_json_file):
    """
    ijson is a module that will work with JSON as a stream.
    Here doc: https://pypi.org/project/ijson/#lower-level-interfaces
    Check if value is textPayload, because next item is textPayload value
    gcp_json_file: full path of json log
    """

    is_textpayload = False
    with open(gcp_json_file) as fjson, open("postgresql.log", "a") as log:
        for prefix, the_type, value in ijson.parse(fjson, multiple_values=True):
            if is_textpayload:
                log.write("%s\n" % value)
                is_textpayload = False

            is_textpayload = value == "textPayload"
