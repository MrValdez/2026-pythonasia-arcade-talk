import arcade
import arcade.future.background as background
import math
from dataclasses import dataclass, field
from pprint import pprint

screen_width, screen_height = 1024, 768


@dataclass
class Vertex:
    x: float
    y: float
    z: float


@dataclass
class Segment:
    index: int
    world: Vertex
    curve: int
    color_road: arcade.types.Color
    color_grass: arcade.types.Color
    color_side: arcade.types.Color
    color_lane: arcade.types.Color | None = None


class Camera:
    def __init__(self, road):
        self.pos = Vertex(0, 800, 0)
        self.dist_to_player = 100
        self.road = road
        self.near_plane = 1
        self.current_segment = None

    def update(self):
        self.near_plane = 1 / (self.pos.y / (self.dist_to_player or 1))


class Road:
    def __init__(self):
        self.segment_length = 20
        self.road_width = 900
        self.road_lanes = 3

        self.reset()

    def reset(self):
        self.road_length = 0

        self.segments = []
        self.segment_index = 0

        self.segment_draw_distance = 50

    def load_roads(self):
        self.create_segments(100)

        self.road_length = len(self.segments) * self.segment_length

    def create_segments(self, n):
        segments = []
        start_i = len(self.segments)
        for i in range(start_i, start_i + n):
            palletes = {
                "LIGHT": {
                    "road": arcade.color.GRAY,
                },
                "DARK": {
                    "road": arcade.color.DARK_BLUE,
                }
            }

            #if i % 2 == 0:
            #    pallete = palletes["LIGHT"]
            #else:
            #    pallete = palletes["DARK"]
            pallete = palletes["LIGHT"]

            color_road = pallete.get("road")
            color_grass = None
            color_side = None
            color_lane = None

            segment = Segment(self.segment_index,
                              Vertex(0, 0, self.segment_index * self.segment_length),
                              0,
                              color_road,
                              color_grass,
                              color_side,
                              color_lane)
            self.segment_index += 1

            segments.append(segment)

        self.segments.extend(segments)

    def project2d(self, segment):
        return Vertex(screen_width / 2, segment.world.z, 0)

    def render2d(self):
        for i in range(len(self.segments) - 1):
            segment_i1 = i % len(self.segments)
            segment_i2 = (i + 1) % len(self.segments)

            current_segment = self.segments[segment_i1]
            next_segment = self.segments[segment_i2]

            p1 = self.project2d(current_segment)
            p2 = self.project2d(next_segment)

            self.draw_segment(
                p1.x, p1.y, self.road_width,
                p2.x, p2.y, self.road_width,
                current_segment,
            )

    def draw_segment(self, x1, y1, w1, x2, y2, w2, segment):
        points = [
            [x1 - w1, y1],
            [x1 + w1, y1],
            [x2 + w2, y2],
            [x2 - w2, y2],
        ]
        arcade.draw_polygon_filled(points, segment.color_road)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height)

        self.road = Road()
        self.road.load_roads()
        self.camera = Camera(self.road)

    def on_draw(self):
        self.clear()

        camera_segment = self.camera.current_segment

        self.road.render2d()

    def on_update(self, dt):
        self.camera.update()


if __name__ == "__main__":
    Game()
    arcade.run()
