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

    return uiNull

def main():
    uiNull = essentials()

    if uiNull[c4d.ID_USERDATA, 51] != 2:
        shadowControl()

def shadowControl():
    uiNull = essentials()
    shadowsValue = uiNull[c4d.ID_USERDATA, 51]

    render_data = doc.GetActiveRenderData()
    if render_data is None: return

    render_data[c4d.RDATA_OPTION_SHADOW] = shadowsValue