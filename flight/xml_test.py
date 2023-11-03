import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse("flight/camera_test.xml")
root = tree.getroot()

# Define the key you're searching for
search_key = "Item 1"

print(root.items())
# Find the element with the specified key
for item in root.findall("food"):
    print(item.find("name").text)
    name = item.find("name").text
    if name == "Homestyle Breakfast":
        value = item.find("calories").text
        print(f"Key: {name}, Value: {value}")
        break
else:
    print(f"Key '{search_key}' not found in the XML.")
    
"""
<av:X_ScalarWebAPI_DeviceInfo xmlns:av="urn:schemas-sony-com:av">
    <av:X_ScalarWebAPI_Version>1.0</av:X_ScalarWebAPI_Version>
    <av:X_ScalarWebAPI_ServiceList>
        <av:X_ScalarWebAPI_Service>
            <av:X_ScalarWebAPI_ServiceType>guide</av:X_ScalarWebAPI_ServiceType>
            <av:X_ScalarWebAPI_ActionList_URL>http://192.168.122.1:8080/sony</av:X_ScalarWebAPI_ActionList_URL>
        </av:X_ScalarWebAPI_Service>
        <av:X_ScalarWebAPI_Service>
            <av:X_ScalarWebAPI_ServiceType>camera</av:X_ScalarWebAPI_ServiceType>
            <av:X_ScalarWebAPI_ActionList_URL>http://192.168.122.1:8080/sony</av:X_ScalarWebAPI_ActionList_URL>
        </av:X_ScalarWebAPI_Service>
    </av:X_ScalarWebAPI_ServiceList>
</av:X_ScalarWebAPI_DeviceInfo>
"""