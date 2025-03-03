from bpy.types import Operator
from bpy.props import StringProperty
from ..helpers import disable_on_empty_folder_path, require_valid_open_folder
from ..functions import refresh_folder_view, contextual_parent_folder, unique_path
from pathlib import Path


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_create_new_file(Operator):
    bl_idname = "text.create_new_file"
    bl_label = "Create New File"
    bl_description = "Create a new file in the currently opened or active directory"
    bl_options = {"INTERNAL"}

    new_file_name: StringProperty(
        name="File Name",
        description="The name of the file to be created",
        default=""
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences

        if self.new_file_name == "":
            self.new_file_name = addon_prefs.get(
                "default_new_file_name", 
                addon_prefs.bl_rna.properties["default_new_file_name"].default
            )

        parent_folder = contextual_parent_folder()

        new_file: Path = parent_folder / self.new_file_name

        unique_new_file = unique_path(new_file)
        unique_new_file.touch(exist_ok=False)

        refresh_folder_view(new_file_path=new_file)
        return {"FINISHED"}