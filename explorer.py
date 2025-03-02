import bpy
from bpy.props import (
    CollectionProperty,
    BoolProperty,
    IntProperty,
    StringProperty
)
from bpy.types import UILayout, UIList, Panel, Operator
from pathlib import Path
from shutil import rmtree


expanded_folder_paths = set()


# ——————————————————————————————————————————————————————————————————————
# MARK: FUNCTIONS
# ——————————————————————————————————————————————————————————————————————


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


# File name (GETTER/SETTER)
def get_file_name(self):
    return self["file_name"]


def set_file_name(self, value):
    source = Path(self.file_path)
    parent = source.parent
    destination: Path = parent / value

    # Is true for when the file is first loaded
    if str(destination) == self.file_path:
        self["file_name"] = value
        return

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
    def show_text(text):
        for area in bpy.context.screen.areas:
            area: bpy.types.AreaSpaces
            if area.type == "TEXT_EDITOR":
                area.spaces[0].text = text

    file = Path(self.folder_view_list[value].file_path)
    texts = bpy.data.texts

    if file.name in texts:
        text = texts[file.name]
        show_text(text)
    else:
        try:
            with open(file, "r") as f:
                pass
            text = bpy.data.texts.load(str(file))
            show_text(text)
        except:
            pass

    self["folder_view_active_index"] = value


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
    def get_open_folder_path(self):
        return self.get("open_folder_path", "")

    def set_open_folder_path(self, value):
        open_folder(Path(value))
        self["open_folder_path"] = value

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


# ——————————————————————————————————————————————————————————————————————
# MARK: INTERFACE
# ——————————————————————————————————————————————————————————————————————


class EXPLORER_UL_folder_view_list(UIList):
    def filter_items(self, context, data, propname):
        helpers = bpy.types.UI_UL_list

        items = getattr(data, propname)
        sort_data = [(i, item.creation_idx) for i, item in enumerate(items)]

        filtered = helpers.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items)
        ordered = helpers.sort_items_helper(sort_data, lambda o: o[1])
        return filtered, ordered

    def draw_filter(self, context, layout):
        layout.prop(self, "filter_name", text="", icon="VIEWZOOM")

    def draw_item(self, context, layout: UILayout, data, item, icon, active_data, active_propname):
        extension_to_icon = {
            ".py": "FILE_SCRIPT",
            ".txt": "FILE_TEXT", ".json": "FILE_TEXT",
            ".blend": "FILE_BLEND",
            ".png": "FILE_IMAGE", ".jpg": "FILE_IMAGE", ".jpeg": "FILE_IMAGE",
            ".tif": "FILE_IMAGE", ".tiff": "FILE_IMAGE", ".gif": "FILE_IMAGE",
            ".webp": "FILE_IMAGE", ".svg": "FILE_IMAGE", ".bmp": "FILE_IMAGE", ".raw": "FILE_IMAGE",
            ".mp4": "FILE_MOVIE", ".mov": "FILE_MOVIE", ".avi": "FILE_MOVIE", ".mkv": "FILE_MOVIE",
            ".flv": "FILE_MOVIE", ".webm": "FILE_MOVIE", ".mpeg": "FILE_MOVIE", ".prores": "FILE_MOVIE",
            ".obj": "FILE_3D", ".fbx": "FILE_3D", ".stl": "FILE_3D", ".gltf": "FILE_3D", ".glb": "FILE_3D",
            ".ply": "FILE_3D", ".dae": "FILE_3D", ".usd": "FILE_3D", ".usdz": "FILE_3D", ".usda": "FILE_3D",
            ".abc": "FILE_3D",
            ".ttf": "FILE_FONT", ".otf": "FILE_FONT", ".dfont": "FILE_FONT", ".fon": "FILE_FONT", ".ttc": "FILE_FONT",
            ".mp3": "FILE_SOUND", ".wav": "FILE_SOUND", ".flac": "FILE_SOUND", ".aac": "FILE_SOUND",
            ".vdb": "FILE_VOLUME",
            "": "FILE"
        }

        file_path = item.file_path
        file_name = item.file_name
        file_type = item.file_type
        depth = item.depth
        is_active = item.creation_idx == active_data.folder_view_active_index
        is_folder = Path(item.file_path).is_dir()
        icon = extension_to_icon.get(file_type, "FILE")

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.emboss = "NONE"

            for i in range(depth):
                spacer = layout.row()
                spacer.ui_units_x = 1

            if is_folder:
                icon = "DOWNARROW_HLT" if file_path in expanded_folder_paths else "RIGHTARROW"
                op = layout.operator("text.toggle_expand_folder", text="", icon=icon)
                op.folder_path = file_path
                layout.prop(item, "file_name", text="")
                if is_active:
                    op = layout.operator("text.delete_file", text="", icon="TRASH")
                    op.file_path = file_path
            else:
                row = layout.row()
                row.label(text="", icon=icon)
                sub = row.row()
                sub.alert = file_name in bpy.data.texts and bpy.data.texts[file_name].is_dirty
                sub.prop(item, "file_name", text="")
                if is_active:
                    op = layout.operator("text.delete_file", text="", icon="TRASH")
                    op.file_path = file_path

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class EXPLORER_PT_explorer_panel(Panel):
    bl_label = "Explorer"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Dev"

    def draw(self, context):
        props = context.window_manager.explorer_properties
        layout = self.layout

        folder = Path(props.open_folder_path)
        folder_name = folder.name

        header, panel = layout.panel("folder_view_subpanel")
        row = header.row(align=True)
        folder_text = folder_name if folder_name != "" else "Open Folder"
        row.operator("text.open_folder", text=folder_text)
        row.operator_context = "EXEC_DEFAULT"
        row.operator("text.create_new_file", text="", icon="FILE_NEW")
        row.operator("text.create_new_folder", text="", icon="NEWFOLDER")
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("text.refresh_folder_view", text="", icon="FILE_REFRESH")
        row.operator("text.collapse_folders", text="",
                     icon="AREA_JOIN_LEFT" if bpy.app.version >= (4, 3, 0) else "AREA_JOIN")
        if panel:
            panel.template_list(
                "EXPLORER_UL_folder_view_list",
                "",
                props, "folder_view_list",
                props, "folder_view_active_index"
            )


