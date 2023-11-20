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
    else: 
        return uiNull

def main():
    uiNull = essentials()
    hideUserData(4, 5, uiNull)

def hideUserData(trigger, target, controller):
    if target == []: err("targetData is empty"); return
    if type(target) == int: target = [target]

    uData = controller.GetUserDataContainer()
    triggerValue = controller[c4d.ID_USERDATA, trigger]
    modifications = []
    
    for targetId in target:
        for descId, container in uData:
            if descId[1].id == targetId:
                container[c4d.DESC_HIDE] = triggerValue == 0
                modifications.append((descId, container))
    
    for descId, container in modifications:
        controller.SetUserDataContainer(descId, container)