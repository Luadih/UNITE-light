# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d
import json
import os

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
    langPath = projectDir + "/data/lang/"
    langRawData = {}

    try:
        langFiles = os.listdir(langPath)
    except EnvironmentError:
        err("lang folder doesn't exist or it wasn't found.")
        return

    for filename in langFiles:
        if filename.endswith('.json'):
            name = os.path.splitext(filename)[0]
            filePath = os.path.join(langPath, filename)

            try:
                with open(filePath, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if not data: err("there is no data inside '%s' lang file."); return
                    langRawData[name] = data
            except TypeError:
                err("the function 'open' in Python triggered a TypeError, update C4D to at least R23")
                try:
                    c4d.gui.MessageDialog(loadMessageTranslation())
                except:
                    c4d.gui.MessageDialog("Caching Languages doesn't work in this version of C4D.\nTry updating to at least Cinema 4D R23 for caching to work.\n*This doesn't necessarily mean that languages don't get applied by using already cached languages.")
                return
            except json.JSONDecodeError:
                err("'%s' lang file is not structured correctly" % filename)
                continue

    if not langRawData: err("lang raw data is empty, returning"); return

    # Sorts the dict just in case
    myKeys = list(langRawData.keys())
    myKeys.sort()
    sorted_dict = {i: langRawData[i] for i in myKeys}

    cacheData = usePseudoVariables(sorted_dict)
    langNull[c4d.ID_USERDATA, 1] = json.dumps(cacheData, indent=4, ensure_ascii=False)

    listCache = {index: item for index, item in enumerate(sorted_dict)}
    langNull[c4d.ID_USERDATA, 2] = json.dumps(listCache)

    langDict = eval(langNull[c4d.ID_USERDATA, 1])

    print("UN: Cached %s languages to UNITE" % len(langDict))

    loadLanguagesToUi(languageSel, langDict)

def loadMessageTranslation():
    uiNull = essentials()[0]
    langNull = doc.SearchObject("py_languageChanger")
    languageSel = 31
    idCache = eval(langNull[c4d.ID_USERDATA, 2])
    langData = eval(langNull[c4d.ID_USERDATA, 1])
    activeLang = idCache.get(str(uiNull[c4d.ID_USERDATA, languageSel]))
    messageContent = langData[activeLang]["content"]["message"]["cacheLanguagesFailed"]
    return messageContent

def loadLanguagesToUi(controllerId, langDict):
    uiNull = essentials()[0]
    controllerValue = uiNull[c4d.ID_USERDATA, controllerId]
    udId, bc = accessDictionary_by_UdID(controllerId, uiNull)

    cycleCont = c4d.BaseContainer()
    for index, langKey in enumerate(langDict.keys()):
        langName = langDict[langKey]["displayName"]
        cycleCont.SetString(index, langName)

    if controllerValue > len(langDict) - 1: uiNull[c4d.ID_USERDATA, controllerId] = 0

    bc[c4d.DESC_CYCLE] = cycleCont
    uiNull.SetUserDataContainer(udId, bc)

def changeLanguage():
    uiNull = essentials()[0]
    langNull, languageSel = mainVar()
    idCache = eval(langNull[c4d.ID_USERDATA, 2])
    langData = eval(langNull[c4d.ID_USERDATA, 1])
    activeLang = idCache.get(str(uiNull[c4d.ID_USERDATA, languageSel]))
    langDisplay = langData[activeLang]["displayName"]
    stringsDir = langData[activeLang]["content"]

    if not stringsDir:
        err("Language '%s' was made using the wrong format" % langDisplay)
        return None
    
    try:
        langCredit = langData[activeLang]["credit"]
        showUserData(True, 53)
        uiNull[c4d.ID_USERDATA, 53] = langCredit
    except KeyError:
        showUserData(False, 53)

    checks = list(stringsDir)
    nullBc = uiNull.GetUserDataContainer()

    if "controls" in checks:
        controlChanges = []

        for key in stringsDir["controls"]:
            for udId, bc in nullBc:
                udName = bc.GetString(c4d.DESC_NAME)
                udsName = bc.GetString(c4d.DESC_SHORT_NAME)

                if udName != key and udsName != key: continue

                if udId[1].dtype in [11] or udId[1].id in [21, 25]:
                    udDefName = udsName
                    nameSpace = c4d.DESC_NAME
                else:
                    udDefName = udName
                    nameSpace = c4d.DESC_SHORT_NAME

                if udDefName == key:
                    controlChanges.append((udId, nameSpace, str(stringsDir["controls"][key]), bc))

        for udId, key, value, container in controlChanges:
            container[key] = value
            uiNull.SetUserDataContainer(udId, container)

    if "values" in checks:
        valueChanges = []

        for key, value in stringsDir["values"].items():
            udId, bc = accessDictionary_by_UdID(int(key), uiNull)
            valueChanges.append((value, udId, bc))

        for values, udId, container in valueChanges:
            containerValues = container[14]
            for index, name in values.items():
                containerValues.SetString(int(index), name)

            container.SetContainer(c4d.DESC_CYCLE, containerValues)

            uiNull.SetUserDataContainer(udId, container)

    if "comment" in checks:
        for key in stringsDir["comment"]:
            uiNull[c4d.ID_USERDATA, int(key)] = stringsDir["comment"][key]

def accessDictionary_by_UdID(userdataid, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 1])

    udId, bc = userData[userDataDict[userdataid]]

    return udId, bc

def usePseudoVariables(jsonFile):
    def replaceVars(stringsCont, vars):
        for key, value in stringsCont.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    for var, replacement in vars.items():
                        if var in v:
                            value[k] = v.replace(var, replacement)
            elif isinstance(value, str):
                for var, replacement in vars.items():
                    if var in value:
                        stringsCont[key] = value.replace(var, replacement)

    for lang, langData in jsonFile.items():
        try: 
            langContent = langData.get("content", {})
            if not langContent: raise KeyError("ALERT: Language %s doesn't have any translation strings" % lang)

            varsDict = langData.get("vars", {})
            if not varsDict: continue

            for group, stringsCont in langContent.items():
                replaceVars(stringsCont, varsDict)
        except KeyError as errorMessage:
            err(str(errorMessage))

    return jsonFile

def showUserData(trigger, target):
    controller = essentials()[0]
    if target == []: err("targetData is empty"); return
    if type(target) == int: target = [target]

    for targetId in target:
        udId, bc = accessDictionary_by_UdID(targetId, controller)
        bc[c4d.DESC_HIDE] = trigger == 0
        modifications = [(udId, bc)]
    
    for descId, container in modifications:
        controller.SetUserDataContainer(descId, container)