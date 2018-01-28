"""
I downloaded a huge dataset of movie stars from TMBd. It contained a bunch of info, the most important being the id
the actor uses in the API. Problem was it was huge, like 70mb. Luckily it also contained a popularity rating of
the star so I just filtered out anyone with below a 1 because they are irrelevant

1/28/18

Author: Sean Bonaventure
"""

import json


cleanfile = open("cleaninput.json", 'w', encoding="utf8")
with(open("person_ids_04_28_2017.json", encoding="utf8")) as file:
    for line in file:
        lineJson = json.loads(line)
        var = lineJson["popularity"]
        if var >= 1:
            cleanfile.write(line)
