class Road:
    #...
    def load_roads(self):
        #...

        exit_segment = 0
        exit_segment = self.add_ease("hill", 300, exit_segment, 10, 40, 20)
        exit_segment += 40
        exit_segment = self.add_ease("hill", -200, exit_segment, 10, 40, 20)
        exit_segment = self.add_ease("hill", 300, exit_segment, 10, 40, 5)


    def add_ease(self, type, target, start, enter, hold, exit):
        #...

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
