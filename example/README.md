# Example use of figaro

Here we show an example for how to use the `figaro` CLI tool. To run the example, create a virtual environment with the following packages installed:

- `figaro`
- `matplotlib`
- `pyqt6`
- `numpy`

Then, run the `figaro` CLI with:

```{bash}
figaro -d ./figscripts/ -o ./figures/ --verbose --gitignore
```

This will generate three figures according to the Python scripts in `./figscripts/` and store them into the `./figures/` directory. 
With the `--verbose` flag information on what `figaro` is doing is displayed along with the time it took for each figure generating
function to run. With the `--gitignore` flag a `.gitignore` file is added to the `./figures/` directory with `*` inside so everything 
inside the folder is ignored by `git`.
