bl_info = {
    "name": "Text Editor for Development",
    "description": "Quality-of-life improvements for add-on developers.",
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
    from .addon_preferences import register as register_preferences, unregister as unregister_preferences
    from .explorer import register as register_explorer, unregister as unregister_explorer

import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


def register():
    register_preferences()
    register_explorer()


def unregister():
    unregister_preferences()
    unregister_explorer()


if __name__ == "__main__":
    register()
