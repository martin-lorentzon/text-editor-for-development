import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty


class TextEditorForDevelopmentPreferences(AddonPreferences):
    bl_idname = __package__

    default_file_name: StringProperty(  # TODO: Connect these to the create file/folder operators
        name="Default File Name",
        default="my_script.py"
    )
    default_folder_name: StringProperty(
        name="Default Folder Name",
        default="new_folder.py"
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        header, panel = layout.panel("explorer_prefs", default_closed=False)
        header.label(text="Explorer")
        if panel:
            panel.prop(self, "default_file_name")
            panel.prop(self, "default_folder_name")


def register():
    bpy.utils.register_class(TextEditorForDevelopmentPreferences)


def unregister():
    bpy.utils.unregister_class(TextEditorForDevelopmentPreferences)
