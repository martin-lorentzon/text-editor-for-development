from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from .. import expanded_folder_paths


class EXPLORER_OT_open_folder(Operator):
    bl_idname = "text.open_folder"
    bl_label = "Open Folder"
    bl_description = "Allows you to quickly search over all files in the currently opened folder"
    bl_options = {"INTERNAL"}

    directory: StringProperty(
        name="Directory",
        description="Folder to open"
    )

    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}  # Hides filtered-out objects
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        global expanded_folder_paths

        props = context.window_manager.explorer_properties

        expanded_folder_paths.clear()
        props.open_folder_path = self.directory
        return {"FINISHED"}