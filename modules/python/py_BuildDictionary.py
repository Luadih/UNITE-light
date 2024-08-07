# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d

def err(error):
    file = op.GetObject().GetName()
    print(file + ": " + error)

def essentials():
    root = op.GetObject().GetUp().GetUp()
    if root is None: err("root not found, hierarchy might have been broken"); return

    uiNull = root.GetUp()
    return uiNull if uiNull is not None else err("main null not found, hierarchy might have been broken"); return 

def main():
    uiNull = essentials()
    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 34
    ):
        buildDictionary()

def buildDictionary():
    uiNull = essentials()
    opObj = op.GetObject()
    userData = uiNull.GetUserDataContainer()
    userDataDictByID = {element[0][1].id: index for index, element in enumerate(userData)}
    
    userDataDictByName = {}
    for index, element in enumerate(userData):
        if element[0][1].dtype in [11] or element[0][1].id in [21, 25]:
            nameToSave = c4d.DESC_SHORT_NAME
        else:
            nameToSave = c4d.DESC_NAME
        
        userDataDictByName.update({element[1].GetString(nameToSave): index})

    opObj[c4d.ID_USERDATA, 1] = str(userDataDictByID)
    opObj[c4d.ID_USERDATA, 2] = str(userDataDictByName)