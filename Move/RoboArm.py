import numpy as np

class Joints():
    angleUpperLimit: float
    angleLowerLimit: float
    currAngle: float 

    def __init__(self, upper=120, lower=0, curr=0):
        """ degrees """
        self.angleUpperLimit = upper
        self.angleLowerLimit = lower
        self.currAngle = curr

    def angleChange(self, direction):
        finalAngle = self.currAngle + direction

        if finalAngle > self.angleUpperLimit:
            self.currAngle = self.angleUpperLimit

        elif finalAngle < self.angleLowerLimit:
            self.currAngle = self.angleLowerLimit

        else:
            self.currAngle = finalAngle
    

class Limb():
    """ Makes a Limb """
    # {
    #   (x, y): Joints()
    # }
    j_coords:dict={}

    def __init__(self, joints: int, lengths: list[float], angles: list[float]|None=None, origin=(0,0)):
        # 
        ph = origin
        self.j_coords[origin] = Joints()

        for j in range(joints):
            # coords = (coords[0] + lengths[j] * np.cos(a), coords[1] + l * np.sin(a))
            if angles == None:
                jc = (ph[0], ph[1] + lengths[j])
            else:
                jc = (
                    ph[0] + lengths[j] * np.cos(np.radians(angles[j])), 
                    ph[1] + lengths[j] * np.sin(np.radians(angles[j]))
                    )
            self.j_coords[jc] = Joints()
            ph = jc
        pass

    def changeAngle(self, joint, angle):
        pass

class GradientDescent(Limb):
    """ Maybe used for optimal angles to get to target """
    currAng = []
    lengths = []

    def __init__(self, joints, lengths, angles = None, origin=(0, 0)):
        super().__init__(joints, lengths, angles, origin)
        for coords, joint in self.j_coords.items():
            self.currAng.append(joint.currAngle)
        self.lengths = lengths
        self.target = (18, 4)

    
    def error(self, hand, target):
        tar = np.array(target)
        # hand = self.kinematics2d()
        error_form = np.sum((hand - tar)**2)
        return error_form

    def kinematics2d(self, angles=None, lengths=None):
        """ Calculates where the end point ends up """
        # 
        # angles and lengths
        if angles == None or lengths == None:
            angles = []
            lengths = []
            prev = (0, 0)
            for coord, joint in self.j_coords.items():
                if type(coord) == tuple:
                    # x, y = coord
                    p1 = np.array(prev)
                    p2 = np.array(coord)
                    length = np.linalg.norm(p2 - p1)
                    print(length, p2, p1)
                    lengths.append(length)
                    prev = coord

                if type(joint) == Joints:
                    # joints are in degrees
                    angles.append(np.radians(joint.currAngle))
        else:
            # assume angles are also in degrees
            ph = []
            for a in angles:
                ph.append(np.radians(a))
            angles = ph
        # hypothenus is length so x = length * cos and y = length * sin
        coords = (0,0)
        for a, l in zip(angles, lengths):
            # assuming angle is in radians
            coords = (coords[0] + l * np.cos(a), coords[1] + l * np.sin(a))
            print(np.array(coords))
        # endpoint coords
        return np.array(coords)
    
    def derivative(self, eps= 0.001,):
        """how much a particular angle changes the endpoint"""
        joints = len(self.currAng)
        angles2 = self.currAng.copy()

        gradient = []
            
        for i in range(joints):
            angles2[i] += eps
            grad = (
                self.error(
                    self.kinematics2d(angles2, self.lengths),
                    self.target
                ) 
                - self.error(
                    self.kinematics2d(self.currAng, self.lengths),
                    self.target
                )
            )
            gradient.append(grad)

        return gradient
    
    def run(self, iter = 500, lr=0.05):
        for iteration in range(iter):
            hand = self.kinematics2d(self.currAng, self.lengths)
            
            if np.linalg.norm(hand-np.array(self.target)) < 0.01:
                break

            grad = self.derivative()
            for a in range(len(grad)):
                self.currAng[a] -= lr * grad[a]
            

# Gradient Descent
# - Calcs the 

test = GradientDescent(
    joints=5,
    lengths=[5,3,4,2,8],
)
# test.kinematics2d(
#     # angles=[30, 60 , 30],
#     # lengths = [1,1,1]
# )
test.run()
# machine learning
# - needs reward system
#   - speed (remove points the longer you go)
#   - efficiency / optimized
# - constrict
#   - collision is bad