import sounddevice as sd
import numpy as np
from scipy.signal import correlate, chirp
import keyboard

class Echolocation:
    def __init__(self, sample_rate=44100, duration=0.1):
        self.sample_rate = sample_rate
        self.duration = duration
        self.signal = self.generate_signal()

    def generate_signal(self):
       t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), endpoint=False)
       return 0.5 * chirp(t, f0=500, f1=4000, t1=self.duration, method='linear')

    def play_signal(self):
        sd.play(self.signal, self.sample_rate)
        sd.wait()

    def record_echo(self):
        echo = sd.rec(int(self.sample_rate * self.duration), samplerate=self.sample_rate, channels=1)
        sd.wait()
        return echo.flatten()

    def t_delay(self, echo, sig2 = None):
        # Simple processing to find the time delay of the echo
        if sig2 is None:
            sig2 = self.signal
            # const = -1
        correlation = np.correlate(echo, sig2, mode='full')
        delay_index = np.argmax(correlation) - (len(sig2) - 1)
        time_delay = delay_index / self.sample_rate
        return time_delay
    
    def distance(self, echo):
        # Calculate the distance based on the time delay
        speed_of_sound = 343  # Speed of sound in air in m/s
        time_delay = self.t_delay(echo)
        distance = (time_delay * speed_of_sound) / 2  # Divide by 2 for round trip
        return distance
    
    # def locate(self, echo):
    #     mic_distance = 0.15  # Distance between the two microphones in meters
    #     left = echo[:,0]
    #     right = echo[:,1]
    #     corr = correlate(left, right, mode='full')
    #     delay_index = np.argmax(corr) - len(right) + 1
    #     time_delay = delay_index / self.sample_rate

    #     max_time_delay = mic_distance / 343  # Maximum time delay based on microphone distance
    #     if abs(time_delay) > max_time_delay:
    #         return None  # Echo is too far to be detected
    #     angle = np.arcsin(time_delay * 343 / mic_distance)  # Calculate angle of arrival
    #     return np.degrees(angle)
    
    # def potential_locations(self, echo, count=0):
    #     # This function can be implemented to analyze the echo and determine potential locations of the object
    #     positions = [(0,0), (1,0), (0,1)]
    #     d01 = np.linalg.norm(np.array(positions[0]) - np.array(positions[1]))
    #     d02 = np.linalg.norm(np.array(positions[0]) - np.array(positions[2]))
    #     x0 = np.mean(positions, axis=0)

    #     print(f"Position {count + 1}: {positions[count]}")
    #     # keyboard.on_press_key("space", lambda _: print("Space key pressed!"))
    #     # keyboard.on_release_key("space", lambda _: print("Space key released!"))
    #     # keyboard.wait("esc")  # Wait for the space key to be pressed
    #     p1 = self.record_echo()
        
    #     if count < len(positions) - 1:
    #         p1 += self.potential_locations(echo, count + 1)

    #     # Time delays between positions
    #     if count == len(positions) - 1:
    #         tdoa1 = self.t_delay(p1[0], p1[1])
    #         tdoa2 = self.t_delay(p1[0], p1[2])

class Where(Echolocation):
    """ Should know the direction of the closest object to origin """
    pos:dict
    count:int
    def __init__(self, sample_rate=44100, duration=0.1):
        super().__init__(sample_rate, duration)
        self.pos = {
            0: [ 
                # (0,0)
                # np.array(positions[0])
                # echo
                # distance
            ],
            1: [], # (0,1)
            2: [] # (1,0): 
        }
        self.count = 0
        self.guide = { 0: (0,0), 1: (0,1), 2:(1,0)}
    
    def play(self):
        if len(self.pos[self.count]) == 0:
            self.play_signal()
            echo = self.record_echo()
            self.pos[self.count] = [
                self.guide[self.count],
                np.array(self.guide[self.count]),
                echo,
                self.distance(echo)
            ]
            self.count += 1
    
    def calc(self):
        full = True
        for v in self.pos.values():
            if len(v) == 0:
                full = False
                break
        
        if not full:
            print("not full")
            return None
        
        e = self.pos
        p0, p1, p2 = e[0][1], e[1][1],e[2][1]
        d0, d1, d2 = e[0][3], e[1][3],e[2][3]

        # Triangulation vis lls
        # From: (x-xi)^2 + (y-yi)^2 = di^2
        A = np.array([
            2 * (p1 - p0),
            2 * (p2 - p0)
        ])
        b = np.array([
            d0**2 - d1**2 -np.dot(p0, p0) +np.dot(p1,p1),
            d0**2 - d1**2 -np.dot(p0, p0) +np.dot(p2,p2),
        ])

        # Solve Ax = b (least squares handles near-singular cases)
        target, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        print(f"Estimated target position: x={target[0]:.3f}m, y={target[1]:.3f}m")

        # Direction from your current position (last position used)
        current = np.array(self.pos[self.count - 1][0])
        direction = target - current
        angle = np.degrees(np.arctan2(direction[1], direction[0]))
        print(f"Direction to target: {angle:.1f}° (from +x axis)")

        return target, angle


if __name__ == "__main__":
        # List all audio devices
    # print(sd.query_devices())

    # # See default input device details
    # device_info = sd.query_devices(kind='input')
    # print(f"\nDefault input: {device_info['name']}")
    # print(f"Max channels: {device_info['max_input_channels']}")

    # echolocation = Echolocation()
    # echolocation.play_signal()
    # echo = echolocation.record_echo()
    # time_delay = echolocation.t_delay(echo)
    # print("hi")
    # distance = echolocation.distance(echo)
    # print("hi2")
    # where = echolocation.locate(echo)

    # echo = echolocation.record_echo()
    # time_delay2 = echolocation.t_delay(echo)
    # distance2 = echolocation.distance(echo)
    # where2 = echolocation.locate(echo)

    # print(f"Time delay of the echo: {time_delay:.10f} seconds")
    # print(f"Time delay of the echo (second attempt): {time_delay2:.10f} seconds")
    # print(f"Distance of the echo: {distance:.10f} meters")
    # print(f"Distance of the echo (second attempt): {distance2:.10f} meters")
    # print(f"Angle of arrival of the echo: {where:.10f} degrees")
    # print(f"Angle of arrival of the echo (second attempt): {where2:.10f} degrees")
    w = Where()
    for i in range(3):
        input(f"Move to position {w.guide[i]}, then press Enter...")
        w.play()
        print(f"  Distance measured: {w.pos[i][3]:.3f}m")
    
    w.calc()