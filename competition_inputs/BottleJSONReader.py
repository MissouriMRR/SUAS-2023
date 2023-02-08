import json
# G J 2-7-2023
# Opens and imports JSON File 'BottleJSON.json' as a list
f = open('competition_inputs/BottleJSON.json')
data=json.load(f)

# Defines Array of Bottles from the list from the JSON file
Bottles=[data['Bottle1'][0], data['Bottle2'][0], data['Bottle3'][0], data['Bottle4'][0], data['Bottle5'][0]]

# Closes the Json File
f.close()