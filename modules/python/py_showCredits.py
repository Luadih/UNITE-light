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

def creditsNull_func():
    creditsNull = op.GetObject()
    if creditsNull is None: err("what the fuck happened"); return

    return creditsNull


def main():
    uiNull = essentials()[0]

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 50
    ):  
        cacheCredits()

    elif (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 48
    ):  
        showCredits()

def cacheCredits():
    creditsNull = creditsNull_func()
    projectDir = doc.GetDocumentPath()
    filePath = projectDir + "/data/credits.json"

    try:
        with open(filePath, "r", encoding="utf-8") as file:
            openFile = json.load(file)
    except EnvironmentError:
        err("credits file doesn't exist, you may be in another directory or data folder may have been removed")
        return
    except TypeError:
        err("the function 'open' in Python triggered a TypeError, update C4D to at least R23")
        c4d.gui.MessageDialog("Caching credits doesn't work in this version of C4D.\nTry updating to at least Cinema 4D R23 for caching to work.\n*This doesn't necessarily mean that credits won't show by using already cached ones.")
        return
    except json.JSONDecodeError:
        err("credits json file is not structured correctly")
        return

    if not openFile: err("there are no credits in the credits json"); return

    creditsNull[c4d.ID_USERDATA, 1] = json.dumps(openFile, indent=4, ensure_ascii=False)

    listCache = {index: item for index, item in enumerate(openFile)}
    creditsNull[c4d.ID_USERDATA, 2] = json.dumps(listCache)

    print("UN: Credits correctly cached to memory")

def showCredits():
    creditsNull = creditsNull_func()
    idCache = eval(creditsNull[c4d.ID_USERDATA, 2])
    creditsData = eval(creditsNull[c4d.ID_USERDATA, 1])

    oldCredits = doc.SearchObject("UNITE Credits")
    if oldCredits is not None:
        oldCredits.Remove()

    creditsObj = creditsObjCreation()
    
    for index in idCache:
        groupName = idCache[index]
        groupElement = createGroupUD(creditsObj, groupName)

        for name, credit in creditsData[groupName].items():
            stringUD = createStringUD(creditsObj, name, groupElement)
            creditsObj[stringUD] = str(credit)

    doc.InsertObject(creditsObj)
    c4d.EventAdd()
    
    c4d.gui.MessageDialog("Credits null was properly created.\nThe credits will be readable in the 'UNITE Credits' null at the top of your project.")

def creditsObjCreation():
    obj = c4d.BaseObject(c4d.Onull)
    obj.SetName("UNITE Credits")
    color = c4d.Vector(0.362, 0.11, 1)

    obj[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
    obj[c4d.ID_BASEOBJECT_COLOR] = color
    obj[c4d.ID_BASELIST_ICON_COLORIZE_MODE] = 1
    obj[c4d.ID_BASELIST_ICON_COLOR] = color

    return obj

def createGroupUD(obj, name, parentGroup=None, columns=None, shortname=None):
    if obj is None: return False
    if shortname is None: shortname = name
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = shortname
    bc[c4d.DESC_TITLEBAR] = 1
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    if columns is not None:
        bc[22] = columns
    bc[16] = True

    return obj.AddUserData(bc) 

def createStringUD(obj, name, parentGroup=None, shortname=None):
    if obj is None: return False
    if shortname is None: shortname = name
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_STRING)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = shortname
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    bc[c4d.DESC_CUSTOMGUI] = 12
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    
    return obj.AddUserData(bc)   