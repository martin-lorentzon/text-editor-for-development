import bpy
from bpy.types import Operator
from .functions import open_folder, find_file_path_index
from pathlib import Path


def refresh_folder_view(
        file_clicked_on: int = 0, 
        new_file_path: Path | str | None = None, 
        redraw_only: bool = False
        ):
    context = bpy.context
    props = context.window_manager.explorer_properties

    if not redraw_only:
        open_folder(
            folder_path=props.open_folder_path,
            file_clicked_on=file_clicked_on  # Currently used in expanding/collapsing folders
            )

    if new_file_path is not None:  # Used when new files are added
        props.folder_view_active_index = find_file_path_index(new_file_path)

    for area in context.screen.areas:
        if area.type == "TEXT_EDITOR":
            for region in area.regions:
                if region.type == "UI":
                    region.tag_redraw()


# ——————————————————————————————————————————————————————————————————————
# MARK: DECORATORS
# ——————————————————————————————————————————————————————————————————————


def disable_on_empty_folder_path(cls):
    original_poll = getattr(cls, "poll", None)

    @classmethod
    def poll(cls, context):
        props = context.window_manager.explorer_properties

        if original_poll:
            return original_poll(context) and props.open_folder_path != ""
        return props.open_folder_path != ""

    cls.poll = poll
    return cls


def require_valid_open_folder(cls):
    original_invoke = getattr(cls, "invoke", None)

    def invoke(self: Operator, context, event):
        props = context.window_manager.explorer_properties
        folder = Path(props.open_folder_path)

        # New invoke logic
        if folder.is_dir() == False:
            self.report({"ERROR"}, "The selected opened folder no longer exists or is not a directory.")
            props.open_folder_path = ""
            refresh_folder_view()
            return {"CANCELLED"}
        
        if original_invoke:  # Existing invoke
            return original_invoke(self, context, event)
        
        # Default invoke logic
        return self.execute(context)

    cls.invoke = invoke
    return cls


def require_valid_active_file(cls):
    original_invoke = getattr(cls, "invoke", None)

    def invoke(self: Operator, context, event):
        props = context.window_manager.explorer_properties
        file = Path(props.folder_view_list[props.folder_view_active_index].file_path)

        if file.exists() == False:
            self.report({"ERROR"}, "The active item no longer exists.")
            refresh_folder_view()
            return {"CANCELLED"}
        
        if original_invoke:
            return original_invoke(self, context, event)
        
        return self.execute(context)

    cls.invoke = invoke
    return cls
