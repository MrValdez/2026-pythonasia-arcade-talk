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
        -translated_camera.y * scale,
        width * scale,
    )

    return Vertex(
        round((1 + projected.x) * (screen_width / 2)),
        round((1 - projected.y) * (screen_height / 2)),
        projected.z * (screen_width / 2),
    ), scale


class Camera:
    def __init__(self, road):
        self.pos = Vertex(0, 800, 0)
        self.dist_to_player = 100
        self.road = road
        self.near_plane = 1
        self.current_segment = None

    def update(self, player):
        self.near_plane = 1 / (self.pos.y / (self.dist_to_player or 1))

        self.pos.x = player.pos.x - (screen_width / 2)
        self.pos.z = player.pos.z - self.dist_to_player


class Player:
    def __init__(self, camera, road):
        self.road = road
        self.camera = camera

        self.reset()

    def reset(self):
        self.pos = Vertex(screen_width / 2, 0, 0)
        self.max_speed = 14
        self.speed = 0
        self.turn_speed = 300
        self.velocity = 0.3

        self.car_drift = 0.059

    def update(self, dt):
        self.pos.z += self.speed

        if self.pos.z > self.road.road_length:
            # teleport player to start of road
            self.pos.z -= self.road.road_length

        if self.camera.current_segment:
            self.pos.x += self.camera.current_segment.curve * self.car_drift * self.speed
            self.pos.y = self.camera.current_segment.world.y

    def move(self, dt, steer_left, steer_right, accelerate, decelerate):
        if steer_left:
            self.pos.x -= self.turn_speed * dt
        if steer_right:
            self.pos.x += self.turn_speed * dt
        if accelerate:
            self.speed += self.velocity
        if decelerate:
            self.speed -= self.velocity

        self.pos.x = max(self.pos.x, 0)
        self.pos.x = min(self.pos.x, screen_width)

        # grass slowdown
        if self.pos.x < self.road.side_x[0]:
            self.speed *= 0.64
        elif self.pos.x > self.road.side_x[1]:
            self.speed *= 0.64

        self.speed = min(self.max_speed, self.speed)
        self.speed = max(-1, self.speed)


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
        self.roadside_length = 3
        self.current_roadside_i = 0
        self.current_roadside_color_switch = 0

        self.side_x = [
            (screen_width/2) - (self.road_width/2),
            (screen_width/2) + (self.road_width/2)
        ]

    def load_roads(self):
        self.create_segments(100)

        self.segments[0].color_road = arcade.color.PURPLE
        self.segments[-2].color_road = arcade.color.PINK         # last segment is end of the road

        self.road_length = len(self.segments) * self.segment_length
        return

        exit_segment = 40
        exit_segment = self.add_ease("curve", 10, exit_segment, 20, 40, 1)
        exit_segment = self.add_ease("curve", 5, exit_segment, 20, 40, 1)
        exit_segment = self.add_ease("curve", -5, exit_segment, 20, 40, 1)
        exit_segment = self.add_ease("curve", 20, exit_segment, 5, 30, 5)
        exit_segment = self.add_ease("curve", -40, exit_segment, 4, 20, 10)
        exit_segment = self.add_ease("curve", -20, exit_segment, 4, 20, 10)
        exit_segment = self.add_ease("curve", 5, exit_segment, 10, 20, 10)
        exit_segment += 50
        exit_segment = self.add_ease("curve", -10, exit_segment, 40, 20, 10)

        exit_segment = 20
        exit_segment = self.add_ease("hill", 30, exit_segment, 40, 40, 20)
        exit_segment += 40
        exit_segment = self.add_ease("hill", -20, exit_segment, 5, 20, 10)
        exit_segment = self.add_ease("hill", 300, exit_segment, 100, 10, 1)
        exit_segment += 140
        exit_segment = self.add_ease("hill", -200, exit_segment, 5, 20, 10)

    def add_ease(self, type, target, start, enter, hold, exit):
        def ease_in(a, b, per):
            return a + (b-a) * math.pow(per, 2)
        def ease_out(a, b, per):
            return a + (b-a) * ((-math.cos(per * math.pi) / 2) + 0.5)

        # cap max and min targets
        if type == "hill":
            target = min(target, 300)
            target = max(target, -200)

        for i in range(0, enter):
            out = ease_in(0, target, i / enter)

            if type == "curve":
                self.segments[start + i].curve = out
            elif type == "hill":
                self.segments[start + i].world.y = out

        start += i
        for i in range(0, hold):
            if type == "curve":
                self.segments[start + i].curve = target
            elif type == "hill":
                self.segments[start + i].world.y = target

        start += i
        for i in range(0, exit):
            out = ease_out(target, 0, i / exit)

            if type == "curve":
                self.segments[start + i].curve = out
            elif type == "hill":
                self.segments[start + i].world.y = out

        return start + i

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
                    "road": arcade.color.SILVER,
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

    def get_segment_per(self, z):
        return (z % self.segment_length) / self.segment_length

    def get_segment_index(self, z):
        if z < 0:
            z += self.road_length

        return math.floor(z / self.segment_length) % len(self.segments)

    def project2d(self, segment):
        return Vertex(screen_width / 2, segment.world.z, 0)

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
            drawn += 1
            if drawn > self.segment_draw_distance:
                break

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


