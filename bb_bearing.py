from build123d import *
from ocp_vscode import *

def generate_bearing(outer_diameter=22 * MM, inner_diameter=8 * MM, thickness=7 * MM, tolerance=0.05 * MM, bb_diameter=6 * MM, size=None, export=True):
    if int(outer_diameter) == outer_diameter:
        n_od = int(outer_diameter)
    else:
        n_od = outer_diameter
    if int(inner_diameter) == inner_diameter:
        n_id = int(inner_diameter)
    else:
        n_id = inner_diameter
    if int(thickness) == thickness:
        n_w = int(thickness)
    else:
        n_w = thickness
    if int(bb_diameter) == bb_diameter:
        n_bd = int(bb_diameter)
    else:
        n_bd = bb_diameter
    if size is None:
        name = f'custom_od{n_od}id{n_id}w{n_w}bd{n_bd}'
    else:
        name = f'{size}_od{n_od}id{n_id}w{n_w}bd{n_bd}'
    name = name.replace('.', '_').replace('/', '-') + '.step'
    
    wall_thickness = (outer_diameter-inner_diameter)/14
    with BuildPart() as p:
        with BuildSketch() as s:
            Circle((outer_diameter-wall_thickness-bb_diameter)  / 2)
            Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness/2, both=True)
        
        with BuildSketch() as s:
            Circle(outer_diameter  / 2)
            Circle((outer_diameter-wall_thickness-bb_diameter/2) / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness/2, both=True)

        if thickness > 2.25*bb_diameter:
            with Locations((0, 0, thickness/4)):
                p.part = p.part - Torus((outer_diameter-bb_diameter-wall_thickness)/2, ((bb_diameter+tolerance)/2) * MM)
            with Locations((0, 0, -thickness/4)):
                p.part = p.part - Torus((outer_diameter-bb_diameter-wall_thickness)/2, ((bb_diameter+tolerance)/2) * MM)
            with BuildSketch(Plane.XY.offset(thickness/2)) as s:
                with Locations(((outer_diameter-wall_thickness-bb_diameter)/2, 0)):
                    Circle(bb_diameter / 2)
            extrude(amount=-thickness/4, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(-thickness/2)) as s:
                with Locations((-(outer_diameter-wall_thickness-bb_diameter)/2, 0)):
                    Circle(bb_diameter / 2)
            extrude(amount=thickness/4, mode=Mode.SUBTRACT)
        else:
            p.part = p.part - Torus((outer_diameter-bb_diameter-wall_thickness)/2, ((bb_diameter+tolerance)/2) * MM)

            with BuildSketch(Plane.XY.offset(thickness/2)) as s:
                with Locations(((outer_diameter-wall_thickness-bb_diameter)/2, 0)):
                    Circle(bb_diameter / 2)
            extrude(amount=-thickness/2, mode=Mode.SUBTRACT)
    if export:
        export_step(p.part, name)
        export_stl(p.part, name.replace('.step', '.stl'), tolerance=0.0001, angular_tolerance=0.1)
    return p

if __name__ == "__main__":
    show(generate_bearing(export=False).part)
    
    from bearing_sizes import bearing_sizes
    for bb_diameter in [6, 4.5]:
        for i, row in bearing_sizes.iterrows():
            if row["WIDTH"] >= bb_diameter and (row['OUTER DIAMETER (OD)']-row['INNER DIAMETER (ID)']) > 2*bb_diameter and row['WIDTH'] <= 3*bb_diameter and not row['SIZE'].startswith('F'):
                generate_bearing(size=row["SIZE"], outer_diameter=row['OUTER DIAMETER (OD)'], inner_diameter=row['INNER DIAMETER (ID)'], thickness=row['WIDTH'], bb_diameter=bb_diameter)
