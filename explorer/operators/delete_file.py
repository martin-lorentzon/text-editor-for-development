import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..helpers import disable_on_empty_folder_path, require_valid_open_folder
from ...helpers import uninitialized_preference
from ..functions import refresh_folder_view, text_at_file_path
from ... import __package__ as base_package
from pathlib import Path
from shutil import rmtree


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_delete_file(Operator):
    bl_idname = "text.delete_file"
    bl_label = "Delete File"
    bl_description = "Deletes the selected file"
    bl_options = {"INTERNAL"}

    file_path: StringProperty()

    def invoke(self, context, event):
        if event.shift:
            return self.execute(context)
        wm = context.window_manager

        file = Path(self.file_path)
        file_name = file.name
        title = f"Are you sure you want to delete {file_name}?"
        message = f"You can restore this {'folder' if file.is_dir() else 'file'} from the Recycle Bin."
        return wm.invoke_confirm(self, event, title=title, message=message, icon="INFO")

    def execute(self, context):
        addon_prefs = context.preferences.addons[base_package].preferences
        wm = context.window_manager

        wm.expanded_folder_paths.discard(self.file_path)

        file = Path(self.file_path)
        is_folder = file.is_dir()

        try:
            if is_folder:
                rmtree(file)
            else:
                file.unlink()
                if uninitialized_preference(addon_prefs, "unlink_on_file_deletion"):
                    text = text_at_file_path(file)
                    if text is not None:
                        bpy.data.texts.remove(text)
        except FileNotFoundError:
            message = f"File {self.file_path} doesn't exist."
            self.report({"ERROR"}, message)
            refresh_folder_view()
            return {"CANCELLED"}

        props = context.window_manager.explorer_properties
        folder_view_list = props.folder_view_list
        active_idx = props.folder_view_active_index

        refresh_folder_view()

        # Calculate new active index
        new_active_idx = min(active_idx, len(folder_view_list) - 1)
        props.folder_view_active_index = new_active_idx
        return {"FINISHED"}
