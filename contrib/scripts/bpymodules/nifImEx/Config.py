import Blender, os, sys
import Read, Write, Defaults
from Blender import Draw, BGL, Registry

# clears the console window
if sys.platform in ('linux-i386','linux2'):
    os.system("clear")
elif sys.platform in ('win32','dos','ms-dos'):
    os.system("cls")

# All UI elements are kept in this dictionary to make sure they never go out of scope
_GUI_ELEMENTS = {}

# To avoid confusion with event ID handling I register them all in a list
_GUI_EVENTS = []

# Configuration
_CONFIG = {}
# Old configuration for cancel button
_CONFIG_BACK = _CONFIG
_CONFIG_NAME = "nifscripts"

# Back target for exit
_BACK_TARGET = None

# Texture search path item index
_IDX_TEXPATH = 0

def __init__():
    global _GUI_ELEMENTS, _WINDOW_SIZE, _CONFIG
    _GUI_ELEMENTS.clear()
    _CONFIG.clear()
    load()

def setImportPath(nifImportPath):
    global _CONFIG
    nifImportPath = Blender.sys.dirname(nifImportPath)
    if nifImportPath == '' or not Blender.sys.exists(nifImportPath):
        Draw.PupMenu('No path selected or path does not exist%t|Ok')
    else:
        _CONFIG["NIF_IMPORT_PATH"] = nifImportPath

def setExportPath(nifExportPath):
    global _CONFIG
    nifExportPath = Blender.sys.dirname(nifExportPath)
    if nifExportPath == '' or not Blender.sys.exists(nifExportPath):
        Draw.PupMenu('No path selected or path does not exist%t|Ok')
    else:
        _CONFIG["NIF_EXPORT_PATH"] = nifExportPath

def setTextureBase(textureBaseFolder):
    global _CONFIG
    textureBaseFolder = Blender.sys.dirname(textureBaseFolder)
    if textureBaseFolder == '' or not Blender.sys.exists(textureBaseFolder):
        Draw.PupMenu('No path selected or path does not exist%t|Ok')
    else:
        _CONFIG["BASE_TEXTURE_FOLDER"] = textureBaseFolder
        
def addTexturePath(nifTexturePath):
    global _CONFIG, _IDX_TEXPATH
    nifTexturePath = Blender.sys.dirname(nifTexturePath)
    if nifTexturePath == '' or not Blender.sys.exists(nifTexturePath):
        Draw.PupMenu('No path selected or path does not exist%t|Ok')
    else:
        _CONFIG["TEXTURE_SEARCH_PATH"].append(nifTexturePath)
        _IDX_TEXPATH = len(_CONFIG["TEXTURE_SEARCH_PATH"]) - 1



def addEvent(evName = "NO_NAME"):
    global _GUI_EVENTS
    eventId = len(_GUI_EVENTS)
    if eventId >= 16383:
        raise "Maximum number of events exceeded"
        return None
    _GUI_EVENTS.append(evName)
    return eventId


def guiText(str = "", xpos = 0, ypos = 0):
    # To draw text on the screen I have to position its start point first
    BGL.glRasterPos2i( xpos, ypos)
    Draw.Text(str)

