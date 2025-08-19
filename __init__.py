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
    reload(remote_content)
else:
    from . import addon_preferences
    from . import explorer
    from . import remote_content
    
    from .addon_preferences import register as register_preferences, unregister as unregister_preferences
    from .explorer import register as register_explorer, unregister as unregister_explorer
    from .remote_content import register as register_remote_content, unregister as unregister_remote_content

import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


def register():
    register_preferences()
    register_explorer()
    register_remote_content()


def unregister():
    unregister_preferences()
    unregister_explorer()
    unregister_remote_content()


if __name__ == "__main__":
    register()
