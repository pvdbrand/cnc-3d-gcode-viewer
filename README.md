# CNC GCode Viewer in 3D

This little tool creates a 3D OpenSCAD model of the *result* of running the tool paths from a gcode file. 

You can use this to double check whether the generated gcode actually results in the object that you want.

## Installation

1. Install [Python](https://www.python.org/downloads/) (either 2 or 3)
1. Install [OpenSCAD](https://www.openscad.org/downloads.html)
1. Clone or download this project
 
## Usage

1. Run the Python script:
    `python gcode-to-scad.py --tooldiam 0.5 examples/crown.gcode examples/crown.scad`
1. Open `examples/crown.scad` in OpenSCAD
1. You should now see the following 3D model:
   ![crown](https://github.com/pvdbrand/cnc-3d-gcode-viewer/blob/master/examples/crown.png)


Optionally, you can render the model in OpenSCAD and export it as an STL. You can then verify dimensions etc in a CAD program.

## Documentation

You can run `python gcode-to-scad.py --help` to get a list of all supported options.

The most important parameter is the tool diameter (`-d` or `--tooldiam`), which sets the diameter of the tool you use, in millimeters.

You might also want to set the thickness of your stock material with the `--sz` parameter. The default thickness is 10mm.

There are two parameters that give you control over the tradeoff between accuracy of the result and time needed to render the model. The `-f` / `--facets` parameter determines how many facets the cylindrical model for the tool should have. More facets means a "rounder" tool, but also more polygons and hence more rendering time needed. Arcs (G2 and G3) are interpolated into small straight line legments. The `-s` / `--seglen` determines the maximum length of these segments. A smaller max length means a "smoother" circle, but again also more polygons and thus slower to render.

## Limitations

The script only supports a very limited subset of GCode. It only works with absolute positioning (G90) and will give an error if you try to use relative positioning (G91). The only supported GCodes are `G0`, `G1`, `G2`, `G3`, `G90`, and `G92`. The script will show any GCode it does not understand.

The only kind of supported tool is a cylinder with a flat bottom (so no ballnose for example). If you know a bit of OpenSCAD it's actually very easy to model any tool you want. You just need to edit the `tool()` module. Tool changes are also not supported.

Only a rectangular model of the stock is provided. Again, it's easy to model any shape of stock you want, just edit the `stock()` module.
