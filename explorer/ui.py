import bpy
from .constants import EXTENSION_TO_ICON
from .functions import text_at_file_path
from bpy.types import UILayout
from pathlib import Path


class EXPLORER_UL_folder_view_list(bpy.types.UIList):
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
        expanded_folder_paths = context.window_manager.expanded_folder_paths
        is_active = item.creation_idx == active_data.folder_view_active_index

        is_folder = item.is_dir
        file_type = item.file_type
        
        icon = EXTENSION_TO_ICON.get(file_type, "FILE")

        text = item.text_ref
        is_modified = text is not None and text.is_modified
        is_unsaved = text is not None and text.is_dirty

        if text is not None:
            layout.context_pointer_set("edit_text", text)

        layout.emboss = "NONE"

        for i in range(item.depth):
            spacer = layout.row()
            spacer.ui_units_x = 1

        if is_folder:
            icon = "DOWNARROW_HLT" if item.file_path in expanded_folder_paths else "RIGHTARROW"
            op = layout.operator("text.toggle_expand_folder", text="", icon=icon)
            op.folder_path = item.file_path

            layout.prop(item, "file_name", text="")

            if is_active:
                op = layout.operator("wm.explorer_delete_file", text="", icon="TRASH")
                op.file_path = item.file_path
        else:
            row = layout.row()
            row.prop(item, "file_name", text="", icon=icon)

            if is_modified:
                if is_active:
                    row.operator("text.save", text="", icon="FILE_TICK")
                    row.operator_context = "EXEC_DEFAULT"
                    op = row.operator("text.resolve_conflict", text="", icon="FILE_REFRESH")
                    op.resolution = "RELOAD"
                    row.operator_context = "INVOKE_DEFAULT"
                sub = row.row()
                sub.alignment = "RIGHT"
                sub.alert = True
                sub.label(text="External edits")
            elif is_unsaved:
                if is_active:
                    row.operator("text.save", text="", icon="FILE_TICK")
                sub = row.row()
                sub.alignment = "RIGHT"
                sub.alert = True
                sub.label(text="Unsaved")

            if is_active:
                op = row.operator("wm.explorer_delete_file", text="", icon="TRASH")
                op.file_path = item.file_path


def template_explorer(layout: UILayout, context: bpy.types.Context):
    props = context.window_manager.explorer_properties

    folder = Path(props.open_folder_path)
    folder_name = folder.name

    header, panel = layout.panel("folder_view_subpanel")
    row = header.row(align=True)
    folder_text = folder_name if folder_name != "" else "Open Folder"
    row.operator("wm.explorer_open_folder", text=folder_text)
    row.operator("wm.explorer_create_new_file", text="", icon="FILE_NEW")
    row.operator("wm.explorer_create_new_folder", text="", icon="NEWFOLDER")
    row.operator_context = "INVOKE_DEFAULT"  # TODO: Why did I do this? Neither operators below use invoke methods X.X
    row.operator("wm.explorer_refresh_folder_view", text="", icon="FILE_REFRESH")
    row.operator("wm.explorer_collapse_folders", text="",
                    icon="AREA_JOIN_LEFT" if bpy.app.version >= (4, 3, 0) else "AREA_JOIN")
    if panel:
        panel.template_list(
            "EXPLORER_UL_folder_view_list",
            "",
            props, "folder_view_list",
            props, "folder_view_active_index"
        )


class EXPLORER_PT_explorer_panel(bpy.types.Panel):
    bl_label = "Explorer"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Dev"

    def draw(self, context):
        layout = self.layout

        template_explorer(layout, context)
