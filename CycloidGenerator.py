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
        unitsMgr = design.unitsManager

        # USER INPUTS (EDIT THESE)  (ALL IN mm)
        N = 30                         # number of outer pins
        D_pitch_mm = 80.0              # pitch circle diameter through outer pin centers (mm)
        pointsCount = 800              # total points computed (higher = smoother)
        decimate = 2                   # keep every Nth point (2=half, 3=third). Speeds up spline solving.

        make_closed = False            # True can be slower. You can close later if needed.
        make_offset_profile = True     # if True, creates an offset curve for the real disc profile

        outer_pin_diam_mm = 7.0        # OUTER ring pin diameter (mm)
        clearance_mm = 0.30            # print clearance (mm)
        # offset distance = (pin radius + clearance)

        # Convert mm -> cm for Fusion API (internal units)
        D_pitch = unitsMgr.evaluateExpression(f'{D_pitch_mm} mm', 'cm')
        outer_pin_diam = unitsMgr.evaluateExpression(f'{outer_pin_diam_mm} mm', 'cm')
        clearance = unitsMgr.evaluateExpression(f'{clearance_mm} mm', 'cm')

        # Derived values (in cm)
        R = D_pitch / 2.0       # pitch radius
        r = R / N               # generating circle radius
        k = N - 1               # lobes

        offset_dist = (outer_pin_diam / 2.0) + clearance  # cm

        # Create a sketch on XY plane
        sketches = root.sketches
        sketch = sketches.add(root.xYConstructionPlane)
        sketch.name = f'Cycloid_N{N}_D{D_pitch_mm:g}mm'

        # Build points (decimated)
        pts = adsk.core.ObjectCollection.create()

        # We compute pointsCount+1 points, but only feed Fusion every "decimate" points
        # This keeps the curve smooth without freezing Fusion.
        for i in range(pointsCount + 1):
            if i % decimate != 0 and i != pointsCount:
                continue

            t = (2.0 * math.pi) * (i / pointsCount)

            x = (R - r) * math.cos(t) + r * math.cos(k * t)
            y = (R - r) * math.sin(t) - r * math.sin(k * t)

            pts.add(adsk.core.Point3D.create(x, y, 0))

        # Create fitted spline through points
        spline = sketch.sketchCurves.sketchFittedSplines.add(pts)
        if make_closed:
            spline.isClosed = True

        # Optional: create offset profile curve (real disc outline)
        offset_curve = None
        if make_offset_profile:
            # Offsets in sketch
            # NOTE: Some Fusion versions return a SketchCurveOffsetCollection
            offsets = sketch.offset(spline, adsk.core.Point3D.create(0, 0, 0), offset_dist)
            # Try to grab the first offset curve (if any)
            if offsets and offsets.count > 0:
                offset_curve = offsets.item(0)

        # Message summary (in mm)
        R_mm = D_pitch_mm / 2.0
        r_mm = R_mm / N
        offset_mm = (outer_pin_diam_mm / 2.0) + clearance_mm

        msg = (
            f'Cycloidal curve created!\n\n'
            f'N (pins) = {N}\n'
            f'D_pitch = {D_pitch_mm:.3f} mm\n'
            f'R = {R_mm:.3f} mm\n'
            f'r = {r_mm:.6f} mm\n'
            f'k = {k}\n'
            f'points computed = {pointsCount}, decimate = {decimate} (points sent ≈ {len(range(0, pointsCount+1, decimate))})\n\n'
        )

        if make_offset_profile:
            msg += (
                f'Offset profile created!\n'
                f'outer pin diam = {outer_pin_diam_mm:.3f} mm\n'
                f'clearance = {clearance_mm:.3f} mm\n'
                f'offset distance = {offset_mm:.3f} mm\n\n'
                f'If the offset went the “wrong way”, delete it and offset the other direction manually.'
            )
        else:
            msg += 'Next: Sketch > Offset by (outer_pin_radius + clearance).'

        ui.messageBox(msg)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))