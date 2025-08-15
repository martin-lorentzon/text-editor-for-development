import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
from pathlib import Path


class TextEditorForDevelopmentPreferences(AddonPreferences):
    bl_idname = __package__

    default_new_file_name: StringProperty(
        name="Default File Name",
        default="new_script.py"
    )

    def get_default_folder_name(self):
        return self.get("default_new_folder_name", "")
    
    def set_default_folder_name(self, value):
        self["default_new_folder_name"] = str(Path(value).with_suffix(""))

    default_new_folder_name: StringProperty(
        name="Default Folder Name",
        default="new_folder",
        get=get_default_folder_name,
        set=set_default_folder_name
    )
    
    unlink_on_file_deletion: BoolProperty(
        name="Unlink on File Deletion",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        header, panel = layout.panel("explorer_prefs", default_closed=False)
        header.label(text="Explorer")
        if panel:
            panel.prop(self, "default_new_file_name")
            panel.prop(self, "default_new_folder_name")
            panel.prop(self, "unlink_on_file_deletion")


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


def register():
    bpy.utils.register_class(TextEditorForDevelopmentPreferences)


def unregister():
    bpy.utils.unregister_class(TextEditorForDevelopmentPreferences)