import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty
from pathlib import Path
from .explorer.helpers import refresh_folder_view
from .explorer import ui as explorer_ui
from . import constants


class TextEditorForDevelopmentPreferences(AddonPreferences):
    bl_idname = __package__

    def update_default_new_file_name(self, context):
        sanitized = str(Path(self.default_new_file_name).name)
        if self.default_new_file_name != sanitized:
            self.default_new_file_name = sanitized

    default_new_file_name: StringProperty(
        name="Default File Name",
        default="new_script.py",
        update=update_default_new_file_name
    )

    def update_default_new_folder_name(self, context):
        sanitized = str(Path(self.default_new_folder_name).stem)
        if self.default_new_folder_name != sanitized:
            self.default_new_folder_name = sanitized

    default_new_folder_name: StringProperty(
        name="Default Folder Name",
        default="new_folder",
        update=update_default_new_folder_name
    )

    def get_show_hidden_items(self):
        return self.internal_show_hidden_items

    def set_show_hidden_items(self, value):
        self.internal_show_hidden_items = value
        refresh_folder_view()

    internal_show_hidden_items: BoolProperty(
        name="Show Hidden Items",
    )

    show_hidden_items: BoolProperty(
        name="Show Hidden Items",
        get=get_show_hidden_items,
        set=set_show_hidden_items
    )

    unlink_on_file_deletion: BoolProperty(
        name="Unlink on File Deletion",
        default=True
    )

    def get_comments_color(self):
        enum_prop = self.bl_rna.properties["internal_comments_color"]
        items = enum_prop.enum_items
        return items[self.internal_comments_color].value if self.internal_comments_color in items else 0

    def set_comments_color(self, value):
        enum_prop = self.bl_rna.properties["internal_comments_color"]
        items = enum_prop.enum_items
        identifier = items[value].identifier
        color = constants.COMMENTS_COLORS[identifier]
        bpy.context.preferences.themes[0].text_editor.syntax_comment = color
        self.internal_comments_color = identifier

    comments_colors = [
        ("BLENDER_DEFAULT", "Blender Default (Gray)", ""),
        ("VSCODE",          "VSCode (Dark Green)",    ""),
        ("LIGHT_GREEN",     "Light Green",            "")
    ]

    internal_comments_color: EnumProperty(
        name="Comments Color",
        items=comments_colors,
    )

    comments_color: EnumProperty(
        name="Comments Color",
        items=comments_colors,
        get=get_comments_color,
        set=set_comments_color
    )

    def update_explorer_category(self, value):
        explorer_ui.unregister()
        explorer_ui.register()

    explorer_category: StringProperty(
        name="Explorer Category",
        default="Explorer",
        update=update_explorer_category
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        text_edit_header, text_editor_panel = layout.panel(
            "text_editor_prefs", default_closed=True)
        text_edit_header.label(text="Text editor")

        if text_editor_panel:
            text_editor_panel.prop(self, "comments_color")

        explorer_header, explorer_panel = layout.panel(
            "explorer_prefs", default_closed=True)
        explorer_header.label(text="Explorer")

        if explorer_panel:
            explorer_panel.prop(self, "explorer_category")
            explorer_panel.prop(self, "default_new_file_name")
            explorer_panel.prop(self, "default_new_folder_name")
            explorer_panel.prop(self, "show_hidden_items")
            explorer_panel.prop(self, "unlink_on_file_deletion")


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


register, unregister = bpy.utils.register_classes_factory((TextEditorForDevelopmentPreferences,))
