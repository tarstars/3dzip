// y_zipper_generator.scad
// Experimental Y-zipper-inspired parametric prototype.
// Not the official MIT/CSAIL Y-Zipper geometry.
//
// In OpenSCAD, set part to one of: "strip", "strip3", "slider".

part = "strip3";

teeth = 12;
pitch = 5.0;
strip_width = 16.0;
margin = 5.0;
base_t = 0.70;
rib_radius = 0.75;
rib_y = 1.25;
bead_r = 1.05;
clip_clearance = 0.35;
clip_wall = 0.85;
snap_lip = true;
plate_spacing = 8.0;
$fn = 24;

length = 2 * margin + teeth * pitch;
bead_segment = pitch * 0.62;
clip_depth = bead_r * 2.2 + clip_clearance;
slot_h = bead_r * 2.0 + clip_clearance;
clip_h = slot_h + 2.0 * clip_wall;

module cyl_x(r, h, center=[0,0,0]) {
  translate(center) rotate([0,90,0]) cylinder(r=r, h=h, center=true);
}

module cyl_y(r, h, center=[0,0,0]) {
  translate(center) rotate([90,0,0]) cylinder(r=r, h=h, center=true);
}

module box(size, center=[0,0,0]) {
  translate(center) cube(size, center=true);
}

module strip(include_edges=true) {
  union() {
    // flexible membrane
    box([strip_width, length, base_t], [0, length/2, base_t/2]);

    // transverse ribs
    rib_len = max(2.0, strip_width - 2.2);
    for (i=[0:teeth-1]) {
      y = margin + (i + 0.5) * pitch;
      box([rib_len, rib_y, rib_radius * 0.55], [0, y, base_t + rib_radius * 0.15]);
      cyl_x(rib_radius, rib_len, [0, y, base_t + rib_radius * 0.75]);
    }

    if (include_edges) {
      // male segmented bead edge
      bead_x = -strip_width/2 - bead_r * 1.15;
      neck_w = bead_r * 0.55;
      neck_x = -strip_width/2 - neck_w/2;
      bead_z = base_t + bead_r;
      for (i=[0:teeth-1]) {
        y = margin + (i + 0.5) * pitch;
        seg = min(bead_segment, pitch * 0.82);
        box([neck_w, seg, bead_r * 0.80], [neck_x, y, bead_z]);
        cyl_y(bead_r, seg, [bead_x, y, bead_z]);
      }

      // female segmented C-clip edge
      back_x = strip_width/2 + clip_wall/2;
      depth_center_x = strip_width/2 + clip_wall + clip_depth/2;
      lip_z_bottom = base_t + clip_wall/2;
      lip_z_top = base_t + clip_wall + slot_h + clip_wall/2;
      back_z = base_t + clip_h/2;
      for (i=[0:teeth-1]) {
        y = margin + (i + 0.5) * pitch;
        seg = min(bead_segment, pitch * 0.82);
        box([clip_wall, seg, clip_h], [back_x, y, back_z]);
        box([clip_depth, seg, clip_wall], [depth_center_x, y, lip_z_bottom]);
        box([clip_depth, seg, clip_wall], [depth_center_x, y, lip_z_top]);
        if (snap_lip) {
          catch_t = max(0.35, bead_r * 0.35);
          catch_h = max(0.25, bead_r * 0.28);
          catch_x = strip_width/2 + clip_wall + clip_depth - catch_t/2;
          lower_z = base_t + clip_wall + catch_h/2;
          upper_z = base_t + clip_wall + slot_h - catch_h/2;
          box([catch_t, seg, catch_h], [catch_x, y, lower_z]);
          box([catch_t, seg, catch_h], [catch_x, y, upper_z]);
        }
      }

      // pull tab
      box([strip_width * 0.70, margin * 0.55, base_t * 1.25], [0, margin * 0.45, base_t * 0.62]);
    }
  }
}

module strip3() {
  approx_width = strip_width + bead_r*2.5 + clip_wall + clip_depth;
  translate([-approx_width - plate_spacing, 0, 0]) strip(true);
  strip(true);
  translate([approx_width + plate_spacing, 0, 0]) strip(true);
}

module oriented_box(len, wid, ht, x, y, angle) {
  translate([x, y, ht/2]) rotate([0,0,angle]) cube([len, wid, ht], center=true);
}

module slider() {
  channel_clearance = 1.2;
  arm_len = 48.0;
  plate_t = 2.2;
  wall_t = 2.0;
  wall_h = 6.5;
  ch_w = strip_width + channel_clearance;
  ring_side = strip_width + 2.0 * channel_clearance;
  ring_wall = wall_t * 1.25;
  ring_h = wall_h;
  R = ring_side / sqrt(3);

  union() {
    // central triangular frame bars
    for (k=[0:2]) {
      a0 = 90 + k*120;
      a1 = 90 + ((k+1)%3)*120;
      p0 = [R*cos(a0), R*sin(a0)];
      p1 = [R*cos(a1), R*sin(a1)];
      mx = (p0[0] + p1[0])/2;
      my = (p0[1] + p1[1])/2;
      dx = p1[0] - p0[0];
      dy = p1[1] - p0[1];
      oriented_box(sqrt(dx*dx+dy*dy) + ring_wall, ring_wall, plate_t + ring_h, mx, my, atan2(dy, dx));
    }

    // radial U channels
    inner_offset = R * 0.55;
    for (k=[0:2]) {
      a = 90 + k*120;
      dx = cos(a); dy = sin(a);
      startx = dx * inner_offset;
      starty = dy * inner_offset;
      cx = startx + dx * arm_len/2;
      cy = starty + dy * arm_len/2;
      px = -dy; py = dx;
      oriented_box(arm_len, ch_w + 2*wall_t, plate_t, cx, cy, a);
      for (s=[-1,1]) {
        oriented_box(arm_len, wall_t, plate_t + wall_h, cx + px*s*(ch_w/2+wall_t/2), cy + py*s*(ch_w/2+wall_t/2), a);
      }
      oriented_box(wall_t*2.2, ch_w + 2*wall_t, plate_t + wall_h*0.65, startx + dx*arm_len, starty + dy*arm_len, a);
    }
  }
}

if (part == "strip") strip(true);
else if (part == "strip3") strip3();
else if (part == "slider") slider();
else strip3();
