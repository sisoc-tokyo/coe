import csv
import io
import pandas as pd
import InputLog

class SignatureDetector:
    EVENT_PRIV = "4672"
    EVENT_PROCESS = "4688"
    SYSTEM_DIR = ["c:\windows","c:\program files","C:\Program Files (x86)"];
    RESULT_NORMAL="normal"
    RESULT_PRIV = "Unexpected privilege is used"
    RESULT_CMD="Abnormal command or tool is used(command on blackList is used)"
    RESULT_MAL_CMD = "Abnormal command or tool is used(is not system directory)"

    df_cmd = pd.DataFrame(data=None, index=None, columns=["processname"], dtype=None, copy=False)

    adminlist=[]
    cmdlist=[]


    def __init__(self):
        print("constructor called")

    @staticmethod
    def signature_detect(datetime, eventid, accountname, clientaddr, servicename, processname, objectname,sharedname):
        """ Detect attack using signature based detection.
        :param datetime: Datetime of the event
        :param eventid: EventID
        :param accountname: Accountname
        :param clientaddr: Source IP address
        :param servicename: Service name
        :param processname: Process name(command name)
        :param objectname: Object name
        :return : True(1) if attack, False(0) if normal
        """

        inputLog = InputLog.InputLog(datetime, eventid, accountname, clientaddr, servicename, processname, objectname,sharedname)
        return SignatureDetector.signature_detect(inputLog)

    @staticmethod
    def signature_detect(inputLog):
        """ Detect attack using signature based detection.
        :param inputLog: InputLog object of the event
        :return : True(1) if attack, False(0) if normal
        """
        result=SignatureDetector.RESULT_NORMAL

        if (inputLog.get_eventid() == SignatureDetector.EVENT_PRIV):
            result =SignatureDetector.isNotAdmin(inputLog)

        elif (inputLog.get_eventid() == SignatureDetector.EVENT_PROCESS):
            result = SignatureDetector.isSuspiciousProcess(inputLog)


        return result

    @staticmethod
    def isNotAdmin(inputLog):
        logs = [s for s in SignatureDetector.adminlist if s == inputLog.get_accountname()]
        if len(logs) == 0:
            return SignatureDetector.RESULT_PRIV
        else:
            return SignatureDetector.RESULT_NORMAL

    @staticmethod
    def isSuspiciousProcess(inputLog):
        matched_list = [s for s in SignatureDetector.SYSTEM_DIR if s in inputLog.get_processname()]
        if (len(matched_list)==0):
            return SignatureDetector.RESULT_MAL_CMD
        cmds=inputLog.get_processname().split("\\")
        cmd=cmds[len(cmds)-1]
        logs = [s for s in SignatureDetector.cmdlist if s==cmd]
        if len(logs)>0:
            return SignatureDetector.RESULT_CMD

        return SignatureDetector.RESULT_NORMAL
