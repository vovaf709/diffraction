Fraunhofer diffraction on an arbitrary hole
## Method
The goal is to calculate integral 

<img src="http://latex.codecogs.com/gif.latex?E(\textbf{s}) = \int\limits_{\Omega}e^{ik(\textbf{sr})}dF" border="0"/> 

for some set of directions **s**.

General idea is to approximate hole by a set of squares. For each square solution is trivial:

<img src="http://latex.codecogs.com/gif.latex?E = \int\limits_{-a/2}^{a/2}\int\limits_{-b/2}^{b/2}e^{ik(s_xx + s_yy)}dxdy = ab\frac{\sin{\alpha}}{\alpha}\frac{\sin{\beta}}{\beta}" border="0"/>

Solutions for each square are summarized considering geometric center of hole as point with zero field initial phase.

## Usage
Red, green, blue, yellow, magneta, cyan and **fancy**(just try it) colors are availbale. If no color is specified white color will be used.
```bash
python3 diffraction.py %colorname
```
Then draw contour of hole and press "finish".

For higher resolution change variable ```color_grid_size``` from 300 to 600. Note that it will slow down calculations.
## Examples

