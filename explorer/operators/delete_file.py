import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ...helpers import uninitialized_preference
from ..helpers import (
    disable_on_empty_folder_path, 
    require_valid_open_folder, 
    require_valid_active_file, 
    refresh_folder_view
    )
from ..functions import text_at_file_path
from ... import __package__ as base_package
from pathlib import Path
from send2trash import send2trash


@disable_on_empty_folder_path
@require_valid_open_folder
@require_valid_active_file
class EXPLORER_OT_delete_file(Operator):
    bl_idname = "wm.explorer_delete_file"
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

        def unlink_contents_recursive(folder: Path):
            for item in folder.iterdir():
                if not item.exists():
                    continue

                if item.is_dir():
                    unlink_contents_recursive(item)
                else:
                    text = text_at_file_path(item)

                    if text is not None:
                        bpy.data.texts.remove(text)

        if is_folder:
            if uninitialized_preference(addon_prefs, "unlink_on_file_deletion"):
                unlink_contents_recursive(file)
            send2trash(file)
        else:
            if uninitialized_preference(addon_prefs, "unlink_on_file_deletion"):
                text = text_at_file_path(file)
                if text is not None:
                    bpy.data.texts.remove(text)
            send2trash(file)

        props = context.window_manager.explorer_properties
        folder_view_list = props.folder_view_list
        active_idx = props.folder_view_active_index

        refresh_folder_view()

        # Calculate new active index
        new_active_idx = min(active_idx, len(folder_view_list) - 1)
        props.folder_view_active_index = new_active_idx
        return {"FINISHED"}
