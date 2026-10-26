import xml.etree.ElementTree as ET

# Open original file
file = f"D:\\Anderson\\Documentos centro\\Horario Blady\\LICEO LOS TOROS - 2022-2023 - No preferencia.fet"
et = ET.parse(file)
print(str(et))

root = et.getroot()

for neighbor in root.iter('neighbor'):
    print(neighbor.attrib)
for child in root:
    print(child)
# Append new tag: <a x='1' y='abc'>body text</a>
# new_tag = xml.etree.ElementTree.SubElement(et.getroot(), 'a')
# new_tag.text = 'body text'
# new_tag.attrib['x'] = '1' # must be str; cannot be an int
# new_tag.attrib['y'] = 'abc'
#
# # Write back to file
# #et.write('file.xml')
# et.write('file_new.xml')