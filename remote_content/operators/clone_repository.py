import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..functions import GIT_NOT_FOUND_MSG, is_git_installed, clone_git_repo
import webbrowser


ONLINE_ACCESS_MSG = "Online Access is required for cloning of remote repositories"


class REMOTE_CONTENT_OT_clone_repository(Operator):
    bl_idname = "wm.clone_repository"
    bl_label = "Clone Repository"
    bl_description = "Clone a remote repository to the specified local directory path"
    bl_options = {"INTERNAL"}

    title: StringProperty(default=bl_label)
    confirm_text: StringProperty(default="OK")

    repository_url: StringProperty(
        name="Repository",
        description="The URL of the repository to clone",
        default=""
    )

    directory: StringProperty(
        name="Directory",
        description="The local path to the target directory",
        subtype="DIR_PATH"
    )

    def invoke(self, context, event):
        wm = context.window_manager

        v4_1_0 = bpy.app.version >= (4, 1, 0)

        if not bpy.app.online_access:
            self.report({"ERROR"}, ONLINE_ACCESS_MSG)
            return {"CANCELLED"}

        result, message = is_git_installed()

        match result:
            case 0:
                clone_dialog_kwargs = dict(title=self.title, confirm_text=self.confirm_text) if v4_1_0 else {}
                return wm.invoke_props_dialog(self, **clone_dialog_kwargs)
            case 2:
                if not v4_1_0:
                    self.report({"ERROR"}, GIT_NOT_FOUND_MSG)
                    return {"CANCELLED"}
                
                install_git_kwargs = dict(
                    title="Git is not installed",
                    icon="ERROR",
                    message="Please install Git to clone remote repositories",
                    confirm_text="To Downloads"
                )
                return wm.invoke_confirm(self, event, **install_git_kwargs)
            case _:
                self.report({"ERROR"}, message)
                return {"CANCELLED"}


    def execute(self, context):
        if not bpy.app.online_access:  # Second check needed in case the operator is called from script
            self.report({"ERROR"}, GIT_NOT_FOUND_MSG)
            return {"CANCELLED"}

        result, message = is_git_installed()

        match result:
            case 2:
                print(GIT_NOT_FOUND_MSG)
                webbrowser.open_new_tab("https://git-scm.com/downloads")
                return {"FINISHED"}
            case 1:
                self.report({"ERROR"}, message)
                return {"CANCELLED"}

        result, message = clone_git_repo(self.repository_url, self.directory)

        match result:
            case 0:
                self.report({"INFO"}, message)
                if getattr(context.window_manager, "explorer_properties", None):
                    bpy.ops.wm.explorer_open_folder(directory=self.directory)
                return {"FINISHED"}
            case _:
                self.report({"ERROR"}, message)
                return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout

        op = layout.operator("wm.url_open", text=f"Source: {self.repository_url}", icon="INTERNET", emboss=False)
        op.url = self.repository_url

        layout.separator()

        layout.label(text="Specify the path to a new or existing empty folder")
        layout.prop(self, "directory", text="")
        if self.directory != "":
            col = layout.column(align=True)
            col.label(text=f"The contents will end up in")
            col.label(text=self.directory)
        else:
            layout.separator()