def gui():
    global _GUI_ELEMENTS, _CONFIG, _IDX_TEXPATH, _GUI_EVENTS
    del _GUI_EVENTS[:]
    # These are to save me some typing
    #W = _WINDOW_SIZE[0]
    H = Blender.Window.GetAreaSize()[1]
    # dictionary of GUI elements
    E = {}
    
    texpathString = ""
    texpathItemString = ""
    if len(_CONFIG["TEXTURE_SEARCH_PATH"]) > 0:
        texpathString = ";".join(_CONFIG["TEXTURE_SEARCH_PATH"])
        if not _IDX_TEXPATH in xrange(len(_CONFIG["TEXTURE_SEARCH_PATH"])):
            _IDX_TEXPATH = 0
        texpathItemString = _CONFIG["TEXTURE_SEARCH_PATH"][_IDX_TEXPATH]
    
    
    # IMPORTANT: Don't start dictionary keys with an underscore, the Registry module doesn't like that, apparently
    # Draw.String(name, event, x, y, width, height, initial, length, tooltip=None) 
    E["NIF_IMPORT_PATH"]        = Draw.String("",       addEvent("NIF_IMPORT_PATH"),     50, H- 75, 390, 20, _CONFIG["NIF_IMPORT_PATH"],        390, "export path")
    E["BROWSE_IMPORT_PATH"]     = Draw.PushButton('...',addEvent("BROWSE_IMPORT_PATH"), 440, H- 75,  30, 20)
    E["NIF_EXPORT_PATH"]        = Draw.String("",       addEvent("NIF_EXPORT_PATH"),     50, H-100, 390, 20, _CONFIG["NIF_EXPORT_PATH"],        390, "import path")
    E["BROWSE_EXPORT_PATH"]     = Draw.PushButton('...',addEvent("BROWSE_EXPORT_PATH"), 440, H-100,  30, 20)
    E["BASE_TEXTURE_FOLDER"]    = Draw.String("",       addEvent("BASE_TEXTURE_FOLDER"), 50, H-125, 390, 20, _CONFIG["BASE_TEXTURE_FOLDER"],    390, "import path")
    E["BROWSE_TEXBASE"]         = Draw.PushButton('...',addEvent("BROWSE_TEXBASE"),     440, H-125,  30, 20)
    E["TEXTURE_SEARCH_PATH"]    = Draw.String("",       addEvent("TEXTURE_SEARCH_PATH"), 50, H-150, 390, 20, texpathString,                     390, "texture search path")
    E["BROWSE_TEXPATH"]         = Draw.PushButton('...',addEvent("BROWSE_TEXPATH"),     440, H-150,  30, 20)
    E["TEXPATH_ITEM"]           = Draw.String("",       addEvent("TEXPATH_ITEM"),        50, H-170, 360, 20, texpathItemString,                 290)
    E["TEXPATH_PREV"]           = Draw.PushButton('<',  addEvent("TEXPATH_PREV"),       410, H-170,  20, 20)
    E["TEXPATH_NEXT"]           = Draw.PushButton('>',  addEvent("TEXPATH_NEXT"),       430, H-170,  20, 20)
    E["TEXPATH_REMOVE"]         = Draw.PushButton('X',  addEvent("TEXPATH_REMOVE"),     450, H-170,  20, 20)
    E["REALIGN_BONES"]          = Draw.Toggle(" ",      addEvent("REALIGN_BONES"),       50, H-200,  20, 20, _CONFIG["REALIGN_BONES"])
    # To draw text on the screen I have to position its start point first
    #BGL.glRasterPos2i( 75, H-195)
    #Draw.Text("try to realign bones")
    guiText("try to realign bones", 75, H-195)
    
    E["CANCEL"]                 = Draw.PushButton('cancel',addEvent("CANCEL"),  50, H-225, 100, 20)
    E["OK"]                     = Draw.PushButton('ok',    addEvent("OK"),  50, H-250, 100, 20)
    # Sets the GUI elements to a global var to avoid them going out of scope (cases segfaults)
    _GUI_ELEMENTS = E
    Draw.Redraw(1)

