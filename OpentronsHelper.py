from flask import Flask, render_template, url_for, redirect
from FileManager import getProtocolList, getWellMapList, makeTempFile
from ScriptHandler import findLabware, findPipettes, findMetadata, findModFields, editModFields, wellMapEnabled, editScriptRTPCR
from Forms import modifyForm
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

@app.route('/WellMapSelect/<filename>')
def WellMapSelect(filename):
    wellMapList = getWellMapList()
    directory = os.getcwd()
    return render_template('wellmap_select.html', protocol=filename, wellMapList=wellMapList, directory=directory)

@app.route('/ApplyWellMap/<filename>/<wellmap>')
def ApplyWellMap(filename, wellmap):
    folder = "TemporaryFiles"
    temp_filename = 'temp_' + filename
    # apply well map
    editScriptRTPCR(folder, temp_filename, wellmap)
    # if no modfields, redirect to confirm
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
    return render_template('confirm.html', protocol=filename, labwareList=labware, pipetteList=pipettes, metadataList = metadata, modFieldList=modFields)


if __name__== '__main__':
    app.run(debug=True)