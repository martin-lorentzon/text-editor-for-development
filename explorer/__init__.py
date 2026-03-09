# fmt: off
if "bpy" in locals():
    from importlib import reload

    reload(constants)
    reload(functions)
    reload(helpers)
    reload(properties)
    reload(ui)
    reload(open_folder)
    reload(refresh_folder_view)
    reload(create_new_file)
    reload(create_new_folder)
    reload(toggle_expand_folder)
    reload(collapse_folders)
    reload(delete_file)
else:
    from . import constants
    from . import functions
    from . import helpers
    from . import properties
    from . import ui
    from .operators import (
        open_folder,
        refresh_folder_view,
        create_new_file,
        create_new_folder,
        toggle_expand_folder,
        collapse_folders,
        delete_file
    )


import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


modules = [
    properties,
    ui,
    open_folder,
    refresh_folder_view,
    create_new_file,
    create_new_folder,
    toggle_expand_folder,
    collapse_folders,
    delete_file,
]


def register():
    for module in modules:
        module.register()

    bpy.types.WindowManager.explorer_properties = bpy.props.PointerProperty(
        type=properties.ExplorerProperties,
        name="Explorer"
    )

    bpy.types.WindowManager.expanded_folder_paths = set()


def unregister():
    for module in reversed(modules):
        module.unregister()

    del bpy.types.WindowManager.explorer_properties
    del bpy.types.WindowManager.expanded_folder_paths