class Game(arcade.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height)

        self.road = Road()
        self.road.load_roads()
        self.camera = Camera(self.road)
        self.player = Player(self.camera, self.road)

        self.input = {}
        self.sprites = arcade.SpriteList()

        car_back = "2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_0005.png"
        car_left = "2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_0004.png"
        car_right = "2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_0006.png"
        self.sprite_car_l = arcade.texture.load_texture(car_left)
        self.sprite_car_r = arcade.texture.load_texture(car_right)
        self.sprite_car_n = arcade.texture.load_texture(car_back)

        self.sprite_car = arcade.Sprite(self.sprite_car_n, scale=0.4)

        self.sprites.append(self.sprite_car)

        self.backgrounds = [
            # image, depth, scale, offset
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/back.png"),
             0, 1, [0, 0]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/buildings.png"),
             10, 1, [0, 0]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/buildings.png"),
             10, 1, [300, 0]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/palms.png"),
             8, 0.6, [300, 150]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/palms.png"),
             7, 0.5, [290, 140])
        ]

    def on_draw(self):
        self.clear()

        camera_segment = self.camera.current_segment

        for i, (bg, depth, scale, offset) in enumerate(self.backgrounds):
            if camera_segment and depth:
                self.backgrounds[i][3][0] += (1 / depth) * camera_segment.curve * (self.player.speed * .2)
            arcade.draw_texture_rect(bg, arcade.LBWH(offset[0], offset[1],
                                                     screen_width*scale, screen_height*scale))

        #self.road.render2d()
        self.road.render3d(self.camera)

        current_i = self.road.get_segment_index(self.player.pos.z)
        current = self.road.segments[current_i]

        if current.curve > 0:
            self.sprite_car.texture = self.sprite_car_l
        elif current.curve < 0:
            self.sprite_car.texture = self.sprite_car_r
        else:
            self.sprite_car.texture = self.sprite_car_n

        position, scale = project3d(
            Vertex(self.player.pos.x, -current.world.y, self.player.pos.z),
            self.camera,
            0, 0,
            self.sprite_car.width,
        )

        car_offset_y = 120   # small offset to allow us to see car
        self.sprite_car.position = self.player.pos.x, position.y + car_offset_y
        self.sprites.draw()

    def on_key_press(self, key, modifiers):
        self.input[key] = True

        # debug keys
        if key == arcade.key.R:
            # restart
            self.player.reset()
            self.road.reset()
            self.road.load_roads()
        if key == arcade.key.J:
            self.road.road_lanes -= 1
        if key == arcade.key.L:
            self.road.road_lanes += 1
        if key == arcade.key.O:
            self.camera.dist_to_player += 5
            self.road.segment_draw_distance += 10
        if key == arcade.key.P:
            self.camera.dist_to_player -= 5
            self.road.segment_draw_distance -= 10
        if key == arcade.key.I:
            self.camera.pos.y += 10
        if key == arcade.key.K:
            self.camera.pos.y -= 10

    def on_key_release(self, key, modifiers):
        self.input[key] = False

    def on_update(self, dt):
        steer_left = self.input.get(arcade.key.LEFT, False)
        steer_right = self.input.get(arcade.key.RIGHT, False)
        accelerate = self.input.get(arcade.key.UP, False)
        decelerate = self.input.get(arcade.key.DOWN, False)

        self.player.move(dt, steer_left, steer_right, accelerate, decelerate)
        self.sprite_car.position = self.player.pos.x, -self.player.pos.y

        self.player.update(dt)
        self.camera.update(self.player)


