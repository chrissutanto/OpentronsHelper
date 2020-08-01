import os, shutil

# Checks if protocol folder exists, if not creates a folder then returns None. Otherwise, returns list of files
def getProtocolList():
    if os.path.exists('ProtocolFiles'):
        protocolList = os.listdir('ProtocolFiles')
    else:
        os.mkdir('ProtocolFiles')
        protocolList = []
    return protocolList

# Takes filename and duplicates it into temporary file folder (creates one if does not exist)
def makeTempFile(filename):
    if not os.path.exists('TemporaryFiles'):
        os.mkdir('TemporaryFiles')
    shutil.copyfile('ProtocolFiles/{}'.format(filename), 'TemporaryFiles/temp_{}'.format(filename))




    