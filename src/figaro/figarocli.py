"""
Author: Aaron Gobeyn
Date: 27/06/2025
"""

from argparse import ArgumentParser, Namespace

import importlib.util
import inspect
import ast
import sys
import time
import json
import hashlib

from pathlib import Path
from typing import Callable


class FigCtlTagFilter(ast.NodeVisitor):
    def __init__(self):
        self.tagged_functions = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and (
                getattr(dec.func, "id", "") == "figarotag"
            ):
                self.tagged_functions.append(node.name)
        self.generic_visit(node)


def checksum(filepath: Path, algorithm="sha256") -> str:
    hash_function = hashlib.new(name=algorithm)

    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_function.update(chunk)
    return hash_function.hexdigest()


def main():
    # ------------------------------
    # Parse CLI Arguments
    # ------------------------------
    parser: ArgumentParser = ArgumentParser(
        description="Figure control manager for handling figure generating Python scripts.",
    )
    parser.add_argument(
        "-d",
        "--dir",
        nargs="*",
        type=Path,
        help="Search directories for figure generating scripts",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Directory to store generated figure files in. Defaults to ./figures/",
        default=Path("./figures/"),
        required=False,
    )
    # parser.add_argument(
    #     "-f",
    #     "--figures",
    #     nargs="*",
    #     type=Path,
    #     help="Specific figure generating script or scripts to run. If not provided, all files in the provided search directories are considered",
    #     default=None,
    #     required=False,
    # )
    parser.add_argument(
        "--gitignore",
        action="store_true",
        help="Add .gitignore to out directory to ignore all files inside.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force figure update even if checksum is the same",
    )
    parser.add_argument(
        "--metafile",
        type=Path,
        help="Path to meta data file containing the required information for whether a figure has to be rebuild or not.",
        default=Path("./.figaro.meta"),
        required=False,
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args: Namespace = parser.parse_args()

    # Validate search directories
    if args.dir is None or args.dir == []:
        print("-d/--dir: At least one search directory must be provided.")
        exit(1)
    for dir in args.dir:
        assert isinstance(dir, Path), "-d/--dir: Search directory has unexpected type"
        if not dir.exists():
            print(f"-d/--dir: Search directory {dir.resolve()} does not exist.")
            exit(1)
        if not dir.is_dir():
            print(f"-d/--dir: Search directory {dir.resolve()} is not a directory.")
            exit(1)

    # Configure output directory
    assert isinstance(args.out, Path), "-o/--out: Out directory has unexpected type"
    if not args.out.exists():
        args.out.mkdir(exist_ok=True)
    if not args.out.is_dir():
        print(f"-o/--out: Out directory {args.out.resolve()} is not a directory.")
        exit(1)

    # Load metadata file if it exists, initialize empty instance otherwise.
    assert isinstance(
        args.metafile, Path
    ), "--metafile: Meta data file has unexpected type"
    if args.metafile.exists():
        if args.verbose:
            print(f"Loading metadata file {args.metafile}...")
        with args.metafile.open("r") as f:
            meta_content: dict = json.load(f)
    else:
        if args.verbose:
            print(f"Metadata file does not exists, initializing new instance...")
        meta_content: dict = {}

    # ---------------------------------
    # Find Figure Generating Functions
    # ---------------------------------

    # Extract python files from all search directories.
    if args.verbose:
        print("Extracting python files from search directories...")
    src_files: list[Path] = [
        file for dir in args.dir for file in dir.rglob("*.py") if file.is_file()
    ]
    if args.verbose:
        print(f"\tFound {len(src_files)} python files in search directories")

    # Filter out only those files which have tagged figure generating functions.
    fig_generators: dict[Path, list[str]] = {}
    if args.verbose:
        print("\t\tFiltering files with tagged functions...")
    for file in src_files:
        if args.verbose:
            print(f"\t\t\tSearching {file.resolve().relative_to(Path.cwd())}")

        with file.open("r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file.resolve()))
        tag_filter = FigCtlTagFilter()
        tag_filter.visit(tree)
        if len(tag_filter.tagged_functions) > 0:
            if args.verbose:
                print(
                    f"\t\t\t\tFound {len(tag_filter.tagged_functions)} tagged functions"
                )
            fig_generators[file] = tag_filter.tagged_functions
        else:
            if args.verbose:
                print(f"\t\t\t\tNo tagged functions")

    # ---------------------------------
    # Run Figure Generating Functions
    # ---------------------------------
    if args.verbose and args.force:
        print("Forced figure generation detected")

    for fp, fncts in fig_generators.items():
        pkgs_name = fp.parent.stem
        submodule_name = fp.stem
        module_name = pkgs_name + "." + submodule_name

        spec = importlib.util.spec_from_file_location(module_name, str(fp.resolve()))
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        loader = spec.loader
        assert loader is not None
        loader.exec_module(module)

        for fnc in fncts:
            if not hasattr(module, fnc):
                print(
                    "Error: Internal logic error, function not found in module that was extracted from module file."
                )
            fig_gen: Callable = getattr(module, fnc)
            sig = inspect.signature(fig_gen)

            params = list(sig.parameters.values())
            if len(params) != 1:
                print(
                    "Invalid function signature. Figure generating function must have signature (pathlib.Path) -> None"
                )
                continue
            param = params[0]
            if param.annotation != Path:
                print(
                    "Invalid function signature. Figure generating function must have signature (pathlib.Path) -> None"
                )
                continue
            if not hasattr(fig_gen, "_figaroname"):
                print(
                    "Error: Internal logic error, functions with appropriate decorator was filtered, but ._figaroname attribute was not found."
                )
            file_name = getattr(fig_gen, "_figaroname")
            if not hasattr(fig_gen, "_figaroext"):
                print(
                    "Error: Internal logic error, functions with appropriate decorator was filtered, but ._figaroext attribute was not found."
                )
            file_ext = getattr(fig_gen, "_figaroext")
            save_path: Path = args.out.joinpath(file_name + "." + file_ext)

            full_fp: str = str(fp.resolve())
            script_checksum: str = checksum(filepath=fp)

            ## Do meta data stuff
            # Check if the current file is in the metadata content
            if full_fp in meta_content:
                # Check if a checksum is present, if not, something went wrong when generating the
                # metadata file in the first place.
                if "checksum" not in meta_content[full_fp]:
                    print(
                        f"Error: Meta data file is corrupt. Try removing {args.metafile}"
                    )
                    continue
                # Check that the checksum from the metadata file is the same as the one just computed. If `--force` is provided,
                # skip the checksum check.
                if meta_content[full_fp]["checksum"] == script_checksum and (
                    not args.force
                ):
                    # If checksum is valid and the figure file exists, then we can skip. Otherwise, it still needs to be generated.
                    if save_path.exists() and save_path.is_file():
                        if args.verbose:
                            print(
                                f"Unchanged checksum: skip calling function {module.__name__ + "." + fig_gen.__name__}"
                            )
                        continue
                else:
                    # If the checksum is not equal, generate the figure and update the checksum.
                    if args.verbose and (not args.force):
                        print(
                            f"Changed checksum detected for {module.__name__ + "." + fig_gen.__name__}"
                        )
                    meta_content[full_fp]["checksum"] = script_checksum
                # Check that the figure is present as a dependent, add if it is not for incremental builds.
                if "dependents" not in meta_content[full_fp]:
                    print(
                        f"Error: Meta data file is corrupt. Try removing {args.metafile}"
                    )
                    continue
                if str(save_path.resolve()) not in meta_content[full_fp]["dependents"]:
                    meta_content[full_fp]["dependents"].append(str(save_path.resolve()))

            # If the current file is not in the metadata content, it must be added.
            else:
                meta_content[full_fp] = dict()
                meta_content[full_fp]["checksum"] = script_checksum
                # Add the figure as a dependent
                meta_content[full_fp]["dependents"] = []
                meta_content[full_fp]["dependents"].append(str(save_path.resolve()))

            if args.verbose:
                print(f"Calling function {module.__name__ + "." + fig_gen.__name__}...")
            ts = time.time()
            fig_gen(save_path)
            te = time.time()
            if args.verbose:
                print(f"\tFinished in {te - ts:.5f} s")
                print(f"\tFigure saved at {save_path}")

    # ------------------------------
    # Cleanup
    # ------------------------------

    # If no figures were generated, remove the output directory, if that directory is empty.
    if not any(args.out.iterdir()):
        args.out.rmdir()
    else:
        # Otherwise, add .gitignore if required
        if args.gitignore:
            with open(args.out.joinpath(".gitignore"), "w") as f:
                f.write("*")

    # ------------------------------
    # Save Metadata File
    # ------------------------------
    with args.metafile.open("w") as f:
        json.dump(meta_content, f, indent=3)
