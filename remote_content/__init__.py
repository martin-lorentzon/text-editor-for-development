# fmt: off
if "bpy" in locals():
    from importlib import reload

    reload(functions)
    reload(ui)
    reload(clone_repository)
else:
    from . import functions
    from . import ui
    from .operators import clone_repository

import bpy
# fmt: on


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


classes = [
    clone_repository.REMOTE_CONTENT_OT_clone_repository
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TEXT_MT_templates.append(ui.new_addon_draw)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.TEXT_MT_templates.remove(ui.new_addon_draw)
