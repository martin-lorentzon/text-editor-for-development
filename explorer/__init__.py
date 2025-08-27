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


classes = [
    properties.FileItemProperties,
    properties.ExplorerProperties,
    ui.EXPLORER_UL_folder_view_list,
    ui.EXPLORER_PT_explorer_panel,
    open_folder.EXPLORER_OT_open_folder,
    refresh_folder_view.EXPLORER_OT_refresh_folder_view,
    create_new_file.EXPLORER_OT_create_new_file,
    create_new_folder.EXPLORER_OT_create_new_folder,
    toggle_expand_folder.EXPLORER_OT_toggle_expand_folder,
    collapse_folders.EXPLORER_OT_collapse_folders,
    delete_file.EXPLORER_OT_delete_file
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.explorer_properties = bpy.props.PointerProperty(
        type=properties.ExplorerProperties,
        name="Explorer"
    )

    bpy.types.WindowManager.expanded_folder_paths = set()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.explorer_properties
    del bpy.types.WindowManager.expanded_folder_paths
