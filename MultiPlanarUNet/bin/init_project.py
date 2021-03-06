from argparse import ArgumentParser
import os
from MultiPlanarUNet.train import YAMLHParams


def copy_yaml_and_set_data_dirs(in_path, out_path, data_dir):
    hparams = YAMLHParams(in_path, no_log=True)
    train = data_dir + "/train" if data_dir else "Null"
    val = data_dir + "/val" if data_dir else "Null"
    test = data_dir + "/test" if data_dir else "Null"
    aug = data_dir + "/aug" if data_dir else "Null"

    # Set values in parameter file and save to new location
    hparams.set_value("train_data", "base_dir", train,
                      overwrite=True, err_on_missing_dir=True)
    hparams.set_value("val_data", "base_dir", val,
                      overwrite=True, err_on_missing_dir=False)
    hparams.set_value("test_data", "base_dir", test,
                      overwrite=True, err_on_missing_dir=False)
    hparams.set_value("aug_data", "base_dir", aug,
                      overwrite=True, err_on_missing_dir=False)
    hparams.save_current(out_path)


def get_parser():
    parser = ArgumentParser(description='Create a new project folder')

    # Define groups
    parser._action_groups.pop()
    required = parser.add_argument_group('required named arguments')
    optional = parser.add_argument_group('optional named arguments')

    required.add_argument('--name', type=str, required=True,
                        help='the name of the project folder')
    optional.add_argument('--root', type=str, default=os.path.abspath("./"),
                          help='a path to the root folder in '
                               'which the project will be initialized')
    optional.add_argument("--model", type=str, default="MultiPlanar",
                          help="Specify a model type parameter file "
                               "('MultiPlanar', '3D', 'MultiTask')")
    optional.add_argument("--data_dir", type=str, default=None,
                          help="Root data folder for the project")

    return parser


def entry_func(args=None):

    default_folder = os.path.split(os.path.abspath(__file__))[0] + "/defaults"
    if not os.path.exists(default_folder):
        raise OSError("Default path not found at %s" % default_folder)

    # Parse arguments
    parser = get_parser()
    args = vars(parser.parse_args(args))
    path = os.path.abspath(args["root"])
    name = args["name"]
    preset = args["model"]
    data_dir = args["data_dir"]
    if data_dir:
        data_dir = os.path.abspath(data_dir)

    # Validate project path and create folder
    if not os.path.exists(path):
        raise OSError("root path '%s' does not exist." % args["root"])
    else:
        folder_path = "%s/%s" % (path, name)
        if os.path.exists(folder_path):
            response = input("Folder at '%s' already exists. Overwrite? "
                             "Only parameter files and code will be replaced. (y/n) " % folder_path)
            if response.lower() == "n":
                raise OSError("Folder at '%s' already exists" % folder_path)
        else:
            os.makedirs("%s/%s" % (path, name))

    # Get yaml path
    from glob import glob
    yaml_paths = glob(os.path.join(default_folder, preset, "*.yaml"))

    # Write file
    for p in yaml_paths:
        copy_yaml_and_set_data_dirs(in_path=p,
                                    out_path=os.path.join(folder_path, os.path.split(p)[-1]),
                                    data_dir=data_dir)


if __name__ == "__main__":
    entry_func()
