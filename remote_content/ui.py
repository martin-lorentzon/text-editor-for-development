from bpy.types import UILayout


def new_addon_draw(self, context):
    layout: UILayout = self.layout

    layout.separator()
    op = layout.operator("wm.clone_repository", text="New Add-on")
    op.title = "New Add-on"
    op.confirm_text = "Create New Add-on"
    op.repository_url = "https://github.com/martin-lorentzon/clean-blender-addon-template/"