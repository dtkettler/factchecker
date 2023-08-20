import xml.etree.ElementTree as ET
import json
import string
from pinecone_db import PineconeDB


#tree = ET.parse("fact_checks_20190605.txt")
#root = tree.getroot()

pcdb = PineconeDB()
with open("../fact_checks_20190605.txt") as f:
    lines = f.readlines()

    num_errors = 0
    num_success = 0
    for line in lines:
        try:
            xml_root = ET.fromstring(line)

            json_data = json.loads(xml_root.text)

            # print(json_data["url"])
            # print(json_data["claimReviewed"])
            claim = json_data["claimReviewed"].translate(str.maketrans('', '', string.punctuation))
            # print(claim)

            pcdb.add_strings([claim], json_data["url"])

            num_success += 1
        except Exception as e:
            print(e)
            num_errors += 1


print("{} entries successfully uploaded and {} errors".format(num_success, num_errors))

