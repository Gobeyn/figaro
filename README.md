# Figaro

Figaro is a CLI tool for handling figures generated with Python scripts incrementally without needing to rely on tools like `make`.

## Installation

To install `figaro`, simply install it with `pip` or your favourite Python package manager via
```{bash}
pip install .
```
or equivalent.

## How does it work

Here we discuss the general principal behind how `figaro` functions. To see the CLI options, run `figaro --help`. An example setup is 
provided in the `./example/` directory.

### Tagging functions

In order for `figaro` to know which functions will generate a figure (and hence which ones to execute), a decorator function called `figarotag` is provided by the 
library. In code this will look like

```{py}
from figaro import figarotag
from pathlib import Path

@figarotag(name="filename", ext="extension (pdf, png, etc.)")
def figure_function(out_path: Path) -> None:
    ...
```

The decorator allows the addition of extra information such as the name of the resulting figure and which file extension it should have. If that is not provided, 
the name of the function and `pdf` is used by default. 

It is further also required that the figure generating function has a particular function signature namely `pathlib.Path -> None`, e.g. it takes in a single 
argument of type `pathlib.Path` and returns nothing. The path argument is intended to be the path where the generated figure is saved.

### Metadata file

Incremental builds are handled by auto-generating a metadata file. For every Python script that has a figure generating function, it stores a checksum of that script and 
stores the dependent figures generated from it. When `figaro` is run again, and no change was made to a tracked source file, the figures are not regenerated.
