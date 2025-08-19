import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
from .explorer.functions import refresh_folder_view
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

    def get_show_hidden_items(self):
        return self.get("show_hidden_items", False)

    def set_show_hidden_items(self, value):
        self["show_hidden_items"] = value
        refresh_folder_view()
    
    show_hidden_items: BoolProperty(
        name="Show Hidden Items",
        default=False,
        get=get_show_hidden_items,
        set=set_show_hidden_items
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
            panel.prop(self, "show_hidden_items")
            panel.prop(self, "unlink_on_file_deletion")


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


def register():
    bpy.utils.register_class(TextEditorForDevelopmentPreferences)


def unregister():
    bpy.utils.unregister_class(TextEditorForDevelopmentPreferences)