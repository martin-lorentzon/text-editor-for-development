from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty


class TemplatePreferences(AddonPreferences):  # {AddonNamePreferences}
    bl_idname = __package__

    setting_1: StringProperty(
        name="Setting 1",
        subtype="DIR_PATH"
    )
    setting_2: BoolProperty(
        name="Setting 2"
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "setting_1")
        layout.prop(self, "setting_2")
