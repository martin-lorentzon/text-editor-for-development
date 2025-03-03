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

    reload(register_explorer)
    reload(unregister_explorer)
else:
    from .explorer import register as register_explorer, unregister as unregister_explorer

import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


def register():
    register_explorer()


def unregister():
    unregister_explorer()


if __name__ == "__main__":
    register()
