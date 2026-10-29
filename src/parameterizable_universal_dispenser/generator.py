import build123d as bt

from parameterizable_universal_dispenser.configuration import ConfigSchema


def generate_dispenser(conf: ConfigSchema) -> tuple[bt.Part, bt.Part]:
    n = conf.circles_dims.n
    rec_base = bt.RectangleRounded(
        conf.dispenser_dims.x_mm,
        conf.dispenser_dims.y_mm,
        conf.dispenser_dims.corner_rounding_radius_mm,
    )
    circle_locations = [
        bt.Location(rec_base.wire().position_at(i / n)) for i in range(n)
    ]
    circles = circle_locations * bt.Circle(conf.circles_dims.r_mm)
    base = rec_base + circles

    dispenser = bt.extrude(base, amount=conf.dispenser_dims.z_mm)

    dispenser_top_face = dispenser.faces().sort_by(bt.Axis.Z)[-1]

    hole_base = bt.Plane(dispenser_top_face) * bt.Rectangle(
        conf.item_dims.x_mm,
        conf.item_dims.y_mm,
    )
    dispenser -= bt.extrude(
        hole_base,
        amount=-(conf.dispenser_dims.z_mm - conf.dispenser_dims.base_z_mm),
        mode=bt.Mode.SUBTRACT,
    )
    front_inner_wall = (
        dispenser.faces().filter_by(bt.GeomType.PLANE).sort_by(bt.Axis.X)[0]
    )
    plane_inner_wall = bt.Plane(front_inner_wall).shift_origin(
        front_inner_wall.edges().sort_by(bt.Axis.Z)[0].center()
    )
    item_hole = plane_inner_wall * bt.RectangleRounded(
        conf.item_dims.y_mm,
        conf.item_dims.z_mm,
        radius=0.5,
        align=(bt.Align.CENTER, bt.Align.MIN),
    )
    dispenser -= bt.extrude(item_hole, amount=-100)

    finger_hole = plane_inner_wall * bt.Rectangle(
        conf.fingerhole_dims.fingerhole_x,
        conf.fingerhole_dims.fingerhole_z,
        align=(bt.Align.CENTER, bt.Align.MIN),
    )
    finger_hole_3d = bt.extrude(finger_hole, amount=-100)
    finger_hole_upper_edges = finger_hole_3d.edges().group_by(bt.Axis.Z)[-1]
    finger_hole_upper_edges = finger_hole_upper_edges.sort_by(bt.Axis.X)[:-1]
    dispenser -= finger_hole_3d.fillet(
        finger_hole_3d.max_fillet(tolerance=0.9, edge_list=finger_hole_upper_edges),
        finger_hole_upper_edges,
    )
    lid = bt.extrude(base, amount=conf.lid_dims.z_mm)

    lid_internal = bt.Rectangle(
        conf.item_dims.x_mm - conf.lid_dims.margin_mm,
        conf.item_dims.y_mm - conf.lid_dims.margin_mm,
    )

    lid += bt.extrude(lid_internal, amount=-conf.lid_dims.internal_z_mm)

    return dispenser, lid
