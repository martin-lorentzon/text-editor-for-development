import bpy
from bpy.types import UILayout, UIList, Panel
from .properties import expanded_folder_paths
from pathlib import Path


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
                row.prop(item, "file_name", text="", icon=icon)
                text_datablock = bpy.data.texts.get(file_name, None)
                if text_datablock is not None and text_datablock.is_dirty:
                    sub = row.row()
                    sub.alert = True
                    sub.alignment = "RIGHT"
                    sub.label(text="Unsaved")
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