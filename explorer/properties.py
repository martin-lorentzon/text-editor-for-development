import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty
from pathlib import Path
from .functions import unique_path, refresh_folder_view, open_folder, file_path_at_index, text_at_index, text_at_file_path


# ——————————————————————————————————————————————————————————————————————
# MARK: GETTERS/SETTERS
# ——————————————————————————————————————————————————————————————————————


# File name (GETTER/SETTER)
def get_file_name(self):
    return self["file_name"]


def set_file_name(self, value):
    source = Path(self.file_path)
    parent = source.parent
    destination: Path = parent / value

    if str(destination) == self.file_path:  # Is true for when the file is first loaded
        self["file_name"] = value
        return
    
    text = text_at_file_path(source)

    if text:
        bpy.data.texts.remove(text)

    unique_destination = unique_path(destination)
    source.rename(unique_destination)

    self["file_name"] = unique_destination.name
    self.file_path = str(unique_destination)
    self.name = unique_destination.name

    refresh_folder_view()


# Active index (GETTER/SETTER)
def get_folder_view_active_index(self):
    return self.get("folder_view_active_index", 0)


def set_folder_view_active_index(self, value):
    self["folder_view_active_index"] = value

    folder_view_list = self.folder_view_list

    if len(folder_view_list) < 1:
        return

    def show_text(text):
        for area in bpy.context.screen.areas:
            area: bpy.types.AreaSpaces
            if area.type == "TEXT_EDITOR":
                area.spaces[0].text = text

    file = file_path_at_index(value)
    text = text_at_index(value)

    if text is not None:
        show_text(text)
    else:
        try:
            with open(str(file), "r") as f:
                pass
            text = bpy.data.texts.load(str(file))
            show_text(text)
        except:
            pass


# Open folder path (GETTER/SETTER)
def get_open_folder_path(self):
        return self.get("open_folder_path", "")


def set_open_folder_path(self, value):
    folder = Path(value)
    if not folder.is_dir():
        print(f"Failed to set property open_folder_path - {value} is not a directory")
        return
    open_folder(folder)
    refresh_folder_view(redraw_only=True)
    self["open_folder_path"] = value


# ——————————————————————————————————————————————————————————————————————
# MARK: PROPERTY DEFINITIONS
# ——————————————————————————————————————————————————————————————————————


class FileItemProperties(bpy.types.PropertyGroup):
    file_path: StringProperty(name="File Path")
    file_name: StringProperty(
        name="File Name",
        get=get_file_name,
        set=set_file_name
    )
    file_type: StringProperty(name="File Type")
    creation_idx: IntProperty()
    depth: IntProperty()


class ExplorerProperties(bpy.types.PropertyGroup):
    open_folder_path: StringProperty(
        name="Open Folder Path",
        get=get_open_folder_path,
        set=set_open_folder_path
    )
    folder_view_list: CollectionProperty(type=FileItemProperties)
    folder_view_active_index: IntProperty(
        name="Active File Index",
        get=get_folder_view_active_index,
        set=set_folder_view_active_index
    )
