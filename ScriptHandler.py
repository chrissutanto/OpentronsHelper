import re, os

# Takes filename, returns lines of script
def getLines(filename, folder):
    file = open('{}/{}'.format(filename, folder))
    lines = file.readlines()
    return lines

# Takes line containing item (pipette/labware) info, returns dict of {location:item}
def getItem(line):
    pattern = "'(.*?)'"
    item = re.search(pattern, line)[1]
    afterComma = line[line.find(","):]
    location = re.search(pattern, afterComma)[1]
    return {'location': location, 'item': item}

# Takes line containing metadata info, returns dict of {field:value}
def getInfo(line):
    pattern = "'(.*?)'"
    field = re.search(pattern, line)[1]
    afterColon = line[line.find(":"):]
    value = re.search(pattern, afterColon)[1]
    return {'field': field, 'value': value}

# Takes line containing modifiable field, returns dict of {field:value}
def getField(line):
    field = line.split("=")[0].strip() 
    value = line.split("=")[1].strip()
    description = ""
    if "#" in value:
        description = value.split("#")[1].lstrip().capitalize()
        value = value.split("#")[0]
    return {'field': field, 'value': value, 'description': description}

# Takes labware, returns deck location (helper to sort labware by deck location)
def getLocation(labware):
    return labware['location']

# Takes filename, returns list of dict containing labware info
def findLabware(folder, filename):
    labware = []
    lines = getLines(folder, filename)
    for i in range(len(lines)):
        if "protocol.load_labware" in lines[i]:
            if "'" in lines[i]:
                new_item = getItem(lines[i])
            elif "'" in lines[i+1]:
                new_item = getItem(lines[i+1])
            labware.append(new_item)
    labware.sort(key=getLocation)
    return labware

# Takes filename, returns list of dict containing pipette info
def findPipettes(folder, filename):
    pipettes = []
    lines = getLines(folder, filename)
    for i in range(len(lines)):
        if "protocol.load_instrument" in lines[i]:
            if "'" in lines[i]:
                new_item = getItem(lines[i])
            elif "'" in lines[i+1]:
                new_item = getItem(lines[i+1])
            pipettes.append(new_item)
    return pipettes

# Takes filename, returns list of dict containing metadata info
def findMetadata(folder, filename):
    metadata = []
    lines = getLines(folder, filename)
    for i in range(len(lines)):
        if "metadata" in lines[i]:
            while not "}" in lines[i+1]:
                metadata.append(getInfo(lines[i+1]))
                i = i+1    
            break
    return metadata

# Takes filename, returns list of dict containing mod field info
def findModFields(folder, filename):
    fields = []
    lines = getLines(folder, filename)
    for i in range(len(lines)):
        if "# modify" in lines[i]:
            while not "# end modify" in lines[i+1]:
                fields.append(getField(lines[i+1]))
                i = i+1
    return fields

# Takes list of tuples representing user input, updates script modfields
def editModFields(filename, user_input):
    lines = getLines("ProtocolFiles", filename)
    input_no = 0
    for i in range(len(lines)):
        if "# modify" in lines[i]:
            while not "# end modify" in lines[i+1]:
                if "=" in lines[i+1]:
                    field = lines[i+1].split("=")[0]
                    new_value = user_input[input_no][1]['value']
                    if "#" in lines[i+1]:
                        description = lines[i+1].split("#")[1]
                        lines[i+1] = field + "= " + new_value + " # " + description.lstrip().capitalize()
                    else:
                        lines[i+1] = field + "= " + new_value + "\n"
                    input_no = input_no + 1
                i = i + 1
    protocol_file = open("TemporaryFiles/temp_{}".format(filename), "w")
    protocol_file.writelines(lines)
    protocol_file.close()

# Takes modField list, returns if well maps are enabled
def wellMapEnabled(metadata):
    for item in metadata:
        if item['field'].lower() == "well-map":
            if item['value'].lower() == "true":
                return True
    return False