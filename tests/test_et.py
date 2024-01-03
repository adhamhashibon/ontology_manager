import xml.etree.ElementTree as ET
tree = ET.parse('country_data.xml')
root = tree.getroot()


# or root = ET.fromstring(country_data_as_string)

print("root.tag=", root.tag)
print("root.attrib=", root.attrib)

print("# iterating root\n")

for child in root:
    print (child.tag, child.attrib)

print("# iterating recursicely on the neighbor jey")
for neighbor in root.iter('neighbor'):
    print(neighbor.attrib)

print("# iterating recursicely on the country jey")
for country in root.iter('country'):
    print(country.attrib)

# Element.findall() finds only elements with a tag which are direct children of the current element. Element.find() finds the first child with a particular tag, and Element.text accesses the element’s text content. Element.get() accesses the element’s attributes:

print("# Element.findall(): elements of a tag")
for country in root.findall('country'):
    rank =     country.find('rank').text
    name =     country.get('name')
    year =     country.find('year').text

    print(name, rank, year)
