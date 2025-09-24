bl_info = {
    "name": "Text editor for Development",
    "description": "Text editor enhancements for add-on development",
    "author": "Martin Lorentzon",
    "version": (1, 0, 4),
    "blender": (4, 5, 0),
    "location": "Text Editor > Sidebar > Dev",
    "doc_url": "https://github.com/martin-lorentzon/text-editor-for-development",
    "tracker_url": "https://github.com/martin-lorentzon/text-editor-for-development/issues",
    # "warning": "",
    "support": "COMMUNITY",
    "category": "Development",
}


# ——————————————————————————————————————————————————————————————————————
# MARK: IMPORTS
# ——————————————————————————————————————————————————————————————————————


# fmt: off
if "bpy" in locals():
    from importlib import reload

    reload(constants)
    reload(addon_preferences)
    reload(explorer)
    reload(remote_content)
else:
    from . import constants
    from . import addon_preferences
    from . import explorer
    from . import remote_content

import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


modules = [
    addon_preferences,
    explorer,
    remote_content
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()


if __name__ == "__main__":
    register()
