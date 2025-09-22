import json
import pandas as pd

# with open("script.json","r") as file:
#     data = json.load(file)
#     for student in data:
#         print("roll no",student["roll no"])

df = pd.read_json("script.json")
print(df)



dn = pd.json_normalize(df["Student"]) 
print(dn)

# df = pd.DataFrame('Student')
# print(df.to_string(index=False))
