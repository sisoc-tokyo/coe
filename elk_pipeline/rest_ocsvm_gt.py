import urllib.parse
from flask import Flask, jsonify, request
from signature_detection import SignatureDetector
import InputLog
import pickle
import os

DOMAIN_NAME='example.com'
log='logs.pickle'

class MyFlask (Flask):
    def __init__(self, import_name, static_path=None, static_url_path=None,
                 static_folder='static', template_folder='templates',
                 instance_path=None, instance_relative_config=False):
        Flask.__init__(self, import_name, static_path, static_url_path,
                       static_folder, template_folder,
                       instance_path, instance_relative_config)

        print('Initialize Flask')
        if os.path.exists(log)==True:
            with open(log, mode='rb') as f:
                SignatureDetector.df=pickle.load(f)

        try:
            file_admin = open("./admin.csv")
            SignatureDetector.adminlist = file_admin.readlines()
            file_cmd = open("./command.csv")
            SignatureDetector.cmdlist = file_cmd.readlines()
        except Exception as e:
            print(e)
        finally:
            file_admin.close()
            file_cmd.close()

        SignatureDetector.adminlist = [s.replace('\n', '') for s in SignatureDetector.adminlist]
        SignatureDetector.cmdlist = [s.replace('\n', '') for s in SignatureDetector.cmdlist]

    def __del__(self):
        print('destructor called')


app = MyFlask(__name__)

@app.route('/preds', methods=['POST'])
def preds():
    global DOMAIN_NAME
    # loading
    response = jsonify()
    datetime = request.form.get('datetime',None)
    eventid = request.form.get('eventid',None)
    org_accountname = request.form.get('accountname',None)
    clientaddr = request.form.get('clientaddr',None)
    servicename = request.form.get('servicename',None)
    processname = request.form.get('processname',None)
    objectname = request.form.get('objectname',None)
    sharedname = request.form.get('sharedname',None)

    datetime = datetime.strip("'")
    eventid = eventid.strip("'")
    if org_accountname != None:
        accountname = org_accountname.strip("'")
        accountname = accountname.lower()
        accountname = accountname.split('@')[0]
        if (accountname.find(DOMAIN_NAME)> -1 or len(accountname)==0):
            return SignatureDetector.RESULT_NORMAL
    if clientaddr != None:
        clientaddr = clientaddr.strip("'")
    if servicename != None:
        servicename = servicename.strip("'")
        servicename = servicename.lower()
    if processname != None:
        processname = processname.strip("'")
        processname = processname.lower()
    if objectname != None:
        objectname = objectname.strip("'")
        objectname = objectname.lower()
    if sharedname != None:
        sharedname = sharedname.strip("'")
        sharedname = sharedname.lower()

    inputLog = InputLog.InputLog(datetime, eventid, accountname, clientaddr, servicename, processname, objectname, sharedname)
    result = SignatureDetector.signature_detect(inputLog)

    print(inputLog.get_eventid()+","+inputLog.get_accountname()+","+inputLog.get_clientaddr()+","+inputLog.get_processname())


    return result

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0')
    finally:
        with open(log, mode='wb') as handle:
            pickle.dump(SignatureDetector.df, handle, protocol=pickle.HIGHEST_PROTOCOL)