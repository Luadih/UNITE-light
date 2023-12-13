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

def mainVar():
    # HDRI Vars
    hdriMatLayer = ["un.hdri.Univ", "un.hdri.Simp"]
    hdriMemNull = "un_HDRIMemory"
    hdriMemPrefix = "UN.HDR."

    # Universal Vars
    lightPrefix = "un_L_"
    panelPrefix = "un_P_"

    return hdriMatLayer, hdriMemNull, hdriMemPrefix, lightPrefix, panelPrefix

def main():
    uiNull = essentials()[0]

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

def message(msg_type, data):
    if (
        msg_type == c4d.MSG_NOTIFY_EVENT and
        data['event_data']['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND and
        data['event_data']['msg_data']['id'][1].id == 19
    ):
        populateOptions("un_ActivePresets", 20, "SELECT A PRESET", 3, 29)
        populateOptions("un_LCollections", 13, "None", 0, 22)
        populateOptions("un_PCollections", 17, "None", 1, 26)
        generateHdrimem()
        populateOptions("un_HDRIMemory", 14, "[Personal/Custom]", 2, 28)
                

## Functions
def populateOptions(options, controlId, noneSelection, elementType, cacheList_ID):
    uiNull = essentials()[0]
    hdriMatLayer, hdriMemNull, hdriMemPrefix, lightPrefix, panelPrefix = mainVar()
    controlValue = uiNull[c4d.ID_USERDATA, controlId]
    options = doc.SearchObject(options)   # Where groups are located
    children = options.GetChildren()

    udId, bc = accessDictionary_by_UdID(controlId, uiNull)
    prefixes = {0: lightPrefix, 1: panelPrefix, 2: hdriMemPrefix}
    
    cycle = c4d.BaseContainer()
    for index, child in enumerate(children):
        if elementType in prefixes:
            prefix = prefixes.get(elementType, '')
            childName = (child.GetName()).replace(prefix, '')
        else:
            childName = child[c4d.ID_USERDATA, 4]
        cycle.SetString(index, childName)
    cycle.SetString(999,noneSelection)

    bc.SetContainer(c4d.DESC_CYCLE, cycle)

    uiNull.SetUserDataContainer(udId, bc)

    if not children:
        uiNull[c4d.ID_USERDATA, controlId] = 999
    elif controlValue > len(children) - 1 and controlValue != 999:
        uiNull[c4d.ID_USERDATA, controlId] = 0

    print("UN: Added %s elements from %s to User Interface" % (len(children), options.GetName()))

    createLinks(cacheList_ID, children, uiNull)

def createLinks(cacheList, elements, controller):
    controller[c4d.ID_USERDATA,cacheList] = c4d.InExcludeData()

    inexList = controller[c4d.ID_USERDATA,cacheList]
    for elem in elements:
        inexList.InsertObject(elem, 0)
    controller[c4d.ID_USERDATA,cacheList] = inexList

def generateHdrimem():
    clearMemory()
    hdriMatLayer= mainVar()[0]
    hdriMemPrefix = mainVar()[2]
    mats = doc.GetMaterials()
    hdriMats = []

    for selmat in mats:
        lmats = selmat.GetLayerObject(doc).GetName() if selmat.GetLayerObject(doc) else None

        if lmats is None: 
            continue

        if lmats in hdriMatLayer:
            orderIndex = hdriMatLayer.index(lmats)
            materialName = selmat.GetName()
            materialNameF = hdriMemPrefix + materialName
            hdriMats.append((materialNameF, selmat, orderIndex))
    
    def sortFunction(elem):
        return elem[2]
    hdriMats.sort(key=sortFunction)

    for name, mat, index in hdriMats:
        createMemory(name, mat)

def createMemory(nullName, linkobj): # Creates objects to use as memory
    hdriMemNull = mainVar()[1]
    hdriCollection = doc.SearchObject(hdriMemNull)
    nullObj = c4d.BaseObject(5140)
    nullObj.SetName(nullName)
    # Add user data
    hdriMemUserData(nullObj, linkobj)
    memLayerobj = hdriCollection.GetLayerObject(doc)
    nullObj.SetLayerObject(memLayerobj)
    # Tag Creation
    matTag = c4d.TextureTag()
    matTag.SetMaterial(linkobj)
    matTag.SetLayerObject(memLayerobj)
    nullObj.InsertTag(matTag)
    nullObj.InsertUnderLast(hdriCollection) # Inserts the object
    print("UN: Added HDRI: '%s' to memory" % nullName)

def clearMemory(): # Removes all children of hdriMemNull (clearing memory)
    hdriMemNull = mainVar()[1]
    collection = doc.SearchObject(hdriMemNull)
    items = collection.GetChildren()
    for item in items: item.Remove()

def hdriMemUserData(nullObj, linkobj): #Adds User Data to Null
    # HDRI Link
    matLink = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BASELISTLINK)
    matLink[c4d.DESC_NAME] = "matLink"
    matLink[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    matLinkUD = nullObj.AddUserData(matLink)
    nullObj[matLinkUD] = linkobj
    # HDRI Default Value
    valueSlider = c4d.GetCustomDataTypeDefault(c4d.DTYPE_REAL)
    valueSlider[c4d.DESC_NAME] = "defaultValue"
    valueSlider[c4d.DESC_MIN] = 0
    valueSlider[c4d.DESC_MAX] = 1
    valueSlider[c4d.DESC_STEP] = 0.01
    valueSlider[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    valueSlider[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_REALSLIDER
    valueSlider[c4d.DESC_UNIT] = c4d.DESC_UNIT_PERCENT
    valueSliderUD = nullObj.AddUserData(valueSlider)
    nullObj[valueSliderUD] = linkobj[c4d.MATERIAL_DIFFUSION_BRIGHTNESS]

def accessDictionary_by_UdID(userdataid, directory):
    dictNull = essentials()[1]
    userData = directory.GetUserDataContainer()
    userDataDict = eval(dictNull[c4d.ID_USERDATA, 1])

    udId, bc = userData[userDataDict[userdataid]]

    return udId, bc