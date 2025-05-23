from pathlib import Path
from .functions import refresh_folder_view


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
