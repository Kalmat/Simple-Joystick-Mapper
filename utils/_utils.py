import os
import re
import sys

import pkg_resources


def is_packaged():
    return getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS")


def app_location():
    # this function returns de actual application location (where .py or .exe files are located)
    # Thanks to pullmyteeth: https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
    if is_packaged():
        location = os.path.dirname(sys.executable)
    else:
        location = os.path.dirname(sys.modules["__main__"].__file__)
    return location


def resource_path(relative_path, inverted=False, use_dist_folder="", module=""):
    # this will find resources packaged or not within the executable, with a relative path from application folder
    # when intended to use pyinstaller, move the external resources to the dist folder and set use_dist_folder accordingly (most likely "dist")
    path = ""
    ret = ""
    found = False
    if is_packaged():
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        ret = os.path.normpath(os.path.join(base_path, relative_path))
        found = os.path.exists(ret)

    if not found and module:
        # resource might be inside a wheel (this will crash otherwise)
        try:
            ret = os.path.normpath(pkg_resources.resource_filename(module, relative_path))
            found = os.path.exists(ret)
        except:
            pass

    if not found:
        # resource is in separate folder, not packaged within executable or wheel
        base_path = app_location()
        if not is_packaged():
            base_path = os.path.normpath(os.path.join(base_path, use_dist_folder))
        ret = os.path.normpath(os.path.join(base_path, relative_path))
        found = os.path.exists(ret)

    if found:
        if inverted:
            # required for some specific syntax (e.g. in .qss files)
            ret = ret.replace("\\", "/")
        path = ret

    return path


def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        return ""
    return s