class Road2(Road):
    def load_roads(self):
        self.create_segments(1400)

        self.segments[0].color_road = arcade.color.PURPLE
        self.segments[-2].color_road = arcade.color.PINK         # last segment is end of the road

        # song markers
        self.segments[1000].color_road = arcade.color.GREEN
        #self.segments[1400].color_road = arcade.color.GREEN

        self.road_length = len(self.segments) * self.segment_length

        exit_segment = 10
        exit_segment = self.add_ease("curve", 2, exit_segment, 40, 30, 40)
        exit_segment = self.add_ease("curve", -2, exit_segment, 40, 30, 40)
        exit_segment += 100
        exit_segment = self.add_ease("curve", 1, exit_segment, 40, 30, 40)
        exit_segment = self.add_ease("curve", 2, exit_segment, 10, 40, 60)

        exit_segment = self.add_ease("curve", 2, exit_segment, 10, 40, 60)

        exit_segment += 100
        exit_segment = self.add_ease("curve", -1, exit_segment, 5, 200, 30)

        exit_segment = 990
        exit_segment = self.add_ease("curve", 12, exit_segment, 10, 50, 10)
        exit_segment = self.add_ease("curve", -10, exit_segment, 10, 60, 10)
        exit_segment = self.add_ease("curve", 14, exit_segment, 10, 70, 10)
        exit_segment = self.add_ease("curve", 13, exit_segment, 10, 30, 10)
        exit_segment = self.add_ease("curve", -23, exit_segment, 5, 60, 10)


class CheatedPlayer(Player):
    def move(self, dt, steer_left, steer_right, accelerate, decelerate):
        if steer_left:
            self.pos.x -= self.turn_speed * dt
        if steer_right:
            self.pos.x += self.turn_speed * dt
        if accelerate:
            self.speed += self.velocity
        if decelerate:
            self.speed -= self.velocity

        # hardcoded AE86 technique
        self.pos.x = max(283, self.pos.x)
        self.pos.x = min(755, self.pos.x)

        self.speed = min(self.max_speed, self.speed)
        self.speed = max(-1, self.speed)


class GameGenie:
    def __init__(self):
        super().__init__()

        # too much coupling
        self.road = Road2()
        self.road.load_roads()
        self.camera.road = self.road

        # cheat to maintain drift
        self.player = CheatedPlayer(self.camera, self.road)
        self.car_drift = 0

        self.passed_segments = 0

        self.sprite_car_textures = []
        for texture in [
            f"2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_000{i}.png"
            for i in range(8)
        ]:
            self.sprite_car_textures.append(arcade.texture.load_texture(texture))
        self.current_sprite_i = 0
        self.current_sprite_change_trigger = 0

        self.shock = arcade.Sprite(
            arcade.texture.load_texture("shock.png"),
        )
        self.shock.position = [1300, 500]
        self.is_shocked = False
        self.sprites.append(self.shock)

        self.show_text = False

    def on_update(self, dt):
        super().on_update(dt)

        current_i = self.road.get_segment_index(self.player.pos.z)
        if current_i >= self.passed_segments:
            self.passed_segments += 1

        if self.passed_segments >= len(self.road.segments):
            self.on_draw = self.scene_victory_draw
            self.on_update = self.scene_victory_update

            self.sprite_car.position = self.sprite_car.position[0], 120
        elif self.passed_segments > 1200:
            self.is_shocked = False
            self.shock.visible = False
        elif self.passed_segments > 1000:
            self.is_shocked = True

        if self.is_shocked:
            pos_x = self.shock.position[0] - 40
            pos_x = max(300, pos_x)
            self.shock.position = (pos_x, self.shock.position[1])
            self.shock.update()

    def scene_victory_update(self, dt):
        self.sprite_car.texture = self.sprite_car_textures[int(self.current_sprite_i)]

        self.current_sprite_change_trigger += (1 / dt)

        target_anim_frame = 400
        if self.current_sprite_change_trigger > target_anim_frame:
            self.current_sprite_i += 1
            self.current_sprite_change_trigger -= target_anim_frame

        self.current_sprite_i %= len(self.sprite_car_textures)

        if self.sprite_car.position[1] <= 500:
            self.sprite_car.position = self.sprite_car.position[0], self.sprite_car.position[1] + 2
        else:
            self.show_text = True

    def scene_victory_draw(self):
        self.clear()

        self.sprites.draw()

        if self.show_text:
            arcade.draw_text("Game Over",
                         0,
                         300,
                         arcade.color.WHITE,
                         20,
                         width=self.get_size()[0],
                         align="center")



class Game2(GameGenie, Game):
    pass

if __name__ == "__main__":
    Game2()
    arcade.run()
