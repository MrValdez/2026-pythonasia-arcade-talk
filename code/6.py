class Road:
    #...
    def reset(self):
        #self.segment_draw_distance = 50

    #...
    def load_roads(self):
        self.create_segments(500)
        # ...
        exit_segment = 40
        exit_segment = self.add_ease("curve", 10, exit_segment, 20, 40, 1)
        exit_segment = self.add_ease("curve", -20, exit_segment, 4, 20, 10)
        exit_segment += 40
        exit_segment = self.add_ease("curve", -10, exit_segment, 4, 20, 5)

    def add_ease(self, type, target, start, enter, hold, exit):
        def ease_in(a, b, per):
            return a + (b-a) * math.pow(per, 2)

        def ease_out(a, b, per):
            return a + (b-a) * ((-math.cos(per * math.pi) / 2) + 0.5)

        for i in range(0, enter):
            out = ease_in(0, target, i / enter)

            self.segments[start + i].curve = out

        start += i
        for i in range(0, hold):
            self.segments[start + i].curve = target

        start += i
        for i in range(0, exit):
            out = ease_out(target, 0, i / exit)
            self.segments[start + i].curve = out

        return start + i

    #...
    def render3d(self, camera):
        # this will trigger if our camera needs to render last segment (usually at start of the loop)
        camera_segment_i = self.get_segment_index(camera.pos.z)
        camera_segment = self.segments[camera_segment_i]

        offset_x = 0
        dx = camera_segment.curve * self.get_segment_per(camera.pos.z)

        drawn = 0
        current_clip = 0
        camera.current_segment = camera_segment

        for i in range(len(self.segments)):
            #drawn += 1
            #if drawn > self.segment_draw_distance:
            #    break

            segment_i = (camera_segment.index + i) % len(self.segments)

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

            offset_x += dx
            dx -= current_segment.curve

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
