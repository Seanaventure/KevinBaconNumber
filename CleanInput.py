import json


cleanfile = open("cleaninput.json", 'w', encoding="utf8")
with(open("person_ids_04_28_2017.json", encoding="utf8")) as file:
    for line in file:
        lineJson = json.loads(line)
        var = lineJson["popularity"]
        if var >= 1:
            cleanfile.write(line)
