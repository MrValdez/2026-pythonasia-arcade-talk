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
