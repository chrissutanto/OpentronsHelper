import re, os, time
from openpyxl import load_workbook
from subprocess import Popen, PIPE

# Takes filename, returns lines of script
def getLines(folder, filename):
    file = open('{}/{}'.format(folder, filename))
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

# Takes filename, folder, returns description
def findDescription(folder, filename):
    metadata = findMetadata(folder, filename)
    for item in metadata:
        if item['field'] == 'description':
            return item['value']

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

# Takes filename, returns linked well map filename (returns none if none)
def findWellmap(folder, filename):
    lines = getLines(folder, filename)
    for line in lines:
        if "# wellmap" in line:
            wellmap = line[24:-2]
            modtime = time.ctime(os.path.getmtime(os.path.join('WellMaps', wellmap)))
            return {'name': wellmap, 'time': modtime}
    return {}


# Takes list of tuples representing user input, updates script modfields
def editModFields(filename, user_input):
    temp_filename = "temp_" + filename
    lines = getLines("TemporaryFiles", temp_filename)
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

# takes folder and filename, returns if file is a history file
def isHistory(folder, filename):
    lines = getLines(folder, filename)
    for line in lines:
        if "# HISTORY FILE" in line:
            return True
    return False

# Takes folder and filename, simulates protocol file and returns log
def simulateScript(folder, filename):
    # command = os.popen(r"opentrons_simulate.exe {}\{}".format(folder, filename)).read().splitlines()
    # return command

    p = Popen("opentrons_simulate.exe {}\{}".format(folder, filename), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True, text=True, universal_newlines=True)
    out = p.communicate()[0]
    err = p.communicate()[1]
    error = False

    if p.returncode != 0: 
        error = True
        return [error, err]
    return [error, out]

#-------------------- RTPCR Script Editing --------------------
# Takes wellmap filename, returns dict (different ranges) of dict (values, cell color) 
def readWellMap(wellmap):
    path = 'WellMaps/{}'.format(wellmap)
    workbook = load_workbook(path)
    sheet = workbook.active

    destination = sheet['B5:E12']
    source_1 = sheet['H5:M8']
    source_2 = sheet['H12:S19']

    wellData = {'destination': destination, 'source_1': source_1, 'source_2': source_2}
    # print(sheet['B1'].value)

    return wellData

#Takes source (cell), destination (tuple of tuples), and returns array of bool if color matches
def findColorMatch(source, destination):
    matches = []
    for row in destination:
        temp_row = []
        for cell in row:
            if cell.fill.start_color.index == source.fill.start_color.index and source.fill.start_color.index != '00000000':
                temp_row.append(True)
            else:
                temp_row.append(False)
        matches.append(temp_row)
    return matches

# Takes source (cell), destination (tuple of tuples), and returns array of bool if value matches
def findValueMatch(source, destination):
    matches = []
    for row in destination:
        temp_row = []
        for cell in row:
            if cell.value == source.value and source.value != None:
                temp_row.append(True)
            else:
                temp_row.append(False)
        matches.append(temp_row)
    return matches

# Clears all lines in protocol file after "# commands"
def clearCommands(folder, filename):
    lines = getLines(folder, filename)
    for i in range(len(lines)):
        if "# commands" in lines[i]:
            protocol_file = open("{}/{}".format(folder, filename), "w")
            lines = lines[:i+1]
            protocol_file.writelines(lines)
            protocol_file.close()
            break

# Sets up dictionary of destination wells in protocol file, also writes wellmap filename
def writeSetup(folder, filename, wellmap):
    with open("{}/{}".format(folder, filename), 'a') as file:
        file.write("    # wellmap filename: {} \n".format(wellmap))

    command = "    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']" + "\n" + "    d = {}" + "\n" + "    for letter in letters:" + "\n" + "        for i in range(1, 13):" + "\n" + "            d[letter + str(i)] = destination.wells_by_name()[letter + str(i)]"
    with open("{}/{}".format(folder, filename), 'a') as file:
        file.write(command)
    return None

# Takes source title, source location, and 2D array of matches, returns string of appropriate command
def generateCommand(source_title, row_idx, col_idx, matches):
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    command = ''
    destinations = ''
    match = False

    source_location = letters[row_idx] + str(col_idx + 1)

    if source_title == 'source_1':
        volume = 'source_1_volume'
    elif source_title == 'source_2':
        volume = 'source_2_volume'

    row_idx = 0
    for row in matches:
        col_idx = 0
        for cell in row:
            if cell:
                match = True
                for i in range(3):
                    destinations = destinations + "d['" + letters[row_idx] + str(col_idx * 3 + i + 1) + "'], "
            col_idx = col_idx + 1
        row_idx = row_idx + 1
    
    if match:
        command =  "\n" + "    " + 'single_pipette.distribute(' + volume + ', ' + source_title + ".wells_by_name()['" + source_location + "'], [" + destinations[:-2] + '])'
    return command

# Takes filename and command string, writes string onto file
def writeToScript(folder, filename, command):
    with open("{}/{}".format(folder, filename), 'a') as file:
        file.write(command)
    return None

# Takes protocol and well map filenames, edits protocol file with appropriate code
def editScriptRTPCR(folder, filename, wellmap):
    wellData = readWellMap(wellmap)

    source_1 = wellData['source_1']
    source_2 = wellData['source_2']
    sources = {'source_1': source_1, 'source_2': source_2}
    destination = wellData['destination']

    clearCommands(folder, filename)
    writeSetup(folder, filename, wellmap)

    for source in sources:
        row_idx = 0
        for row in sources[source]:
            col_idx = 0
            for cell in row:
                if source == 'source_1':
                    matches = findColorMatch(cell, destination)
                elif source == 'source_2':
                    matches = findValueMatch(cell, destination)
                command = generateCommand(source, row_idx, col_idx, matches)
                writeToScript(folder, filename, command)
                col_idx = col_idx + 1
            row_idx = row_idx + 1
    

    return None