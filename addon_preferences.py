import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty
from .explorer.helpers import refresh_folder_view
from pathlib import Path
from . import constants


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

    def get_comments_color(self):
        return self.get("comments_color", "BLENDER_DEFAULT")
    
    def set_comments_color(self, value):
        self["comments_color"] = value
        enum_prop = self.bl_rna.properties["comments_color"]
        color = constants.COMMENTS_COLORS[enum_prop.enum_items[value].identifier]
        bpy.context.preferences.themes[0].text_editor.syntax_comment = color

    comments_color: EnumProperty(
        name="Comments Color",
        items=[
            ("BLENDER_DEFAULT", "Blender Default (Gray)", ""),
            ("VSCODE",          "VSCode (Dark Green)",    ""),
            ("LIGHT_GREEN",     "Light Green",            "")
        ],
        default="BLENDER_DEFAULT",
        get=get_comments_color,
        set=set_comments_color
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        text_edit_header, text_editor_panel = layout.panel("text_editor_prefs", default_closed=False)
        text_edit_header.label(text="Text editor")

        if text_editor_panel:
            text_editor_panel.prop(self, "comments_color")

            explorer_header, explorer_panel = layout.panel("explorer_prefs", default_closed=False)
            explorer_header.label(text="Explorer")

            if explorer_panel:
                explorer_panel.prop(self, "default_new_file_name")
                explorer_panel.prop(self, "default_new_folder_name")
                explorer_panel.prop(self, "show_hidden_items")
                explorer_panel.prop(self, "unlink_on_file_deletion")


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


def register():
    bpy.utils.register_class(TextEditorForDevelopmentPreferences)


def unregister():
    bpy.utils.unregister_class(TextEditorForDevelopmentPreferences)