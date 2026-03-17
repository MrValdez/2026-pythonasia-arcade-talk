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
    color_road: arcade.types.Color
    color_grass: arcade.types.Color
    color_side: arcade.types.Color
    color_lane: arcade.types.Color | None = None


class Camera:
    def __init__(self, road):
        self.pos = Vertex(0, 500, 0)
        self.dist_to_player = 50
        self.road = road

    def update(self, player):
        self.near_plane = 1 / (self.pos.y / self.dist_to_player)
        self.pos.x = player.pos.x - window_width / 2
        self.pos.z = player.pos.z - self.dist_to_player

        # this will trigger if our camera goes past the last segment
        if self.pos.z < 0:
            self.pos.z += self.road.road_length


class Player:
    def __init__(self, camera, road):
        self.road = road
        self.camera = camera

        self.pos = Vertex(window_width / 2, 0, 0)
        self.max_speed = 500
        self.speed = 0
        self.turn_speed = 20
        self.velocity = 10

    def update(self, dt):
        self.speed = min(self.max_speed, self.speed)
        speed = self.speed * dt
        self.pos.z += speed

        if self.pos.z > self.road.road_length:
            # teleport player to start of road
            self.pos.z -= self.road.road_length

    def move(self, steer_left, steer_right, accelerate, decelerate):
        if steer_left:
            self.pos.x -= self.turn_speed
        if steer_right:
            self.pos.x += self.turn_speed
        if accelerate:
            self.speed += self.velocity
        if decelerate:
            self.speed -= self.velocity

        self.pos.x = max(self.road.side_x[0], self.pos.x)
        self.pos.x = min(self.road.side_x[1], self.pos.x)


class Road:
    def __init__(self):
        self.segment_length = 30
        self.road_length = 0
        self.road_width = 600
        self.road_lanes = 2
        self.segments = []
        self.segment_index = 0
        self.segment_draw_distance = 50
        self.roadside_segments = 3

        self.side_x = [
            (window_width/2) - (self.road_width/2),
            (window_width/2) + (self.road_width/2)
        ]

    def create_roads(self):
        self.create_segments(2000)

        self.segments[0].color_road = arcade.color.PURPLE
        self.segments[-2].color_road = arcade.color.PINK         # last segment is end of the road

        self.road_length = len(self.segments) * self.segment_length

    def create_segments(self, n):
        segments = []
        start_i = len(self.segments)
        for i in range(start_i, start_i + n):
            palletes = {
                "LIGHT": {
                    "road": arcade.color.GRAY,
                    "grass": arcade.color.ARMY_GREEN,
                    "side": arcade.color.WHITE,
                },
                "DARK": {
                    "road": arcade.color.GREEN,
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
            color_side = pallete.get("side")
            color_lane = pallete.get("lane")

            segment = Segment(self.segment_index,
                              Vertex(0, 0, self.segment_index * self.segment_length),
                              Vertex(0, 0, 0),
                              -1,
                              color_road,
                              color_grass,
                              color_side,
                              color_lane)
            self.segment_index += 1
            segments.append(segment)

        self.segments.extend(segments)

    def get_segment(self, z):
        if z < 0:
            z += len(self.segments)
        i = math.floor(z / self.segment_length) % len(self.segments)
        return self.segments[i]

    def project2d(self, segment):
        return Vertex(window_width / 2, segment.world.z, 0)

    def render2d(self):
        drawn = 0

        for i in range(len(self.segments) - 1):
            drawn += 1
            if drawn > self.segment_draw_distance:
                break

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

    def project3d(self, point, camera, offset_z):
        # translate world coordinates to camera coordinates
        translated_camera = Vertex(
            point.world.x - camera.pos.x,
            point.world.y - camera.pos.y,
            point.world.z - camera.pos.z + offset_z,
        )

        # scaling factor based on law of similar triangles
        scale = (camera.near_plane / translated_camera.z)

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
        drawn = 0

        for i in range(len(self.segments)):
            drawn += 1
            if drawn > self.segment_draw_distance:
                break

            segment_i = (camera_segment.index + i) % len(self.segments)

            current_segment = self.segments[segment_i]
            next_segment = self.segments[(segment_i + 1) % len(self.segments)]

            # offset end of road back to start
            offset_z = self.road_length if segment_i < camera_segment.index else 0

            # todo: can be optimized to store the projected coordinates per update instead
            #       of computing each time
            p1 = self.project3d(current_segment, camera, offset_z)
            p2 = self.project3d(next_segment, camera, offset_z)

            if p1.z < 0 or p2.z < 0: continue

            self.draw_segment(
                p1.x, p1.y, p1.z,
                p2.x, p2.y, p2.z,
                current_segment,
            )

    def draw_segment(self, x1, y1, w1, x2, y2, w2, segment):
        points = [
            [0, y1],
            [window_width, y1],
            [window_width, y2],
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


class Game(arcade.Window):
    def __init__(self):
        super().__init__(window_width, window_height)
        #arcade.set_background_color(arcade.color.BLUE)
        self.road = Road()
        self.road.create_roads()
        self.camera = Camera(self.road)
        self.player = Player(self.camera, self.road)

        self.input = {}
        self.sprites = arcade.SpriteList()
        self.sprite_car = arcade.Sprite("car.png")
        self.sprites.append(self.sprite_car)

    def on_draw(self):
        self.clear()

        #self.road.render2d()
        self.road.render3d(self.camera)

        self.sprites.draw()

    def on_key_press(self, key, modifiers):
        self.input[key] = True

    def on_key_release(self, key, modifiers):
        self.input[key] = False

    def on_update(self, dt):
        steer_left = self.input.get(arcade.key.LEFT, False)
        steer_right = self.input.get(arcade.key.RIGHT, False)
        accelerate = self.input.get(arcade.key.UP, False)
        decelerate = self.input.get(arcade.key.DOWN, False)

        self.player.move(steer_left, steer_right, accelerate, decelerate)
        self.sprite_car.position = self.player.pos.x, self.player.pos.y

        self.player.update(dt)
        self.camera.update(self.player)

Game()
arcade.run()
