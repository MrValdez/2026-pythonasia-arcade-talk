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
