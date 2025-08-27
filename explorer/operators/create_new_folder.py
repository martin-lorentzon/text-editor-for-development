from bpy.types import Operator
from bpy.props import StringProperty
from ...helpers import uninitialized_preference
from ..helpers import disable_on_empty_folder_path, require_valid_open_folder, refresh_folder_view
from ..functions import contextual_parent_folder, unique_path
from ... import __package__ as base_package
from pathlib import Path


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_create_new_folder(Operator):
    bl_idname = "wm.explorer_create_new_folder"
    bl_label = "Create New Folder"
    bl_description = "Create a new folder in the currently opened or active directory"
    bl_options = {"INTERNAL"}

    new_folder_name: StringProperty(
        name="Folder Name",
        description="The name of the folder to be created",
        default=""
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        addon_prefs = context.preferences.addons[base_package].preferences

        if self.new_folder_name == "":
            self.new_folder_name = uninitialized_preference(addon_prefs, "default_new_folder_name")

        parent_folder = contextual_parent_folder()

        new_folder: Path = parent_folder / self.new_folder_name
        unique_new_folder = unique_path(new_folder)

        unique_new_folder.mkdir()

        refresh_folder_view(new_file_path=new_folder)
        return {"FINISHED"}