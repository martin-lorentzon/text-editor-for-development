bl_info = {
    "name": "Template Add-on Name",
    "description": "Template add-on description.",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > N Panel > Hello World",
    # "doc_url": "https://github.com/{username}/{repo-name}",
    # "tracker_url": "https://github.com/{username}/{repo-name}/issues",
    # "warning": "Pre-Release",
    "support": "COMMUNITY",
    "category": "Choose a category",  # Try to fit into an existing category (or use your department's name)
}

"""
Make sure to update package.bat with the path to your Blender executable
"""

# ——————————————————————————————————————————————————————————————————————
# MARK: IMPORTS
# ——————————————————————————————————————————————————————————————————————


# fmt: off
if "bpy" in locals():
    from importlib import reload

    # Modules to reload during development go here
    reload(addon_preferences)
    reload(hello_world_module)
else:
    # ...and here
    from . import addon_preferences
    from . import hello_world_module

# ...but not here
import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


# Classes Blender should know about go in this list
classes = [
    addon_preferences.TemplatePreferences,
    hello_world_module.HelloWorldProperties,
    hello_world_module.TEMPLATE_PT_hello_world_panel,
    hello_world_module.TEMPLATE_OT_hello_world_operator,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.hello_world_properties = bpy.props.PointerProperty(type=hello_world_module.HelloWorldProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.hello_world_properties


if __name__ == "__main__":
    register()
