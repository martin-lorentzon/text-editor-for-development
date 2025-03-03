from bpy.types import Operator
from bpy.props import StringProperty
from ..helpers import disable_on_empty_folder_path, require_valid_open_folder
from ..functions import find_file_path_index, open_folder
from ..properties import expanded_folder_paths
from pathlib import Path


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_toggle_expand_folder(Operator):
    bl_idname = "text.toggle_expand_folder"
    bl_label = "Expand Folder"
    bl_description = "Show the contents of this folder"
    bl_options = {"INTERNAL"}

    folder_path: StringProperty()

    def execute(self, context):
        global expanded_folder_paths

        props = context.window_manager.explorer_properties
        file_clicked_on = find_file_path_index(self.folder_path, 0)

        if self.folder_path in expanded_folder_paths:
            expanded_folder_paths.discard(self.folder_path)
        else:
            expanded_folder_paths.add(self.folder_path)

        open_folder(Path(props.open_folder_path), file_clicked_on=file_clicked_on)
        return {"FINISHED"}