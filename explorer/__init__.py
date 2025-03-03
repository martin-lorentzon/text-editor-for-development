# ——————————————————————————————————————————————————————————————————————
# MARK: IMPORTS
# ——————————————————————————————————————————————————————————————————————


# fmt: off
if "bpy" in locals():
    from importlib import reload

    reload(FileItemProperties)
    reload(ExplorerProperties)
    reload(EXPLORER_UL_folder_view_list)
    reload(EXPLORER_PT_explorer_panel)
    reload(EXPLORER_OT_open_folder)
    reload(EXPLORER_OT_refresh_folder_view)
    reload(EXPLORER_OT_create_new_file)
    reload(EXPLORER_OT_create_new_folder)
    reload(EXPLORER_OT_toggle_expand_folder)
    reload(EXPLORER_OT_collapse_folders)
    reload(EXPLORER_OT_delete_file)
else:
    from .properties import FileItemProperties, ExplorerProperties
    from .ui import EXPLORER_UL_folder_view_list
    from .ui import EXPLORER_PT_explorer_panel
    from .operators.open_folder import EXPLORER_OT_open_folder
    from .operators.refresh_folder_view import EXPLORER_OT_refresh_folder_view
    from .operators.create_new_file import EXPLORER_OT_create_new_file
    from .operators.create_new_folder import EXPLORER_OT_create_new_folder
    from .operators.toggle_expand_folder import EXPLORER_OT_toggle_expand_folder
    from .operators.collapse_folders import EXPLORER_OT_collapse_folders
    from .operators.delete_file import EXPLORER_OT_delete_file


import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


classes = [
    FileItemProperties,
    ExplorerProperties,
    EXPLORER_UL_folder_view_list,
    EXPLORER_PT_explorer_panel,
    EXPLORER_OT_open_folder,
    EXPLORER_OT_refresh_folder_view,
    EXPLORER_OT_create_new_file,
    EXPLORER_OT_create_new_folder,
    EXPLORER_OT_toggle_expand_folder,
    EXPLORER_OT_collapse_folders,
    EXPLORER_OT_delete_file
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.WindowManager.explorer_properties = bpy.props.PointerProperty(
        type=ExplorerProperties,
        name="Explorer"
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.WindowManager.explorer_properties