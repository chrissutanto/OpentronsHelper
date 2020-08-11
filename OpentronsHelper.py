from flask import Flask, render_template, url_for, redirect, send_file, request
from FileManager import getProtocolList, getWellMapList, makeTempFile, saveHistory, getHistoryList, deleteFile
from ScriptHandler import findLabware, findPipettes, findMetadata, findModFields, editModFields, wellMapEnabled, editScriptRTPCR, simulateScript, findWellmap, isHistory
from Forms import modifyForm, historyForm
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'justheresoformswork'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ProtocolScripts')
def ProtocolScripts():
    protocolList = getProtocolList()
    directory = os.getcwd()
    return render_template('protocol_scripts.html', protocolList=protocolList, directory=directory)

@app.route('/AddProtocol')
def AddProtocol():
    return render_template('add_protocol.html')

@app.route('/protocoluploader', methods=['GET', 'POST'])
def UploadProtocol():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join('ProtocolFiles/', f.filename))
        return redirect(url_for('ProtocolScripts'))

@app.route('/AddWellMap/<filename>')
def AddWellMap(filename):
    return render_template('add_wellmap.html', filename=filename)

@app.route('/wellmapuploader/<filename>', methods=['GET', 'POST'])
def UploadWellMap(filename):
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join('WellMaps/', f.filename))
        if filename == 'None':
            return redirect(url_for('ManageWellMaps'))
        else:
            return redirect(url_for('WellMapSelect', filename=filename))

@app.route('/DeleteProtocolConfirm/<filename>')
def DeleteProtocolConfirm(filename):
    return render_template('delete_protocol.html', protocol=filename)

@app.route('/DeleteProtocol/<filename>')
def DeleteProtocol(filename):
    deleteFile('ProtocolFiles', filename)
    return redirect(url_for('ProtocolScripts'))

@app.route('/ManageWellMaps')
def ManageWellMaps():
    wellMapList = getWellMapList()
    return render_template('manage_wellmaps.html', wellMapList=wellMapList)

@app.route('/DeleteWellMapConfirm/<filename>')
def DeleteWellMapConfirm(filename):
    return render_template('delete_wellmap.html', wellmap=filename)

@app.route('/DeleteWellMap/<filename>')
def DeleteWellMap(filename):
    deleteFile('WellMaps', filename)
    return redirect(url_for('ManageWellMaps'))

@app.route('/WellMapSelect/<filename>')
def WellMapSelect(filename):
    wellMapList = getWellMapList()
    directory = os.getcwd()
    return render_template('wellmap_select.html', protocol=filename, wellMapList=wellMapList, directory=directory)

@app.route('/ApplyWellMap/<filename>/<wellmap>')
def ApplyWellMap(filename, wellmap):
    folder = "TemporaryFiles"
    temp_filename = 'temp_' + filename
    editScriptRTPCR(folder, temp_filename, wellmap)
    modFields = findModFields(folder, temp_filename)
    if modFields != []:
        return redirect(url_for('Modify', filename=filename))
    return redirect(url_for('Confirm', filename=filename))

@app.route('/Protocol/<filename>')
def Protocol(filename):
    folder = "ProtocolFiles"
    labware = findLabware(folder, filename)
    pipettes = findPipettes(folder, filename)
    metadata = findMetadata(folder, filename)
    modFields = findModFields(folder, filename)
    makeTempFile(filename)
    wellMap = wellMapEnabled(metadata)
    return render_template('protocol.html', protocol=filename, labwareList=labware, pipetteList=pipettes, metadataList=metadata, modFieldList=modFields, wellMapEnabled=wellMap)

@app.route('/Modify/<filename>', methods=['post', 'get'])
def Modify(filename):
    folder = "ProtocolFiles"
    modFields = findModFields(folder, filename)
    form = modifyForm(fields=modFields)
    if form.validate_on_submit():
        results=[]
        for data in enumerate(form.fields.data):
            results.append(data)
        editModFields(filename, results)
        return redirect(url_for('Confirm', filename=filename))
    return render_template('modify.html', protocol=filename, form=form, modFieldList=modFields)

@app.route('/Confirm/<filename>')
def Confirm(filename):
    temp_filename = 'temp_' + filename
    folder = "TemporaryFiles"
    labware = findLabware(folder, temp_filename)
    pipettes = findPipettes(folder, temp_filename)
    metadata = findMetadata(folder, temp_filename)
    modFields = findModFields(folder, temp_filename)
    return render_template('confirm.html', protocol=filename, labwareList=labware, pipetteList=pipettes, metadataList = metadata, modFieldList=modFields, history=False)

@app.route('/HistoryConfirm/<filename>')
def HistoryConfirm(filename):
    folder = "History/{}".format(filename)
    labware = findLabware(folder, filename)
    pipettes = findPipettes(folder, filename)
    metadata = findMetadata(folder, filename)
    modFields = findModFields(folder, filename)
    return render_template('confirm.html', protocol=filename, labwareList=labware, pipetteList=pipettes, metadataList = metadata, modFieldList=modFields, history=True)

@app.route('/Simulate/<filename>')
def Simulate(filename):
    temp_filename = 'temp_' + filename
    folder = "TemporaryFiles"
    simulationLog = simulateScript(folder, temp_filename)
    return render_template('simulate.html', simulationLog=simulationLog[1], filename=filename, error=simulationLog[0], history=False)

@app.route('/SimulateHistory/<filename>')
def SimulateHistory(filename):
    folder = "History/{}".format(filename)
    simulationLog = simulateScript(folder, filename)
    return render_template('simulate.html', simulationLog=simulationLog[1], filename=filename, error=simulationLog[0], history=True)

@app.route('/FileReady/<filename>')
def FileReady(filename):
    return render_template('file_ready.html', filename=filename, history=False)

@app.route('/FileReadyHistory/<filename>')
def FileReadyHistory(filename):
    return render_template('file_ready.html', filename=filename, history=True)

@app.route('/ReturnFile/<filename>')
def ReturnFile(filename):
    temp_filename = 'temp_' + filename
    return send_file('TemporaryFiles/{}'.format(temp_filename), as_attachment=True, cache_timeout=-1)

@app.route('/ReturnFileHistory/<filename>')
def ReturnFileHistory(filename):
    return send_file('History/{}/{}'.format(filename, filename), as_attachment=True, cache_timeout=-1)

@app.route('/SaveHistory/<filename>', methods=('GET', 'POST'))
def SaveHistory(filename):
    form = historyForm()
    if form.validate_on_submit():
        email = form.email.data
        description = form.description.data
        saveHistory(filename, email, description)
        return redirect(url_for('home'))
    return render_template('save_history.html', filename=filename, form=form)

@app.route('/History')
def History():
    historyList = getHistoryList()
    return render_template('history_list.html', historyList=historyList)

@app.route('/History/Protocol/<filename>')
def ProtocolHistory(filename):
    folder = "History/{}".format(filename)
    labware = findLabware(folder, filename)
    pipettes = findPipettes(folder, filename)
    metadata = findMetadata(folder, filename)
    modFields = findModFields(folder, filename)
    wellmap = findWellmap(folder, filename)
    return render_template('protocol_history.html', history=filename, labwareList=labware, pipetteList=pipettes, metadataList=metadata, modFieldList=modFields, wellmap=wellmap)

if __name__== '__main__':
    app.run(debug=True)