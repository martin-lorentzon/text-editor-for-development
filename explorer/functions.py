import bpy
from pathlib import Path


def find_file_path_index(file_path: Path | str, default=0):
    folder_view_list = bpy.context.window_manager.explorer_properties.folder_view_list
    return next((i for i, file in enumerate(folder_view_list) if file.file_path == str(file_path)), default)


def file_path_at_index(index: int):
    folder_view_list = bpy.context.window_manager.explorer_properties.folder_view_list
    if index >= len(folder_view_list):
        raise ValueError(f"Couldn't get file path, index ({index}) not in range")
    return Path(folder_view_list[index].file_path)


def text_at_index(index: int):
    folder_view_list = bpy.context.window_manager.explorer_properties.folder_view_list
    if index >= len(folder_view_list):
        raise ValueError(f"Couldn't get text, index ({index}) not in range")
    texts = bpy.data.texts
    file = Path(folder_view_list[index].file_path)
    return next((t for t in texts if Path(t.filepath).resolve() == file.resolve()), None)


def text_at_file_path(file_path: Path | str):
    """
    Exists because getting texts by their name isn't enough >> bpy.data.texts.get(file.name)
    Files of different folders often share the same name, hence this is a safer approach and necessary.
    """
    texts = bpy.data.texts
    return next((t for t in texts if Path(t.filepath).resolve() == Path(file_path).resolve()), None)


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

        # Restore active index if possible
        if active_file_path is None:
            new_idx = 0
        else:
            new_idx = find_file_path_index(active_file_path, file_clicked_on)

        props.folder_view_active_index = new_idx
        return result
    return wrapper


@restore_active_file_decorator
def open_folder(folder_path: Path | str, creation_idx=0, depth=0, file_clicked_on=0):
    context = bpy.context
    wm = context.window_manager
    props = wm.explorer_properties
    expanded_folder_paths = wm.expanded_folder_paths

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
