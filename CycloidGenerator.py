import adsk.core, adsk.fusion, adsk.cam
import math, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion design.')
            return
        
        root = design.rootComponent

        # USER INPUTS (EDIT THIS)
        N = 30                  # number of outer pins
        D_pitch = 80.0          # mm, pitch circle diameter through outer pin centers
        pointsCount = 1500      # increase for smoother curve (800-3000 typical)

        # Derived values
        R = D_pitch / 2.0       # pitch radius
        r = R / N               # generating circle radius
        k = N - 1               # for 30 pins -> 29 lobes

        # Create a sketch on XY plane
        sketches = root.sketches
        sketch = sketches.add(root.xYConstructionPlane)
        sketch.name = f'Cycloid_N{N}_D{D_pitch:g}mm'

        # Build points
        pts = adsk.core.ObjectCollection.create()
        for i in range(pointsCount + 1):
            t = (2.0 * math.pi) * (i / pointsCount)

            x = (R - r) * math.cos(t) + r * math.cos(k * t)
            y = (R - r) * math.sin(t) - r * math.sin(k * t)

            # Fusion internal units are cm by default, but API accepts "real" values
            # in the design's unit system; most designs are mm. If yours is mm, this is fine.
            pts.add(adsk.core.Point3D.create(x, y, 0))

        # Create fitted spline through points
        spline = sketch.sketchCurves.sketchFittedSplines.add(pts)
        spline.isClosed = True

        ui.messageBox(
            f'Cycloidal reference curve created!\n\n'
            f'N = {N}\nD_pitch = {D_pitch} mm\n'
            f'R = {R:.4f} mm\nr = {r:.6f} mm\nk = {k}\n\n'
            f'Next: use Sketch > Offset to offset outward by (outer_pin_radius + clearance).'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))