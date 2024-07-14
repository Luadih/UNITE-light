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
    messageContent = langData[activeLang]["contains"]["popup"]["cacheLanguagesError"]
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
    stringsDir = langData[activeLang]["contains"]

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

    if "interface" in checks: recursiveStringChange(stringsDir["interface"])

    if "values" in checks:
        valueChanges = []

        for key, value in stringsDir["values"].items():
            try:
                udId, bc = accessDictionary_by_Name(key, uiNull)
                valueChanges.append((value, udId, bc))
            except:
                err(key + " was not found in the user interface. (Skipping) [from 'values' translation]")

        for values, udId, container in valueChanges:
            containerValues = container[14]
            for index, name in values.items():
                containerValues.SetString(int(index), name)

            container.SetContainer(c4d.DESC_CYCLE, containerValues)

            uiNull.SetUserDataContainer(udId, container)

    if "notes" in checks:
        for key in stringsDir["notes"]:
            try:
                udID, bc = accessDictionary_by_Name(key, uiNull)
                uiNull[c4d.ID_USERDATA, udID[1].id] = stringsDir["notes"][key]
            except KeyError:
                err(key + " was not found in the user interface. (Skipping) [from 'notes' translation]")

def recursiveStringChange(data):
    uiNull = essentials()[0]
    tabIds = {
        "tab.home": 1,
        "tab.universal": 9,
        "tab.hdri": 32,
        "tab.advanced": 37,
        "tab.developer": 5
    }
    
    for key, value in data.items():
        if key.startswith("tab."):
            tab_udID, tab_bc = accessDictionary_by_UdID(tabIds.get(key), uiNull)
            
            tab_bc[c4d.DESC_SHORT_NAME] = value["name"]
            if "titleName" in value:
                tab_bc[c4d.DESC_NAME] = "-> " + value["titleName"]
            else:
                tab_bc[c4d.DESC_NAME] = "-> " + value["name"]
            
            uiNull.SetUserDataContainer(tab_udID, tab_bc)
            
            recursiveStringChange(value["contains"])
        elif isinstance(value, dict) and "contains" in value:
            try:
                udID, bc = accessDictionary_by_Name(key, uiNull)
                
                bc[c4d.DESC_NAME] = value["name"]
                
                uiNull.SetUserDataContainer(udID, bc)
            except KeyError:
                err(key + " was not found in the user interface. (Skipping)")
            recursiveStringChange(value["contains"])
        else:
            try:
                udID, bc = accessDictionary_by_Name(key, uiNull)
                
                if udID[1].dtype in [11]:
                    bc[c4d.DESC_NAME] = value
                else:
                    bc[c4d.DESC_SHORT_NAME] = value
                
                uiNull.SetUserDataContainer(udID, bc)
            except KeyError:
                err(key + " was not found in the user interface. (Skipping)")

def accessDictionary_by_UdID(userdataid, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 1])

    udId, bc = userData[userDataDict[userdataid]]

    return udId, bc

def accessDictionary_by_Name(udName, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 2])

    udId, bc = userData[userDataDict[udName]]

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
            langContent = langData.get("contains", {})
            if not langContent: raise KeyError("ALERT: Language %s doesn't have any translation strings" % lang)

            varsDict = langData.get("variables", {})
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