import arcade
import math
from dataclasses import dataclass, field
from pprint import pprint

window_width, window_height = 1024, 768

@dataclass
class Vertex:
    x: float
    y: float
    z: float

@dataclass
class Segment:
    index: int
    world: Vertex
    screen: Vertex
    scale: float
    color_road: str


class Camera:
    def __init__(self):
        self.pos = Vertex(0, 500, 0)
        self.dist_to_player = 50
        self.update()

    def update(self):
        self.near_plane = 1 / (self.pos.y / self.dist_to_player)
        self.pos.z = -self.dist_to_player


class Player:
    def __init__(self):
        self.pos = Vertex(0, 0, 0)


class Road:
    def __init__(self):
        self.segment_length = 20
        self.road_length = 0
        self.road_width = 400
        self.segments = []
        self.segment_index = 0
        self.segment_draw_distance = 100

    def create_roads(self):
        segments = self.create_segments(200)
        self.segments.extend(segments)
        self.road_length = len(self.segments) * self.segment_length

    def create_segments(self, n):
        segments = []
        for i in range(n):
            color = arcade.color.GREEN if (len(self.segments) + i) % 2 == 0 else arcade.color.GRAY
            segment = Segment(self.segment_index,
                              Vertex(0, 0, self.segment_index * self.segment_length),
                              Vertex(0, 0, 0),
                              -1,
                              color)
            self.segment_index += 1
            segments.append(segment)
        return segments

    def get_segment(self, z):
        if z < 0:
            z += len(self.segments)
        i = math.floor(z / self.segment_length) % len(self.segments)
        return self.segments[i]

    def project2d(self, segment):
        return Vertex(window_width / 2, segment.world.z, 0)

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
                current_segment.color_road,
            )

    def project3d(self, point, camera):
        # translate world coordinates to camera coordinates
        translated_camera = Vertex(
            point.world.x - camera.pos.x,
            point.world.y - camera.pos.y ,
            point.world.z - camera.pos.z ,
        )

        # scaling factor based on law of similar triangles
        scale = (camera.near_plane / translated_camera.z) if translated_camera.z else 1

        # project camera coordinates into projection plane
        projected = Vertex(
            translated_camera.x * scale,
            -translated_camera.y * scale,
            self.road_width * scale,
        )

        # scale projected point to screen coordinates
        return Vertex(
            round((1 + projected.x) * (window_width / 2)),
            round((1 - projected.y) * (window_height / 2)),
            projected.z * (window_width / 2),
        )

    def render3d(self, camera):
        camera_segment = self.get_segment(camera.pos.z)

        for i in range(len(self.segments)):
            segment_i = (camera_segment.index + i) % (len(self.segments) - 1)

            current_segment = self.segments[segment_i]
            next_segment = self.segments[segment_i + 1]

            # todo: can be optimized to store the projected coordinates per update instead
            #       of computing each time
            p1 = self.project3d(next_segment, camera)
            p2 = self.project3d(current_segment, camera)

            self.draw_segment(
                p1.x, p1.y, p1.z,
                p2.x, p2.y, p2.z,
                current_segment.color_road,
            )

    def draw_segment(self, x1, y1, w1, x2, y2, w2, color):
        points = [
            [x1 - w1, y1],
            [x1 + w1, y1],
            [x2 + w2, y2],
            [x2 - w2, y2],
        ]
        arcade.draw_polygon_filled(points, color)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(window_width, window_height)
        #arcade.set_background_color(arcade.color.BLUE)
        self.road = Road()
        self.road.create_roads()
        self.camera = Camera()

    def on_draw(self):
        self.clear()

        #self.road.render2d()
        self.road.render3d(self.camera)

    def on_update(self, dt):
        #self.camera.pos.y += 1
        self.camera.update()
        pass

Game()
arcade.run()
