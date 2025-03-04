from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty


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
        wm = context.window_manager
        props = wm.explorer_properties

        wm.expanded_folder_paths.clear()
        props.open_folder_path = self.directory
        return {"FINISHED"}