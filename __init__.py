"""
MAP Importer
-
Import symbol names from .map files
"""

from binaryninja import *



def parse_address_name(line):
    line = line.strip()
    section, remain = line.split(":")
    section = int(section)
    address, name = remain.split()
    address = int("0x" + address, 16)
    return (section, address, name)

def importMap(mapfile, binaryView):
    data = []
    code = []
    stage = 0
    with open(mapfile, "r") as fd:
        for line in fd.readlines():
            if stage == 0:
                if "Publics by Value" in line:
                    stage = 1
                    continue
            if stage == 1:
                if len(line.split()) == 0:
                    continue
                stage = 2
                data.append(parse_address_name(line))
            elif stage == 2:
                if len(line.split()) == 0:
                    break
                data.append(parse_address_name(line))
    
    for section, address, name in data:
        print("{} {}, {}".format(section, hex(address), name))
        if section == 3:
            stype = SymbolType.FunctionSymbol
        else:
            stype = SymbolType.DataSymbol
        binaryView.define_user_symbol(Symbol(stype, address, name))

    show_message_box("Map Import Successful", "Symbols from the .map file have been successfully imported. ", MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.InformationIcon)

    return True, None


def importMapWrap(binaryView):
    # This is the string that's displayed in the pop-up dialogue by binja itself
    mapFile = OpenFileNameField("Import Map")

    # Sets the title of the dialogue and gets the input field value
    get_form_input([mapFile], "IDC Import Options")

    filename = None

    if mapFile.result != '':
        filename = mapFile.result

    if len(mapFile.result) < 4:
        show_message_box("Error from MAP Importer", "The MAP file you've given is invalid. ", MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.ErrorIcon)
        return

    (success, err) = importMap(filename, binaryView)

    if success:
        log_info("Map import completed successfully.")
    else:
        log_error(err)


PluginCommand.register("Import MAP File", "Import symbols from .map files", importMapWrap)
