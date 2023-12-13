# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d

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

def main():
    uiNull = essentials()[0]

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_POSTSETPARAMETER and
        data['event_data']['msg_data']['descid'][1].id == 4
    ):
        hideUserData(4,5)

def hideUserData(trigger, target):
    controller = essentials()[0]
    if target == []: err("targetData is empty"); return
    if type(target) == int: target = [target]

    for targetId in target:
        udId, bc = accessDictionary_by_UdID(targetId, controller)
        bc[c4d.DESC_HIDE] = trigger == 0
        modifications = [(udId, bc)]
    
    for descId, container in modifications:
        controller.SetUserDataContainer(descId, container)

def accessDictionary_by_UdID(userdataid, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 1])

    udId, bc = userData[userDataDict[userdataid]]

    return udId, bc