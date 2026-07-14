import cv2

class Visual:
    def __init__(self):
        pass
    
    def see(self, name='img', functions=None):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            
            # grayscale 
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if functions:
                faces = functions(gray)

            # Draw Rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow(name, frame)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    
def detect_faces(gray):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

if __name__ == "__main__":
    visual = Visual()
    visual.see(functions=detect_faces)