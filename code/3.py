class Road:
    # ...
    def reset(self):
        self.roadside_length = 3
        self.current_roadside_i = 0
        self.current_roadside_color_switch = 0

    def load_roads(self):
        self.create_segments(500)

        #self.segments[0].color_road = arcade.color.PURPLE
        #self.segments[-2].color_road = arcade.color.PINK         # last segment is end of the road

        self.road_length = len(self.segments) * self.segment_length

    def create_segments(self, n):
        #...
            palletes = {
                "LIGHT": {
                    "road": arcade.color.GRAY,
                    "grass": arcade.color.ARMY_GREEN,
                    "side": arcade.color.WHITE,
                },
                "DARK": {
                    "road": arcade.color.DARK_BLUE,
                    "grass": arcade.color.APPLE_GREEN,
                    "side": arcade.color.BLACK,
                    "lane": arcade.color.WHITE,
                }
            }
            if i % 2:
                pallete = palletes["LIGHT"]
            else:
                pallete = palletes["DARK"]

            color_road = pallete.get("road")
            color_grass = pallete.get("grass")
            color_lane = pallete.get("lane")

            self.current_roadside_i += 1
            if self.current_roadside_i >= self.roadside_length:
                self.current_roadside_i = 0
                self.current_roadside_color_switch += 1

            if self.current_roadside_color_switch % 2:
                pallete = palletes["LIGHT"]
            else:
                pallete = palletes["DARK"]

            color_side = pallete.get("side")

    # ...
    def draw_segment(self, x1, y1, w1, x2, y2, w2, segment):
        points = [
            [0, y1],
            [screen_width, y1],
            [screen_width, y2],
            [0, y2],
        ]
        arcade.draw_polygon_filled(points, segment.color_grass)

        points = [
            [x1 - w1, y1],
            [x1 + w1, y1],
            [x2 + w2, y2],
            [x2 - w2, y2],
        ]
        arcade.draw_polygon_filled(points, segment.color_road)

        side_w1 = w1 / 5
        side_w2 = w2 / 5
        points = [
            [x1 - w1 - side_w1, y1],
            [x1 - w1, y1],
            [x2 - w2, y2],
            [x2 - w2 - side_w2, y2],
        ]
        arcade.draw_polygon_filled(points, segment.color_side)
        points = [
            [x1 + w1 + side_w1, y1],
            [x1 + w1, y1],
            [x2 + w2, y2],
            [x2 + w2 + side_w2, y2],
        ]
        arcade.draw_polygon_filled(points, segment.color_side)

        if segment.color_lane:
            line_w1 = w1 / 20 / 2
            line_w2 = w2 / 20 / 2
            lane_w1 = w1 * 2 / self.road_lanes
            lane_w2 = w2 * 2 / self.road_lanes

            lane_x1 = x1 - w1
            lane_x2 = x2 - w2

            for i in range(1, self.road_lanes):
                lane_x1 += lane_w1
                lane_x2 += lane_w2

                points = [
                    [lane_x1 - line_w1, y1],
                    [lane_x1 + line_w1, y1],
                    [lane_x2 + line_w2, y2],
                    [lane_x2 - line_w2, y2],
                ]
                arcade.draw_polygon_filled(points, segment.color_lane)
