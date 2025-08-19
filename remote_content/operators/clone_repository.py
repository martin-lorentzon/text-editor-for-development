import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..functions import is_git_installed, clone_git_repo
import webbrowser


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
        
        if is_git_installed() == False:
            title ="Git is not installed"
            message = "Please install Git in order to clone remote contents."
            confirm_text = "To Downloads"
            return wm.invoke_confirm(self, event, title=title, message=message, confirm_text=confirm_text, icon="INFO")
        return wm.invoke_props_dialog(self, title=self.title, confirm_text=self.confirm_text)

    def execute(self, context):
        if is_git_installed() == False:  # Second check needed in case the operator is called from script
            webbrowser.open_new_tab("https://git-scm.com/downloads")
            return {"FINISHED"}

        success, message = clone_git_repo(self.repository_url, self.directory)

        if not success:
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        self.report({"INFO"}, message)
        bpy.ops.text.open_folder(directory=self.directory)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        layout.label(text="Specify the path to a new or existing empty folder")
        layout.prop(self, "directory", text="")
        if self.directory != "":
            col = layout.column(align=True)
            col.label(text="The contents will end up in")
            col.label(text=self.directory)
        else:
            layout.separator()
