from build123d import *
from parameterizable_universal_dispenser.configuration import ConfigSchema


def universal_item_dispenser(conf: ConfigSchema) -> Part:
    base_size_x = conf.dispenser_dims.x_mm
    base_size_y = conf.dispenser_dims.y_mm
    # suwak here
    circle_r = conf.circles_dims.r_mm
    # suwak here
    n = conf.circles_dims.n
    base_z = conf.dispenser_dims.base_z_mm
    total_z = conf.item_dims.z_mm * conf.item_dims.count
    # suwak here
    total_rounding = conf.dispenser_dims.corner_rounding_radius_mm

    obj_x = conf.item_dims.x_mm
    obj_y = conf.item_dims.y_mm
    obj_z = conf.item_dims.z_mm

    finger_hole_height = conf.fingerhole_dims.fingerhole_z
    finger_hole_width = conf.fingerhole_dims.fingerhole_x

    lid_height = conf.lid_dims.z_mm
    lid_margin = conf.lid_dims.margin_mm
    lid_internal_len = conf.lid_dims.internal_z_mm

    with BuildPart() as dispenser:
        with BuildSketch() as solid_walls:
            RectangleRounded(base_size_x, base_size_y, total_rounding)
        extrude(solid_walls.sketch, amount=total_z)

        locs = [solid_walls.wire().position_at(i / n) for i in range(n)]
        with BuildSketch() as circles:
            with Locations(locs):
                Circle(circle_r)
        extrude(circles.sketch, amount=total_z)

        topf = dispenser.faces().sort_by(Axis.Z)[-1]
        start = topf.vertices().group_by(Axis.X)[0][0]
        internal_offset_x = start.X + circle_r
        with BuildSketch(topf) as hole:
            with Locations((start.X + circle_r, 0, start.Z)):
                Rectangle(obj_x, obj_y, align=(Align.MIN, Align.CENTER))

        extrude(hole.sketch, amount=-total_z + base_z, mode=Mode.SUBTRACT)

        front_inner_wall = (
            dispenser.faces().filter_by(GeomType.PLANE).sort_by(Axis.X)[0]
        )
        plane_inner_wall = Plane(front_inner_wall, z_dir=(-1, 0, 0))
        plane_inner_wall = plane_inner_wall.shift_origin(
            front_inner_wall.edges().sort_by(Axis.Z)[0].center()
        )
        with BuildSketch(plane_inner_wall) as slot:
            RectangleRounded(obj_y, obj_z, radius=0.5, align=(Align.CENTER, Align.MIN))
            RectangleRounded(
                finger_hole_width,
                finger_hole_height,
                radius=finger_hole_width / 2 - 0.1,
                align=(Align.CENTER, Align.MIN),
            )

        extrude(slot.sketch, amount=-5, mode=Mode.SUBTRACT)

        bottom_face = dispenser.faces().sort_by(Axis.Z)[0]
        with BuildSketch(bottom_face.offset(5)) as lid_base:
            RectangleRounded(base_size_x, base_size_y, total_rounding)
            locs_lid = [lid_base.wire().position_at(i / n) for i in range(n)]
            with Locations(locs_lid):
                Circle(circle_r)
        extrude(lid_base.sketch, amount=lid_height)

        with BuildSketch(bottom_face.offset(5 + lid_height)) as lid_internal:
            with Locations((internal_offset_x + lid_margin, 0, 0)):
                Rectangle(
                    obj_x - lid_margin,
                    obj_y - lid_margin,
                    align=(Align.MIN, Align.CENTER),
                )
        extrude(lid_internal.sketch, amount=lid_internal_len)

    assert dispenser.part is not None

    return dispenser.part
