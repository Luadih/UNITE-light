# pyright: reportMissingImports=false, reportUndefinedVariable=false
import c4d

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
    # Main Vars
    global lightLayer
    lightLayer = "UNITE.root"

    # HDRI Vars
    global hdriMatLayer
    hdriMatLayer = ["un.hdri.Simp", "un.hdri.Univ"]

    global hdriMemNull
    hdriMemNull = "un_HDRIMemory"

    global hdriMemPrefix
    hdriMemPrefix = "UN.HDR."

    # Universal Vars
    global lightPrefix
    lightPrefix = "un_L_"

    global panelPrefix
    panelPrefix = "un_P_"
def main():
    essentials()
    mainVar()

    if not uiNull.FindEventNotification(doc, op, c4d.NOTIFY_EVENT_MESSAGE):
        uiNull.AddEventNotification(op, c4d.NOTIFY_EVENT_MESSAGE, 0, c4d.BaseContainer())

# Build Interface Button

def message(msg_type, data):
    if msg_type == c4d.MSG_NOTIFY_EVENT:
        event_data = data['event_data']
        if event_data['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND:
            desc_id = event_data['msg_data']['id']
            if desc_id[1].id == 19: # The ID of the User Data
                populateOptions("un_ActivePresets", 20, 1, "presetSelection", "Preset", "SELECT A PRESET", 3)
                createLinks(29, "un_ActivePresets")
                populateOptions("un_LCollections", 13, 9, "uni_lightSelection", "Lights Selected", "None", 0)
                createLinks(22, "un_LCollections")
                populateOptions("un_PCollections", 17, 9, "uni_panelSelection", "Panels Selected", "None", 1)
                createLinks(26, "un_PCollections")
                generateHdrimem()
                populateOptions("un_HDRIMemory", 14, 32, "hdri_hdriSelection", "HDRI Selected", "[Personal/Custom]", 2)
                createLinks(28, "un_HDRIMemory")
## Functions
def populateOptions(options, controlId, groupId, innerName, displayName, noneSelection, elementType):
    options = doc.SearchObject(options)   # Where groups are located

    children = options.GetChildren()
    count = len(children)

    # Create and initialize user data container for an integer for the children
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)

    bc.SetString(c4d.DESC_NAME, innerName)
    bc.SetString(c4d.DESC_SHORT_NAME, displayName)
    bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_CYCLE)
    bc.SetInt32(c4d.DESC_MIN, 0)
    bc.SetInt32(c4d.DESC_MAX, count-1)
    parentGroup = c4d.DescID(c4d.DescLevel(c4d.ID_USERDATA), c4d.DescLevel(groupId, c4d.DTYPE_GROUP, 0))
    bc.SetData(c4d.DESC_PARENTGROUP, parentGroup)

    # Filling options
    cycle = c4d.BaseContainer()
    for index in range(0, count) :
        child = children[index]
        if elementType == 0:
            childName = (child.GetName()).replace(lightPrefix, '')
        elif elementType == 1:
            childName = (child.GetName()).replace(panelPrefix, '')
        elif elementType == 2:
            childName = (child.GetName()).replace(hdriMemPrefix, '')
        else:
            childName = child[c4d.ID_USERDATA, 4]
        cycle.SetString(index, childName)
    if noneSelection != None:
        cycle.SetString(999,noneSelection)

    # Reset the value so it isn't left blank
    print(displayName + ": " + str(count))
    if count == 0:
        uiNull[c4d.ID_USERDATA, controlId] = 999
    elif uiNull[c4d.ID_USERDATA, controlId] > count - 1 and uiNull[c4d.ID_USERDATA, controlId] != 999:
        uiNull[c4d.ID_USERDATA, controlId] = 0

    bc.SetContainer(c4d.DESC_CYCLE, cycle)
    # Set container for children user data cycle parameter
    uiNull.SetUserDataContainer([c4d.ID_USERDATA,controlId], bc)

def createLinks(userDataId, options):

    options = doc.SearchObject(options)   # Where groups are located

    children = options.GetChildren()
    count = len(children)

    # Clear list
    uiNull[c4d.ID_USERDATA,userDataId] = c4d.InExcludeData()

    # Add items to list
    inexList = uiNull[c4d.ID_USERDATA,userDataId]
    for index in range(0, count) :
        child = children[index]
        inexList.InsertObject(child, 0)
    uiNull[c4d.ID_USERDATA,userDataId] = inexList

# HDRI Specific Functions

def generateHdrimem():
    clearMemory()
    mats = doc.GetMaterials()

    layerCount = len(hdriMatLayer)
    count = len(mats)

    for layerIndex in range(0, layerCount):
        for index in range(0, count):
            child = mats[index]
            lmats = child.GetLayerObject(doc)
            if lmats != None :
                if lmats.GetName() == hdriMatLayer[layerIndex]:
                    materialName = child.GetName()
                    materialNameF = hdriMemPrefix + materialName
                    linkobj = child
                    createMemory(materialNameF, linkobj)
                    c4d.EventAdd()

def createMemory(nullName, linkobj): # Creates objects to use as memory
    hdriCollection = doc.SearchObject(hdriMemNull)
    nullType = c4d.BaseObject(5140)
    nullType.SetName(nullName)
    # Add user data
    hdriMemUserData(nullType, linkobj)
    memLayerobj = hdriCollection.GetLayerObject(doc)
    nullType.SetLayerObject(memLayerobj)
    # Tag Creation
    matTag = c4d.TextureTag()
    matTag.SetMaterial(linkobj)
    matTag.SetLayerObject(memLayerobj)
    nullType.InsertTag(matTag)
    nullType.InsertUnderLast(hdriCollection) # Inserts the object
    print("UN: Added HDRI: '" + nullName + "' to memory")

def clearMemory(): # Removes all children of hdriMemNull (clearing memory)
    collection = doc.SearchObject(hdriMemNull)
    items = collection.GetChildren()

    count = len(items)
    for index in range(0,count):
        child = items[index]
        child.Remove()

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