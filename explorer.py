import bpy
from bpy.props import (
    CollectionProperty,
    BoolProperty,
    IntProperty,
    StringProperty
)
from bpy.types import UILayout, UIList, Panel, Operator
from pathlib import Path


expanded_folder_paths = set()


# ——————————————————————————————————————————————————————————————————————
# MARK: FUNCTIONS
# ——————————————————————————————————————————————————————————————————————


def find_file_path_index(file_path, default=0):
    folder_view_list = bpy.context.window_manager.explorer_properties.folder_view_list
    return next((i for i, file in enumerate(folder_view_list) if file.file_path == file_path), default)


def restore_active_file_decorator(func):
    def wrapper(*args, **kwargs):
        context = bpy.context
        props = context.window_manager.explorer_properties

        folder_view_list = props.folder_view_list
        active_idx = props.folder_view_active_index
        file_clicked_on = kwargs.get("file_clicked_on", 0)

        if 0 <= active_idx < len(folder_view_list):
            active_file_path = folder_view_list[active_idx].file_path
        else:
            active_file_path = None

        result = func(*args, **kwargs)

        if active_file_path is None:
            new_idx = 0
        else:
            new_idx = find_file_path_index(active_file_path, file_clicked_on)

        props.folder_view_active_index = new_idx
        return result
    return wrapper


@restore_active_file_decorator
def open_folder(folder: Path, creation_idx=0, depth=0, file_clicked_on=0):
    global expanded_folder_paths

    context = bpy.context
    props = context.window_manager.explorer_properties

    if creation_idx == 0:
        props.folder_view_list.clear()

    files = sorted(
        folder.iterdir(),
        key=lambda f: (
            not f.is_dir(),  # Folders first
            f.name.lower()   # Then sort by name
        )
    )

    for file in files:
        item = props.folder_view_list.add()
        item.creation_idx = creation_idx
        item.depth = depth
        item.name = file.name
        item.file_path = str(file)
        item.file_type = file.suffix.lower()
        creation_idx += 1

        if item.file_path in expanded_folder_paths and file.is_dir():
            creation_idx = open_folder(file, creation_idx, depth+1)
    return creation_idx  # Ensure index continuity


# ——————————————————————————————————————————————————————————————————————
# MARK: PROPERTY DEFINITIONS
# ——————————————————————————————————————————————————————————————————————


class FileItemProperties(bpy.types.PropertyGroup):
    file_path: StringProperty(name="File Path")
    file_type: StringProperty(name="File Type")
    creation_idx: IntProperty()
    depth: IntProperty()


class ExplorerProperties(bpy.types.PropertyGroup):
    def get_folder_path(self):
        return self.get("open_folder_path", "")

    def set_folder_path(self, value):
        open_folder(Path(value))
        self["open_folder_path"] = value

    open_folder_path: StringProperty(
        name="Open Folder Path",
        get=get_folder_path,
        set=set_folder_path
    )
    folder_view_list: CollectionProperty(type=FileItemProperties)
    folder_view_active_index: IntProperty(name="Active File Index", default=0)


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
        file_type = item.file_type
        depth = item.depth
        is_directory = Path(item.file_path).is_dir()
        icon = extension_to_icon.get(file_type, "FILE")

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            for i in range(depth):
                spacer = layout.row()
                spacer.ui_units_x = 1

            if is_directory:
                icon = "DOWNARROW_HLT" if file_path in expanded_folder_paths else "RIGHTARROW"
                op = layout.operator("text.toggle_expand_folder", text="", icon=icon, emboss=False)
                op.folder_path = file_path
                layout.label(text=item.name)
            else:
                layout.label(text=item.name, icon=icon)

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
        folder_text = folder_name if str(folder) != "" else "Open Folder"
        row.operator("text.open_folder", text=folder_text)
        row.operator("text.create_new_folder", text="", icon="NEWFOLDER")
        row.operator("text.refresh_folder", text="", icon="FILE_REFRESH")
        row.operator("text.collapse_folders", text="", icon="AREA_JOIN_LEFT")
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


def require_valid_open_folder(cls):
    @classmethod
    def poll(cls, context):
        props = context.window_manager.explorer_properties
        return props.open_folder_path != "" and Path(props.open_folder_path).is_dir()

    cls.poll = poll
    return cls


@require_valid_open_folder
class EXPLORER_OT_refresh_folder(Operator):
    bl_idname = "text.refresh_folder"
    bl_label = "Refresh Folder"
    bl_description = "Update the displayed contents of the folder view"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        global expanded_folder_paths
        props = context.window_manager.explorer_properties

        open_folder(Path(props.open_folder_path))
        return {"FINISHED"}


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
        props = context.window_manager.explorer_properties

        expanded_folder_paths = set()
        open_folder(Path(props.open_folder_path))  # Refresh
        return {"FINISHED"}


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


@require_valid_open_folder
class EXPLORER_OT_create_new_folder(Operator):
    bl_idname = "text.create_new_folder"
    bl_label = "Create New Folder"
    bl_description = "Create a new folder in the currently opened or active directory"
    bl_options = {"INTERNAL"}

    new_folder_name: StringProperty(
        name="Folder Name",
        description="Name of the new folder",
        default="New Folder"
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        global expanded_folder_paths

        props = context.window_manager.explorer_properties
        active_idx = props.folder_view_active_index
        active_item = props.folder_view_list[active_idx]

        if active_item.file_type == "" and active_item.file_path in expanded_folder_paths:
            parent_folder_path = active_item.file_path
        else:
            parent_folder_path = str(Path(active_item.file_path).parent)

        new_folder = Path(parent_folder_path) / self.new_folder_name

        try:
            new_folder.mkdir()
        except Exception as e:
            self.report({"ERROR"}, f"Unable to create new folder: {e}")
            return {"CANCELLED"}

        open_folder(Path(props.open_folder_path))  # Refresh
        return {"FINISHED"}


classes = [
    FileItemProperties,
    ExplorerProperties,
    EXPLORER_UL_folder_view_list,
    EXPLORER_PT_explorer_panel,
    EXPLORER_OT_open_folder,
    EXPLORER_OT_refresh_folder,
    EXPLORER_OT_collapse_folders,
    EXPLORER_OT_toggle_expand_folder,
    EXPLORER_OT_create_new_folder,
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
