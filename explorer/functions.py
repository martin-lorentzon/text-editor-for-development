import bpy
from .properties import expanded_folder_paths
from pathlib import Path


def find_file_path_index(file_path: Path | str, default=0):
    folder_view_list = bpy.context.window_manager.explorer_properties.folder_view_list
    return next((i for i, file in enumerate(folder_view_list) if file.file_path == str(file_path)), default)


def restore_active_file_decorator(func):
    def wrapper(*args, **kwargs):
        context = bpy.context
        props = context.window_manager.explorer_properties

        folder_view_list = props.folder_view_list
        active_idx = props.folder_view_active_index
        file_clicked_on: int = kwargs.get("file_clicked_on", 0)

        if 0 <= active_idx < len(folder_view_list):
            active_file_path = folder_view_list[active_idx].file_path
        else:
            active_file_path = None

        result = func(*args, **kwargs)  # Original function call

        # Restore active file path if possible
        if active_file_path is None:
            new_idx = 0
        else:
            new_idx = find_file_path_index(active_file_path, file_clicked_on)

        props.folder_view_active_index = new_idx
        return result
    return wrapper


@restore_active_file_decorator
def open_folder(folder_path: Path | str, creation_idx=0, depth=0, file_clicked_on=0):
    global expanded_folder_paths

    # TODO: Remove file paths from expanded_folder_paths if they don't exist on disk

    context = bpy.context
    props = context.window_manager.explorer_properties

    if creation_idx == 0:
        props.folder_view_list.clear()

    files = sorted(
        Path(folder_path).iterdir(),
        key=lambda f: (
            not f.is_dir(),  # Folders first
            f.name.lower()   # Then sort by name
        )
    )

    for file in files:
        item = props.folder_view_list.add()
        item.file_path = str(file)
        item.file_name = file.name
        item.file_type = file.suffix.lower()
        item.name = file.name
        item.depth = depth
        item.creation_idx = creation_idx
        creation_idx += 1

        if item.file_path in expanded_folder_paths and file.is_dir():
            creation_idx = open_folder(file, creation_idx=creation_idx, depth=depth+1)
    return creation_idx  # Ensure index continuity


def refresh_folder_view(new_file_path: Path | str | None = None):
    context = bpy.context
    props = context.window_manager.explorer_properties

    open_folder(props.open_folder_path)

    if new_file_path is not None:
        props.folder_view_active_index = find_file_path_index(new_file_path)

    context.area.tag_redraw()


def contextual_parent_folder():
    props = bpy.context.window_manager.explorer_properties
    folder_view_list = props.folder_view_list

    if len(folder_view_list) < 1:  # Return open folder if there are no subfolders
        return Path(props.open_folder_path)

    active_idx = props.folder_view_active_index
    if not 0 <= active_idx < len(folder_view_list):
        return
    active_item = props.folder_view_list[active_idx]

    if active_item.file_path in expanded_folder_paths:
        parent_folder = Path(active_item.file_path)
    else:
        parent_folder = Path(active_item.file_path).parent
    return parent_folder


def unique_path(destination: Path | str) -> Path:
    parent = destination.parent
    original_stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while destination.exists():
        destination = parent / f"{original_stem} ({counter}){suffix}"
        counter += 1
    return Path(destination)
