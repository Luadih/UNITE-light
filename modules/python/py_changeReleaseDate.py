# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d
from datetime import date

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

def main():
    essentials()

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

# Build Interface Button

def message(msg_type, data):
    if msg_type == c4d.MSG_NOTIFY_EVENT:
        event_data = data['event_data']
        if event_data['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND:
            desc_id = event_data['msg_data']['id']
            if desc_id[1].id == 30: # The ID of the User Data
                changeReleaseDate()
## Functions
def changeReleaseDate():
    releaseUI = uiNull[c4d.ID_USERDATA, 3]

    dateToday = date.today()
    dateToday = dateToday.strftime("%Y%m%d")
    releaseValue = "R" + dateToday

    if releaseUI == releaseValue or releaseUI.find(".") != -1:
        if releaseUI.find(".") != -1:
            lastChar = releaseUI[-1]
            uiNull[c4d.ID_USERDATA, 3] = releaseValue + "." + str(int(lastChar) + 1)
        else:
            uiNull[c4d.ID_USERDATA, 3] = releaseValue + ".1"
    else:
        uiNull[c4d.ID_USERDATA, 3] = releaseValue