import os, shutil, time
from datetime import datetime
from ScriptHandler import findWellmap, findDescription, getLines
from EmailHandler import sendEmail

# Checks if protocol folder exists, if not creates a folder then returns None. Otherwise, returns list of files
def getProtocolList():
    protocolList = []
    if os.path.exists('ProtocolFiles'):
        nameList = os.listdir('ProtocolFiles')
        path = 'ProtocolFiles'
        nameList.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
        for name in nameList:
            protocol = {'name': name, 'time': time.ctime(os.path.getmtime(os.path.join(path, name))), 'description': findDescription(path, name)}
            protocolList.append(protocol)
    else:
        os.mkdir('ProtocolFiles')
    return protocolList

# Checks if history folder exists, then returns history list
def getHistoryList():
    if os.path.exists('History'):
        historyList = os.listdir('History')
        path = 'History/'
        historyList.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
    else:
        historyList = []
    return historyList

# Checks if well map folder exists, if not creates a folder then returns None. Otherwise, returns list of well map files
def getWellMapList():
    wellMapList = []
    if os.path.exists('WellMaps'):
        nameList = os.listdir('WellMaps')
        path = 'WellMaps/'
        wellMapList.sort(key = lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
        for name in nameList:
            wellMap = {'name': name, 'time': time.ctime(os.path.getmtime(os.path.join(path, name)))}
            wellMapList.append(wellMap)
    else:
        os.mkdir('WellMaps')
    return wellMapList

# Takes filename and duplicates it into temporary file folder (creates one if does not exist)
def makeTempFile(filename):
    if not os.path.exists('TemporaryFiles'):
        os.mkdir('TemporaryFiles')
    shutil.copyfile('ProtocolFiles/{}'.format(filename), 'TemporaryFiles/temp_{}'.format(filename))

# Deletes file
def deleteFile(folder, filename):
    os.remove(os.path.join(folder, filename))

# Deletes and recreates given folder
def clearDirectory(folder):
    shutil.rmtree(folder)
    time.sleep(1)
    os.mkdir(folder)

def getHistoryDescription(folder):
    lines = getLines(folder, 'description.txt')
    lines[0] = lines[0][13:]
    return lines

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

    # add history tag to file

    history_tag = '\n # HISTORY FILE'
    with open("History/{}/{}".format(title, title), 'a') as file:
        file.write(history_tag)

    # if there's a well map, add sheet to folder

    temp_filename = 'temp_' + filename
    wellmap = findWellmap('TemporaryFiles', temp_filename)
    if wellmap != {}:
        wellmap_name = wellmap['name']
        shutil.copyfile('WellMaps/{}'.format(wellmap_name), 'History/{}/{}'.format(title, wellmap_name))

    # email to user
    try:
        if email != "":
            sendEmail(title, email, description, wellmap_name)
    except Exception as e:
        print("invalid email")



    