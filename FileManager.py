import os, shutil
from datetime import datetime
from ScriptHandler import findWellmap

# Checks if protocol folder exists, if not creates a folder then returns None. Otherwise, returns list of files
def getProtocolList():
    if os.path.exists('ProtocolFiles'):
        protocolList = os.listdir('ProtocolFiles')
    else:
        os.mkdir('ProtocolFiles')
        protocolList = []
    return protocolList

# Checks if well map folder exists, if not creates a folder then returns None. Otherwise, returns list of well map files
def getWellMapList():
    if os.path.exists('WellMaps'):
        wellMapList = os.listdir('WellMaps')
    else:
        os.mkdir('WellMaps')
        wellMapList = []
    return wellMapList

# Takes filename and duplicates it into temporary file folder (creates one if does not exist)
def makeTempFile(filename):
    if not os.path.exists('TemporaryFiles'):
        os.mkdir('TemporaryFiles')
    shutil.copyfile('ProtocolFiles/{}'.format(filename), 'TemporaryFiles/temp_{}'.format(filename))

#-------------------- History Saving --------------------

# Takes filename, description, and directory, writes description to text file in folder
def writeDescription(filename, description, directory):
    line = "Description: " + description
    with open("{}/description.txt".format(directory), 'a') as file:
        file.write(line)
    return None

# Takes filename, email, and description and saves to history
def saveHistory(filename, email, description):
    # if it doesn't exist, create a directory for history

    if not os.path.exists('History'):
        os.mkdir('History')

    # create folder in history directory with descriptive title

    date = datetime.now().strftime("[%Y-%b-%d][%H-%M-%S]")
    title = date + filename
    os.makedirs('History/{}'.format(title))

    # Add description to text file in folder

    writeDescription(filename, description, 'History/{}'.format(title))

    # make new title for temp file and save temp file to new folder in history directory

    shutil.copyfile('TemporaryFiles/temp_{}'.format(filename), 'History/{}/{}'.format(title, title))

    # if there's a well map, add sheet to folder

    wellmap = findWellmap(filename)
    shutil.copyfile('WellMaps/{}'.format(wellmap), 'History/{}/{}'.format(title, wellmap))
    # email to user



    