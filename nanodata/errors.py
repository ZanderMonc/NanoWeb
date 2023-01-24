import inspect
import os
import traceback


class AbstractNotImplementedError(Exception):
    def __init__(self, path_length: int = 3):
        frame = inspect.currentframe()
        prev_frame = frame.f_back
        caller_name: str = prev_frame.f_code.co_name
        # if OS is windows split with \ else split with /
        caller_filename: str = "/".join(
            prev_frame.f_code.co_filename.split("\\" if os.name == "nt" else "/")[
                -path_length:
            ]
        )
        try:
            class_name: str = prev_frame.f_locals["self"].__class__.__name__
            super().__init__(
                f"Method '{caller_name}' not implemented for '{class_name}' in '{caller_filename}'."
            )
        except KeyError:
            super().__init__(
                f"Function '{caller_name}' not implemented in '{caller_filename}'."
            )
