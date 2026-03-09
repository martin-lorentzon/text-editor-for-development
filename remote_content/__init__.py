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


modules = [
    clone_repository,
]


def register():
    for module in modules:
        module.register()

    bpy.types.TEXT_MT_templates.append(ui.draw_func)


def unregister():
    for module in reversed(modules):
        module.unregister()

    bpy.types.TEXT_MT_templates.remove(ui.draw_func)
