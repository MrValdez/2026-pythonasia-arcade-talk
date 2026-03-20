class Player:
    #...
    def reset(self):
        #...
        self.car_drift = 0.059

    def update(self, dt):
        #...
        if self.camera.current_segment:
            self.pos.x += self.camera.current_segment.curve * self.car_drift * self.speed
            self.pos.y = self.camera.current_segment.world.y

    def move(self, dt, steer_left, steer_right, accelerate, decelerate):
        #...

        # grass slowdown
        if self.pos.x < self.road.side_x[0]:
            self.speed *= 0.64
        elif self.pos.x > self.road.side_x[1]:
            self.speed *= 0.64

        self.speed = min(self.max_speed, self.speed)
        self.speed = max(-1, self.speed)


class Road:
    #...
    def reset(self):
        #...
        self.side_x = [
            (screen_width/2) - (self.road_width/2),
            (screen_width/2) + (self.road_width/2)
        ]


class Game:
    def __init__(self):
        #...
        car_back = "2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_0005.png"
        car_left = "2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_0004.png"
        car_right = "2D_Car_Pack_DevilsWorkShop_V01/car01/car01iso_0006.png"
        self.sprite_car_l = arcade.texture.load_texture(car_left)
        self.sprite_car_r = arcade.texture.load_texture(car_right)
        self.sprite_car_n = arcade.texture.load_texture(car_back)

        self.sprite_car = arcade.Sprite(self.sprite_car_n, scale=0.4)

    def update(self):
        #...
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