# ——————————————————————————————————————————————————————————————————————
# MARK: OPERATORS
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

    def invoke(self, context, event):
        props = context.window_manager.explorer_properties
        if not Path(props.open_folder_path).is_dir():
            self.report({"ERROR"}, "The currently opened folder does not exist.")
            props.open_folder_path = ""
            refresh_folder_view()
            return {"CANCELLED"}

        if original_invoke:
            return original_invoke(self, context, event)

        return self.execute(context)

    cls.invoke = invoke
    return cls


class EXPLORER_OT_open_folder(Operator):
    bl_idname = "text.open_folder"
    bl_label = "Open Folder"
    bl_description = "Allows you to quickly search over all files in the currently opened folder"
    bl_options = {"INTERNAL"}

    directory: StringProperty(
        name="Directory",
        description="Folder to open"
    )

    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}  # Hides filtered-out objects
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        global expanded_folder_paths
        props = context.window_manager.explorer_properties

        expanded_folder_paths.clear()
        props.open_folder_path = self.directory
        return {"FINISHED"}


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_refresh_folder_view(Operator):
    bl_idname = "text.refresh_folder_view"
    bl_label = "Refresh Open Folder"
    bl_description = "Update the displayed contents of the folder view"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        refresh_folder_view()
        return {"FINISHED"}


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_toggle_expand_folder(Operator):
    bl_idname = "text.toggle_expand_folder"
    bl_label = "Expand Folder"
    bl_description = "Show the contents of this folder"
    bl_options = {"INTERNAL"}

    folder_path: StringProperty()

    def execute(self, context):
        global expanded_folder_paths

        props = context.window_manager.explorer_properties
        file_clicked_on = find_file_path_index(self.folder_path, 0)

        if self.folder_path in expanded_folder_paths:
            expanded_folder_paths.discard(self.folder_path)
        else:
            expanded_folder_paths.add(self.folder_path)

        open_folder(Path(props.open_folder_path), file_clicked_on=file_clicked_on)
        return {"FINISHED"}


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_collapse_folders(Operator):
    bl_idname = "text.collapse_folders"
    bl_label = "Collapse Folders in Explorer"
    bl_description = "Display only the top-level contents of the opened folder"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.explorer_properties
        return len(props.folder_view_list) > 0

    def execute(self, context):
        global expanded_folder_paths

        expanded_folder_paths = set()
        refresh_folder_view()
        return {"FINISHED"}


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_create_new_folder(Operator):
    bl_idname = "text.create_new_folder"
    bl_label = "Create New Folder"
    bl_description = "Create a new folder in the currently opened or active directory"
    bl_options = {"INTERNAL"}

    new_folder_name: StringProperty(
        name="Folder Name",
        description="The name of the folder to be created",
        default=""
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences

        if self.new_folder_name == "":
            self.new_folder_name = addon_prefs["default_new_folder_name"]

        parent_folder = contextual_parent_folder()

        new_folder: Path = parent_folder / self.new_folder_name
        unique_new_folder = unique_path(new_folder)

        unique_new_folder.mkdir()

        refresh_folder_view(new_file_path=new_folder)
        return {"FINISHED"}


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_create_new_file(Operator):
    bl_idname = "text.create_new_file"
    bl_label = "Create New File"
    bl_description = "Create a new file in the currently opened or active directory"
    bl_options = {"INTERNAL"}

    new_file_name: StringProperty(
        name="File Name",
        description="The name of the file to be created",
        default=""
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences

        if self.new_file_name == "":
            self.new_file_name = addon_prefs["default_new_file_name"]

        parent_folder = contextual_parent_folder()

        new_file: Path = parent_folder / self.new_file_name

        unique_new_file = unique_path(new_file)
        unique_new_file.touch(exist_ok=False)

        refresh_folder_view(new_file_path=new_file)
        return {"FINISHED"}


@disable_on_empty_folder_path
@require_valid_open_folder
class EXPLORER_OT_delete_file(Operator):
    bl_idname = "text.delete_file"
    bl_label = "Delete File"
    bl_description = "Deletes the selected file"
    bl_options = {"INTERNAL"}

    file_path: StringProperty()

    def invoke(self, context, event):
        if event.shift:
            return self.execute(context)
        wm = context.window_manager
        file = Path(self.file_path)
        file_name = file.name
        title = f"Are you sure you want to delete {file_name}?"
        message = f"You can restore this {'folder' if file.is_dir() else 'file'} from the Recycle Bin."
        return wm.invoke_confirm(self, event, title=title, message=message, icon="INFO")

    def execute(self, context):
        file = Path(self.file_path)
        is_folder = file.is_dir()

        try:
            if is_folder:
                rmtree(file)
            else:
                file.unlink()
        except FileNotFoundError:
            message = f"File {self.file_path} doesn't exist."
            self.report({"ERROR"}, message)
            refresh_folder_view()
            return {"CANCELLED"}

        props = context.window_manager.explorer_properties
        folder_view_list = props.folder_view_list
        active_idx = props.folder_view_active_index

        refresh_folder_view()

        # Calculate new active index
        new_active_idx = min(active_idx, len(folder_view_list) - 1)
        props.folder_view_active_index = new_active_idx
        return {"FINISHED"}


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————


classes = [
    FileItemProperties,
    ExplorerProperties,
    EXPLORER_UL_folder_view_list,
    EXPLORER_PT_explorer_panel,
    EXPLORER_OT_open_folder,
    EXPLORER_OT_refresh_folder_view,
    EXPLORER_OT_toggle_expand_folder,
    EXPLORER_OT_collapse_folders,
    EXPLORER_OT_create_new_folder,
    EXPLORER_OT_create_new_file,
    EXPLORER_OT_delete_file,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.explorer_properties = bpy.props.PointerProperty(
        type=ExplorerProperties,
        name="Explorer"
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.explorer_properties
