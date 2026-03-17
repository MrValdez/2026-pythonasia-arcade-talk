import arcade
import math
from dataclasses import dataclass, field
from pprint import pprint

window_width, window_height = 1024, 768

arcade.open_window(window_width, window_height)

#arcade.set_background_color(arcade.color.BLUE)

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
        self.pos = Vertex(0, 1000, 0)
        self.dist_to_player = 50
        self.near_plane = 1 / (self.pos.y / self.dist_to_player)
        self.update()

    def update(self):
        self.pos.z = -self.dist_to_player

class Road:
    def __init__(self):
        self.segment_length = 100
        self.road_width = 300
        self.segments = []
        self.segment_index = 0

    def create_roads(self):
        sections = self.create_section(10)
        self.segments.extend(sections)

    def create_section(self, n):
        section = []
        for i in range(n):
            segment = Segment(self.segment_index,
                              Vertex(0, 0, self.segment_index * self.segment_length),
                              Vertex(0, 0, 0),
                              -1,
                              arcade.color.GREEN)
            self.segment_index += 1
            section.append(segment)
        return section

    def get_segment(self, z):
        if z < 0:
            z += len(self.segments)
        index = math.floor(z / self.segment_length) % len(self.segments)
        return self.segment[index]

    def project2d(self, segment):
        return Vertex(window_width / 2, segment.world.z, 0)

    def render2d(self):
        for i in range(len(self.segments) - 1):
            current_segment = self.segments[i]
            next_segment = self.segments[i + 1]

            p1 = self.project2d(next_segment)
            p2 = self.project2d(current_segment)

            print(p1)
            print(p2)
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
            round(1 + projected.x) * (window_width / 2),
            round(1 - projected.y) * (window_height / 2),
            projected.z * (window_width / 2),
        )

    def render3d(self, camera):
        for i in range(len(self.segments) - 1):
            i = 0

            current_segment = self.segments[i]
            next_segment = self.segments[i + 1]
            print(current_segment)
            print(next_segment)

            p1 = self.project3d(next_segment, camera)
            p2 = self.project3d(current_segment, camera)

            print(p1)
            print(p2)
            print("")
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

road = Road()
road.create_roads()

camera = Camera()

arcade.start_render()

#road.render2d()
road.render3d(camera)

arcade.finish_render()
arcade.run()
