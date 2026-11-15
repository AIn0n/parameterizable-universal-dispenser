from math import floor, radians, tan

import build123d as bt

from parameterizable_universal_dispenser.configuration import ConfigSchema


def _generate_rectangular_base(conf: ConfigSchema):
    return bt.RectangleRounded(
        conf.dispenser_dims.x_mm,
        conf.dispenser_dims.y_mm,
        conf.dispenser_dims.corner_rounding_radius_mm,
    )


def _generate_base_with_circles(conf: ConfigSchema):
    n = conf.circles_dims.n
    rec_base = _generate_rectangular_base(conf)

    circle_locations = [
        bt.Location(rec_base.wire().position_at(i / n)) for i in range(n)
    ]
    circles = circle_locations * bt.Circle(conf.circles_dims.r_mm)
    return rec_base + circles


def get_min_circles_num(conf: ConfigSchema) -> int:
    rec_base = _generate_rectangular_base(conf)
    return floor(rec_base.wire().length / (conf.circles_dims.r_mm * 2)) + 1


def _generate_lid(base, conf: ConfigSchema):
    lid = bt.extrude(base, amount=conf.lid_dims.z_mm)

    lid_upper_x = conf.item_dims.x_mm - conf.lid_dims.margin_mm
    lid_upper_y = conf.item_dims.y_mm - conf.lid_dims.margin_mm
    lid_internal_upper = bt.RectangleRounded(
        lid_upper_x,
        lid_upper_y,
        radius=conf.dispenser_dims.inner_rounding_radius_mm,
    )

    lid_lower_offset = abs(
        tan(radians(conf.lid_dims.internal_wall_angle_degress))
        * conf.lid_dims.internal_z_mm
        * 2
    )
    lid_internal_lower = bt.Plane.XY.offset(
        -conf.lid_dims.internal_z_mm
    ) * bt.RectangleRounded(
        lid_upper_x - lid_lower_offset,
        lid_upper_y - lid_lower_offset,
        radius=conf.dispenser_dims.inner_rounding_radius_mm,
    )
    lid_internal_extruded = bt.loft([lid_internal_upper, lid_internal_lower])
    faces = lid_internal_extruded.faces().sort_by(bt.Axis.Z)
    lid_internal_extruded = bt.offset(
        lid_internal_extruded,
        amount=-conf.lid_dims.internal_wall_thickness_mm,
        openings=[faces[0], faces[-1]],
    )
    return lid + lid_internal_extruded


def generate_dispenser(conf: ConfigSchema) -> tuple[bt.Part, bt.Part]:
    base = _generate_base_with_circles(conf)
    dispenser = bt.extrude(base, amount=conf.dispenser_dims.z_mm)

    dispenser_top_face = dispenser.faces().sort_by(bt.Axis.Z)[-1]

    hole_base = bt.Plane(dispenser_top_face) * bt.RectangleRounded(
        conf.item_dims.x_mm,
        conf.item_dims.y_mm,
        radius=conf.dispenser_dims.inner_rounding_radius_mm,
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
        finger_hole_3d.max_fillet(tolerance=1, edge_list=finger_hole_upper_edges),
        finger_hole_upper_edges,
    )

    return dispenser, bt.Rot(180, 0, 0) * _generate_lid(base, conf)
