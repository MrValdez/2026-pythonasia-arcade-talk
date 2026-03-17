class Road:
    #...
    def load_roads(self):
        #...

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

#...
class Game(arcade.Window):
    def __init__(self):
        #...
        self.backgrounds = [
            # image, depth, offset
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/back.png"),
             0, [0, 0]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/buildings.png"),
             10, [0, 0]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/buildings.png"),
             10, [300, 0]),
            (arcade.load_texture(":resources:/images/miami_synth_parallax/layers/palms.png"),
             8, [300, 0])
        ]

    def on_draw(self):
        self.clear()

        camera_segment = self.camera.current_segment

        for i, (bg, depth, offset) in enumerate(self.backgrounds):
            if camera_segment and depth:
                self.backgrounds[i][2][0] += (1 / depth) * camera_segment.curve * (self.player.speed * .2)
            arcade.draw_texture_rect(bg, arcade.LBWH(offset[0], offset[1], screen_width, screen_height))
