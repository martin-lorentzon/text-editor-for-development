bl_info = {
    "name": "Text Editor for Development",
    "description": "Reimagining the Text Editor for new add-on developers.",
    "author": "Martin Lorentzon",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
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

    reload(addon_preferences)
    reload(explorer)
else:
    from . import addon_preferences
    from . import explorer

import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


modules = [
    addon_preferences,
    explorer
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()


if __name__ == "__main__":
    register()
