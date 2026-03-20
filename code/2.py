def project3d(point, camera, offset_x, offset_z, width):
    # translate world coordinates to camera coordinates
    translated_camera = Vertex(
        point.x - camera.pos.x + offset_x,
        point.y - camera.pos.y,
        point.z - camera.pos.z + offset_z,
    )

    # scaling factor based on law of similar triangles
    scale = (camera.near_plane / (translated_camera.z or 1))

    # project camera coordinates into projection plane
    projected = Vertex(
        translated_camera.x * scale,
        -translated_camera.y * scale,       # need to be negative as Arcade y axis starts at bottom
        width * scale,
    )

    return Vertex(
        round((1 + projected.x) * (screen_width / 2)),
        round((1 - projected.y) * (screen_height / 2)),
        projected.z * (screen_width / 2),
    ), scale


class Road:
    # ...
    def get_segment_per(self, z):
        return (z % self.segment_length) / self.segment_length

    def get_segment_index(self, z):
        if z < 0:
            z += self.road_length

        return math.floor(z / self.segment_length) % len(self.segments)

    def render3d(self, camera):
        # this will trigger if our camera needs to render last segment (usually at start of the loop)
        camera_segment_i = self.get_segment_index(camera.pos.z)
        camera_segment = self.segments[camera_segment_i]

        camera.current_segment  = camera_segment

        current_clip = 0
        offset_x = 0
        offset_z = 0
        dx = 0
        for i in range(len(self.segments)):
            segment_i = (camera_segment.index + i) % len(self.segments)

            current_segment = self.segments[segment_i]
            next_segment = self.segments[(segment_i + 1) % len(self.segments)]

            #if camera.pos.z < 0:
            #    offset_z -= self.road_length

            # todo: can be optimized to store the projected coordinates per update instead
            #       of computing each time
            p1, _ = project3d(current_segment.world, camera, offset_x, offset_z, self.road_width)
            p2, _ = project3d(next_segment.world, camera, offset_x + dx, offset_z, self.road_width)

            # clip segments behind us
            if p1.z < 0 or p2.z < 0: continue

            # clip segments blocked by tall segments
            if p2.y < current_clip: continue

            current_clip = max(current_clip, p2.y)

            self.draw_segment(
                p1.x, p1.y, p1.z,
                p2.x, p2.y, p2.z,
                current_segment,
            )

class Game:
    # ...
    def on_draw(self):
        # ...
        #self.road.render2d()
        self.road.render3d(self.camera)

