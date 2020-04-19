# RenPy script file
# Config changes; written by UnRen

init 999 python:
    try:
        config.underlay[0].keymap['quickLoad'] = QuickLoad()
        config.keymap['quickLoad'] = 'K_F5'
        config.underlay[0].keymap['quickSave'] = QuickSave()
        config.keymap['quickSave'] = 'K_F9'
    except:
        print("Error: Quicksave/-load not working.")
