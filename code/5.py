class Road:
    # ...
    def load_roads(self):
        self.segments[0].color_road = arcade.color.PURPLE
        self.segments[-2].color_road = arcade.color.PINK         # last segment is end of the road

    def render3d(self, camera):
        #...
        for i in range(len(self.segments)):
            #...
            current_segment = self.segments[segment_i]
            next_segment = self.segments[(segment_i + 1) % len(self.segments)]

            # offset end of road back to start
            offset_z = self.road_length if segment_i < camera_segment.index else 0

            if camera.pos.z < 0:
                offset_z -= self.road_length

            # todo: can be optimized to store the projected coordinates per update instead
            #       of computing each time
            p1, _ = project3d(current_segment.world, camera, offset_x, offset_z, self.road_width)
            p2, _ = project3d(next_segment.world, camera, offset_x + dx, offset_z, self.road_width)

            # Warning: removing these two ifs would make visual bug because we'll be drawing "behind the camera"
            # clip segments behind us
            if p1.z < 0 or p2.z < 0: continue

            # clip segments blocked by tall segments
            if p2.y < current_clip: continue


