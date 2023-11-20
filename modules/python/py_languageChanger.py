# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d
import json

def err(error):
    file = op.GetObject().GetName()
    print(file + ": " + error)

def essentials():
    global root
    root = op.GetObject().GetUp().GetUp()

    if root is None:
        err("root not found, hierarchy might have been broken")
        return

    global uiNull
    uiNull = root.GetUp()

    if uiNull is None:
        err("main null not found, hierarchy might have been broken")
        return

def mainVar():
    global langNull
    langNull = op.GetObject()

    if langNull is None:
        err("what the fuck happened")
        return

    global languageSel
    languageSel = 31

    global languageSelGroup
    languageSelGroup = 1


def main():
    essentials()
    mainVar()

    changeLanguage()

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())



def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 33
    ):
        cacheLang()

def cacheLang():
    projectDir = doc.GetDocumentPath()
    try:
        f = open(projectDir + "/data/lang.json","r", encoding="utf-8")
    except EnvironmentError:
        err("lang file doesn't exist, you may be in another directory or data folder may have been removed")
        return

    try:
        fopen = json.load(f)
    except json.JSONDecodeError:
        err("lang json file is not structured correctly")
        return

    count = len(fopen)
    if count == 0:
        err("there are no languages in the language file")
        return

    langNull[c4d.ID_USERDATA, 1] = str(fopen)

    f.close()

    d = eval(langNull[c4d.ID_USERDATA, 1])

    print("UN: Cached " + str(len(d)) + " languages to UNITE")

    ## Loading to Interface

    # Create and initialize user data container for an integer for the children
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)

    bc.SetString(c4d.DESC_NAME, "languageSel")
    bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_CYCLE)
    bc.SetInt32(c4d.DESC_MIN, 0)
    bc.SetInt32(c4d.DESC_MAX, count-1)
    parentGroup = c4d.DescID(c4d.DescLevel(c4d.ID_USERDATA), c4d.DescLevel(languageSelGroup, c4d.DTYPE_GROUP, 0))
    bc.SetData(c4d.DESC_PARENTGROUP, parentGroup)

    # Filling options
    cycle = c4d.BaseContainer()
    for index, lang_key in enumerate(d.keys()):
        langName = d[lang_key]["displayName"]
        cycle.SetString(index, langName)

    # Reset the value so it isn't left blank
    if uiNull[c4d.ID_USERDATA, languageSel] > count - 1:
        uiNull[c4d.ID_USERDATA, languageSel] = 0

    bc.SetContainer(c4d.DESC_CYCLE, cycle)
    # Set container for children user data cycle parameter
    uiNull.SetUserDataContainer([c4d.ID_USERDATA,languageSel], bc)

def changeLanguage():
    uNull = uiNull
    langData = eval(langNull[c4d.ID_USERDATA, 1])
    activeLang = list(langData)[uNull[c4d.ID_USERDATA, languageSel]]
    langValues = langData[activeLang]["values"]
    nullBc = uNull.GetUserDataContainer()

    # Collect modifications in a list
    modifications = []

    for langDictName in langValues:
        for udId, bc in nullBc:
            udName = bc.GetString(c4d.DESC_NAME)
            udsName = bc.GetString(c4d.DESC_SHORT_NAME)
            idValue = udId[1].id

            if udId[1].dtype in [11]:
                udDefName = udsName
                nameSpace = c4d.DESC_NAME
            else:
                udDefName = udName
                nameSpace = c4d.DESC_SHORT_NAME

            if udDefName == langDictName:
                modifications.append((udId, nameSpace, str(langValues[langDictName]), bc))

    # Apply modifications outside the loop
    for udId, key, value, container in modifications:
        container[key] = value
        uNull.SetUserDataContainer(udId, container)
