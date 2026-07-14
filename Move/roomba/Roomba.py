class Roomba:
    def __init__(self, name):
        self.name = name
        self.position = (0, 0)  # Starting position at the origin
        self.cleaned = set()  # Set to keep track of cleaned positions
        self.power = 100  # Initial power level

    def move(self, direction):
        if self.power <= 0:
            raise ValueError("Roomba is out of power.")
        x, y = self.position
        if direction == 'up':
            self.position = (x, y + 1)
        elif direction == 'down':
            self.position = (x, y - 1)
        elif direction == 'left':
            self.position = (x - 1, y)
        elif direction == 'right':
            self.position = (x + 1, y)
        else:
            raise ValueError("Invalid direction. Use 'up', 'down', 'left', or 'right'.")
        
        self.power -= 1
        self.clean()

    def clean(self):
        # Mark the current position as cleaned
        self.cleaned.add(self.position)

    def get_cleaned_positions(self):
        return self.cleaned

    def get_position(self):
        return self.position