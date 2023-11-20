# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d
from datetime import date

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
    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 30
    ):
        changeReleaseDate()

## Functions
def changeReleaseDate():
    uiNull = essentials()
    releaseValue = uiNull[c4d.ID_USERDATA, 3]

    today = date.today()
    dateToday = today.strftime("%Y%m%d")
    newValue = f"R{dateToday}"

    if releaseValue == newValue or "." in releaseValue:
        lastChar = releaseValue[-1] if "." in releaseValue else None
        newValue = f"{newValue}.{int(lastChar) + 1}" if lastChar else f"{newValue}.1"
    
    uiNull[c4d.ID_USERDATA, 3] = newValue