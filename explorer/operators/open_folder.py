import bpy
from bpy.props import StringProperty, BoolProperty
from pathlib import Path
from ..properties import INVALID_OPEN_FOLDER_MSG


class EXPLORER_OT_open_folder(bpy.types.Operator):
    bl_idname = "wm.explorer_open_folder"
    bl_label = "Open Folder"
    bl_description = "Quickly search all files in the current folder"
    bl_options = {"INTERNAL"}

    directory: StringProperty(
        name="Directory",
        description="The folder to open",
        subtype="DIR_PATH"
    )

    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}  # Hides filtered-out objects (non-folders)
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        wm = context.window_manager
        props = wm.explorer_properties

        folder = Path(self.directory)

        if folder.is_dir() == False:
            self.report({"ERROR"}, INVALID_OPEN_FOLDER_MSG.format(folder=self.directory))
            return {"CANCELLED"}

        wm.expanded_folder_paths.clear()
        props.open_folder_path = self.directory
        return {"FINISHED"}


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


register, unregister = bpy.utils.register_classes_factory((EXPLORER_OT_open_folder,))
