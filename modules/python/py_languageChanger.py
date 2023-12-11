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
    except TypeError:
        err("the function 'open' in Python triggered a TypeError, update C4D to at least R23")
        c4d.gui.MessageDialog("Caching Languages doesn't work in this version of C4D.\nTry updating to at least Cinema 4D R23 for caching to work.\n*This doesn't necessarily mean that languages don't get applied by using already cached languages.")
        return

    try: openFile = json.load(file)
    except json.JSONDecodeError: err("lang json file is not structured correctly"); return
    file.close()

    count = len(openFile)
    if count == 0: err("there are no languages in the language file"); return

    # Sorts the dict just in case
    myKeys = list(openFile.keys())
    myKeys.sort()
    sorted_dict = {i: openFile[i] for i in myKeys}

    cacheData = usePseudoVariables(sorted_dict)
    langNull[c4d.ID_USERDATA, 1] = json.dumps(cacheData, indent=4, ensure_ascii=False)

    listCache = {}
    for index, item in enumerate(sorted_dict):
        listCache[index] = item
    langNull[c4d.ID_USERDATA, 2] = json.dumps(listCache)

    langDict = eval(langNull[c4d.ID_USERDATA, 1])

    print("UN: Cached %s languages to UNITE" % len(langDict))

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
    idCache = eval(langNull[c4d.ID_USERDATA, 2])
    langData = eval(langNull[c4d.ID_USERDATA, 1])
    activeLang = idCache.get(str(uiNull[c4d.ID_USERDATA, languageSel]))
    langDisplay = langData[activeLang]["displayName"]
    stringsDir = langData[activeLang]["strings"]

    if len(stringsDir) == 0:
        err("Language '%s' was made using the wrong format" % langDisplay)
        return None

    checks = list(stringsDir)
    nullBc = uiNull.GetUserDataContainer()

    if "interface" in checks:
        interfaceChanges = []

        for key in stringsDir["interface"]:
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
                    interfaceChanges.append((udId, nameSpace, str(stringsDir["interface"][key]), bc))

        for udId, key, value, container in interfaceChanges:
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

    if "desc" in checks:
        for key in stringsDir["desc"]:
            uiNull[c4d.ID_USERDATA, int(key)] = stringsDir["desc"][key]

def accessDictionary_by_UdID(userdataid, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 1])

    udId, bc = userData[userDataDict[userdataid]]

    return udId, bc

def usePseudoVariables(jsonFile):
    def replaceVars(jsonFile, language, stringGroup, vars):
        stringsCont = jsonFile[language]["strings"][stringGroup]
        stringMemory = []
        valueChanges = []

        for data in stringsCont:
            stringMemory.append((data, stringsCont[data]))

        for index, data in enumerate(stringMemory):
            if any(x in list(vars) for x in (data[1].values() if isinstance(data[1], dict) else [data[1]])):
                temp = str(data[1])
                for var in vars:
                    temp = temp.replace(var, vars[var])

                valueChanges.append((stringMemory[index][0], eval(temp)))
                
        for key, content in valueChanges:
            stringsCont[key] = content
    
    languages = list(jsonFile)

    for language in languages:
        try: translationGroups = list(jsonFile[language]["strings"])
        except: err("Language %s doesn't have any translation strings" % language)

        try:
            vars = jsonFile[language]["vars"]
            for group in translationGroups:
                replaceVars(jsonFile, language, group, vars)
        except KeyError:
            err("Language %s doesn't have variables (Skipping)" % language)

    return jsonFile