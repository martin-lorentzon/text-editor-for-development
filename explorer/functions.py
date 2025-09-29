import bpy
from ..helpers import uninitialized_preference
from .. import __package__ as base_package
from pathlib import Path


def find_file_path_index(file_path: Path | str, default=0):
    """**Warning: Expensive | Some of these should likely be phased out**"""
    wm = bpy.context.window_manager
    folder_view_list = wm.explorer_properties.folder_view_list
    return next((i for i, file in enumerate(folder_view_list) if file.file_path == str(file_path)), default)


def file_path_at_index(index: int):
    """**Warning: Expensive | Some of these should likely be phased out**"""
    wm = bpy.context.window_manager
    folder_view_list = wm.explorer_properties.folder_view_list
    if index >= len(folder_view_list):
        raise ValueError(f"[file_path_at_index] Index ({index}) out of range")
    return Path(folder_view_list[index].file_path)


def text_at_index(index: int):
    """**Warning: Expensive | Some of these should likely be phased out**"""
    wm = bpy.context.window_manager
    folder_view_list = wm.explorer_properties.folder_view_list
    if index >= len(folder_view_list):
        raise ValueError(f"[text_at_index] Index ({index}) out of range")
    texts = bpy.data.texts
    file = Path(folder_view_list[index].file_path)
    return next((t for t in texts if Path(t.filepath).resolve() == file.resolve()), None)


def text_at_file_path(file_path: Path | str):
    """
    Exists because getting texts by their name isn't enough -> bpy.data.texts.get(file.name)  
    Files of different hierarchical levels often share the same name, __init__.py e.g, hence this is needed  
    **Warning: Expensive | Some of these should likely be phased out**
    """
    texts = bpy.data.texts
    return next((t for t in texts if Path(t.filepath).resolve() == Path(file_path).resolve()), None)


def restore_active_file(func):
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

        # Restore active index if possible
        if active_file_path is None:
            new_idx = 0
        else:
            new_idx = find_file_path_index(active_file_path, default=file_clicked_on)

        props.folder_view_active_index = new_idx
        return result
    return wrapper


@restore_active_file
def open_folder(folder_path: Path | str, creation_idx=0, depth=0, file_clicked_on=0):
    """
    **Low-level**  
    Prefer higher level alternatives:  
    WindowManager.explorer_properties.open_folder_path  
    and  
    refresh_folder_view()
    """
    context = bpy.context
    wm = context.window_manager
    addon_prefs = context.preferences.addons[base_package].preferences
    props = wm.explorer_properties
    expanded_folder_paths: set = wm.expanded_folder_paths

    if folder_path == "":
        props.folder_view_list.clear()
        expanded_folder_paths.clear()
        return

    # Remove any expanded folder paths that don't exist
    expanded_folders = list(expanded_folder_paths)
    for path in expanded_folders:
        if not Path(path).exists():
            expanded_folder_paths.discard(path)

    if creation_idx == 0:
        props.folder_view_list.clear()

    files = sorted(
        Path(folder_path).iterdir(),
        key=lambda f: (
            not f.is_dir(),  # Folders first
            f.name.lower()   # Then sort by name
        )
    )

    show_hidden_items = uninitialized_preference(addon_prefs, "show_hidden_items")

    for file in files:
        if file.name.startswith(".") and not show_hidden_items:
            continue
        item = props.folder_view_list.add()
        item.file_path = str(file)
        item.file_name = file.name
        item.file_type = file.suffix.lower()
        item.name = file.name
        item.depth = depth
        item.creation_idx = creation_idx
        item.text_ref = text_at_file_path(item.file_path)
        creation_idx += 1

        if item.file_path in expanded_folder_paths and file.is_dir():
            creation_idx = open_folder(file, creation_idx=creation_idx, depth=depth+1)
    return creation_idx  # Ensure index continuity


def contextual_parent_folder():
    context = bpy.context
    wm = context.window_manager
    props = wm.explorer_properties
    expanded_folder_paths = wm.expanded_folder_paths
    folder_view_list = props.folder_view_list

    if len(folder_view_list) < 1:  # Return the open folder if there are no items
        return Path(props.open_folder_path)

    active_idx = props.folder_view_active_index

    if not 0 <= active_idx < len(folder_view_list):  # Return the open folder if the active index is invalid
        return Path(props.open_folder_path)

    active_item = props.folder_view_list[active_idx]

    if active_item.file_path in expanded_folder_paths:
        parent_folder = Path(active_item.file_path)
    else:
        parent_folder = Path(active_item.file_path).parent
    return parent_folder


def unique_path(path: Path | str) -> Path:
    destination = Path(path)
    parent = destination.parent
    original_stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while destination.exists():
        destination = parent / f"{original_stem} ({counter}){suffix}"
        counter += 1
    return destination
