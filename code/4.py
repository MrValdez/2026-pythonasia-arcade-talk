class Camera:
    # ...
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
        self.speed = self.max_speed
        self.turn_speed = 300
        self.velocity = 0.3

    def update(self, dt):
        self.pos.z += self.speed

        if self.pos.z > self.road.road_length:
            # teleport player to start of road
            self.pos.z -= self.road.road_length

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

        self.speed = min(self.max_speed, self.speed)
        self.speed = max(-1, self.speed)


class Game(arcade.Window):
    def __init__(self):
        # ...
        self.player = Player(self.camera, self.road)

        self.input = {}
        self.sprites = arcade.SpriteList()

        self.sprite_car = arcade.Sprite("car.png")
        self.sprite_car_width = self.sprite_car.width
        self.sprites.append(self.sprite_car)

    def on_draw(self):
        # ...
        current_i = self.road.get_segment_index(self.player.pos.z)
        current = self.road.segments[current_i]
        position, scale = project3d(
            Vertex(self.player.pos.x, -current.world.y, self.player.pos.z),
            self.camera,
            0, 0,
            1,
            #self.sprite_car_width
        )

        # number to tweak. todo: haven't found a mathematical way to extract this correctly
        scaling_constant = 1200

        self.sprite_car.scale = 1/ (scaling_constant * -scale)
        self.sprite_car.position = self.player.pos.x, -position.y
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
