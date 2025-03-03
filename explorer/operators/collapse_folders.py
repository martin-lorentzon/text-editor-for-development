from bpy.types import Operator
from .. import expanded_folder_paths
from ..helpers import disable_on_empty_folder_path, require_valid_open_folder
from ..functions import refresh_folder_view


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_collapse_folders(Operator):
    bl_idname = "text.collapse_folders"
    bl_label = "Collapse Folders in Explorer"
    bl_description = "Display only the top-level contents of the opened folder"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.explorer_properties
        return len(props.folder_view_list) > 0

    def execute(self, context):
        global expanded_folder_paths

        expanded_folder_paths = set()
        refresh_folder_view()
        return {"FINISHED"}