def buttonEvent(evt):
    """
    Event handler for buttons
    """
    global _GUI_EVENTS, _CONFIG, _CONFIG_BACK, _IDX_TEXPATH
    evName = _GUI_EVENTS[evt]
    if evName == "OK":
        save()
        exitGUI()
    elif evName == "CANCEL":
        _CONFIG = _CONFIG_BACK
        save()
        exitGUI()
    elif evName == "REALIGN_BONES":
        _CONFIG["REALIGN_BONES"] = not _CONFIG["REALIGN_BONES"]
    elif evName == "BROWSE_IMPORT_PATH":
        # browse import path
        print _CONFIG["NIF_IMPORT_PATH"]
        Blender.Window.FileSelector(setImportPath, "set import path", _CONFIG["NIF_IMPORT_PATH"])
    elif evName == "BROWSE_EXPORT_PATH":
        # browse import path
        Blender.Window.FileSelector(setExportPath, "set export path", _CONFIG["NIF_EXPORT_PATH"])
    elif evName == "BROWSE_TEXBASE":
        # browse and add texture search path
        Blender.Window.FileSelector(setTextureBase, "set texture base folder")
    elif evName == "BROWSE_TEXPATH":
        # browse and add texture search path
        Blender.Window.FileSelector(addTexturePath, "add texture search path")
    elif evName == "TEXPATH_NEXT":
        if _IDX_TEXPATH < (len(_CONFIG["TEXTURE_SEARCH_PATH"])-1):
            _IDX_TEXPATH += 1
    elif evName == "TEXPATH_PREV":
        if _IDX_TEXPATH > 0:
            _IDX_TEXPATH -= 1
    elif evName == "TEXPATH_REMOVE":
        if _IDX_TEXPATH in xrange(len(_CONFIG["TEXTURE_SEARCH_PATH"])):
            del _CONFIG["TEXTURE_SEARCH_PATH"][_IDX_TEXPATH]
        if _IDX_TEXPATH > 0:
            _IDX_TEXPATH-=1
    else:
        None
    Draw.Redraw(1)

def event(evt, val):
    """
    Event handler for GUI elements
    """
    global _GUI_EVENTS
    #print  "event(%i,%i)"%(arg1,arg2)
    if evt == Draw.ESCKEY:
        exitGUI()

def openGUI(back_target=None):
    """
    Opens the config GUI
    """
    # defines what script called the config screen
    global _BACK_TARGET
    _BACK_TARGET = back_target
    load()
    Draw.Register(gui, event, buttonEvent)
    
def exitGUI():
    """
    Closes the config GUI
    """
    global _BACK_TARGET
    Draw.Exit()
    if _BACK_TARGET == "Import":
        Read.openGUI()
    elif _BACK_TARGET == "Export":
        Write.openGUI()

def save():
    """
    Saves the current configuration
    """
    global _CONFIG, _CONFIG_BACK, _CONFIG_NAME
    #print "datadir", Blender.Get('datadir'), "\n\n"
    #print "--",_CONFIG_NAME, _CONFIG, "\n\n"
    Registry.SetKey(_CONFIG_NAME, _CONFIG, True)
    load()
    _CONFIG_BACK = _CONFIG
    

def load():
    """
    Loads the stored configuration and checks saved configuration for incompatible values
    """
    # both loads and cleans up the configuration from the registry
    global _CONFIG, _CONFIG_NAME
    reload(Defaults)
    # I'll do something smarter with dir() here
    _CONFIG = {
        'NIF_IMPORT_PATH'          : Defaults._NIF_IMPORT_PATH, \
        'NIF_EXPORT_PATH'          : Defaults._NIF_EXPORT_PATH, \
        'NIF_IMPORT_FILE'          : Defaults._NIF_IMPORT_FILE, \
        'NIF_EXPORT_FILE'          : Defaults._NIF_EXPORT_FILE, \
        'TEXTURE_SEARCH_PATH'      : Defaults._TEXTURE_SEARCH_PATH, \
        'REALIGN_BONES'            : Defaults._REALIGN_BONES, \
        'IMPORT_SCALE_CORRECTION'  : Defaults._IMPORT_SCALE_CORRECTION, \
        'EXPORT_SCALE_CORRECTION'  : Defaults._EXPORT_SCALE_CORRECTION, \
        'BASE_TEXTURE_FOLDER'      : Defaults._BASE_TEXTURE_FOLDER, \
        'EXPORT_TEXTURE_PATH'      : Defaults._EXPORT_TEXTURE_PATH, \
        'EPSILON'                  : Defaults._EPSILON, \
        'VERBOSE'                  : Defaults._VERBOSE}
    oldConfig = Blender.Registry.GetKey(_CONFIG_NAME, True)
    #print "oldConfig", oldConfig, "\n\n"
    newConfig = {}
    for key, val in _CONFIG.iteritems():
        try:
            newConfig[key] = oldConfig[key]
        except:
            newConfig[key] = val
    #print "newConfig", newConfig, "\n\n"
    _CONFIG = newConfig
    _CONFIG_BACK = newConfig
    Blender.Registry.SetKey(_CONFIG_NAME, _CONFIG, True)
