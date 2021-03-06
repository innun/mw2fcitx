from optparse import OptionParser
from importlib import import_module
from mw2fcitx.build_dict import build
from mw2fcitx.utils import console, sanitize
import json
import os
import re
import sys


def get_args():
    parser = OptionParser(
        usage="Fetch titles from online and generate a dictionary.")
    parser.add_option("-c",
                      "--config",
                      dest="config",
                      default="config.py",
                      help="configuration file location")
    parser.add_option("-n",
                      "--name",
                      dest="name",
                      default="exports",
                      help="configuration object name")

    return parser.parse_args()


def try_file(file):
    console.debug("Finding config file: {}".format(file))
    if not os.access(file, os.R_OK):
        return False
    file_realpath = os.path.realpath(file)
    console.debug("Config file path: {}".format(file_realpath))
    file_path = os.path.dirname(file_realpath)
    file_name = os.path.basename(file_realpath)
    module_name = re.sub(r"\.py$", "", file_name)
    config_file = False
    try:
        sys.path.insert(1, file_path)
        config_file = import_module(module_name)
    except Exception:
        return False
    finally:
        sys.path.remove(file_path)
    return config_file


def main():
    (options, _) = get_args()
    file = options.config
    objname = options.name
    if file.endswith(".py"):
        config_base = try_file(file)
        if config_base == False:
            # I don't think it works... but let's put it here
            config_base = try_file(file + ".py")
    else:
        config_base = try_file(file + ".py")
    if config_base == False:
        console.error("Config file {} not found or not readable".format(
            "{}, {}.py".format(file, file) if file.endswith("py") else file))
        sys.exit(1)
    console.debug("Parsing config file: {}".format(file))
    if objname not in dir(config_base):
        console.error(
            "Exports not found. Please make sure your config in in a object called '{}'."
            .format(objname))
        sys.exit(1)
    config_object = getattr(config_base, objname)
    console.debug("Config load:")
    displayable_config_object = sanitize(config_object)
    console.debug(
        json.dumps(displayable_config_object, indent=2, sort_keys=True))
    build(config_object)


if __name__ == "__main__":
    main()