# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d
import json

def err(error):
    file = op.GetObject().GetName()
    print(file + ": " + error)

def essentials():
    root = op.GetObject().GetUp().GetUp()
    if root is None: err("root not found, hierarchy might have been broken"); return

    uiNull = root.GetUp()
    if uiNull is None: err("main null not found, hierarchy might have been broken"); return

    dictNull = doc.SearchObject("py_buildDictionary")
    if uiNull is None: err("dictionary null doesn't exist"); return

    return uiNull, dictNull

def mainVar():
    langNull = op.GetObject()
    if langNull is None: err("what the fuck happened"); return

    languageSel = 31

    return langNull, languageSel


def main():
    uiNull = essentials()[0]

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())


def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 33
    ):
        cacheLang()

    elif (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_POSTSETPARAMETER and
        data['event_data']['msg_data']['descid'][1].id == 31
    ):
        changeLanguage()
        
def cacheLang():
    langNull, languageSel = mainVar()
    projectDir = doc.GetDocumentPath()
    try: file = open(projectDir + "/data/lang.json","r", encoding="utf-8")
    except EnvironmentError: err("lang file doesn't exist, you may be in another directory or data folder may have been removed"); return

    try: openFile = json.load(file)
    except json.JSONDecodeError: err("lang json file is not structured correctly"); return

    count = len(openFile)
    if count == 0: err("there are no languages in the language file"); return

    langNull[c4d.ID_USERDATA, 1] = json.dumps(openFile, indent=4)
    file.close()

    langDict = eval(langNull[c4d.ID_USERDATA, 1])

    print(f"UN: Cached {len(langDict)} languages to UNITE")

    loadLanguagesToUi(languageSel, langDict)

def loadLanguagesToUi(controllerId, langDict):
    uiNull = essentials()[0]
    count = len(langDict)
    controllerValue = uiNull[c4d.ID_USERDATA, controllerId]

    udId, bc = accessDictionary_by_UdID(controllerId, uiNull)

    cycleCont = c4d.BaseContainer()
    for index, langKey in enumerate(langDict.keys()):
        langName = langDict[langKey]["displayName"]
        cycleCont.SetString(index, langName)

    if controllerValue > count - 1: uiNull[c4d.ID_USERDATA, controllerId] = 0

    bc[c4d.DESC_CYCLE] = cycleCont
    uiNull.SetUserDataContainer(udId, bc)

def changeLanguage():
    uiNull = essentials()[0]
    langNull, languageSel = mainVar()
    langData = eval(langNull[c4d.ID_USERDATA, 1])
    activeLang = list(langData)[uiNull[c4d.ID_USERDATA, languageSel]]
    langValues = langData[activeLang]["values"]
    nullBc = uiNull.GetUserDataContainer()

    modifications = []

    for langDictName in langValues:
        for udId, bc in nullBc:
            udName = bc.GetString(c4d.DESC_NAME)
            udsName = bc.GetString(c4d.DESC_SHORT_NAME)

            if udName != langDictName and udsName != langDictName: continue

            if udId[1].dtype in [11]:
                udDefName = udsName
                nameSpace = c4d.DESC_NAME
            else:
                udDefName = udName
                nameSpace = c4d.DESC_SHORT_NAME

            if udDefName == langDictName:
                modifications.append((udId, nameSpace, str(langValues[langDictName]), bc))

    for udId, key, value, container in modifications:
        container[key] = value
        uiNull.SetUserDataContainer(udId, container)

def accessDictionary_by_UdID(userdataid, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 1])

    udId, bc = userData[userDataDict[userdataid]]

    return udId, bc