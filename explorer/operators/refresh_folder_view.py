from bpy.types import Operator
from ..helpers import disable_on_empty_folder_path, require_valid_open_folder, refresh_folder_view


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_refresh_folder_view(Operator):
    bl_idname = "wm.explorer_refresh_folder_view"
    bl_label = "Refresh Open Folder"
    bl_description = "Update the displayed contents of the folder view"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        refresh_folder_view()
        return {"FINISHED"}