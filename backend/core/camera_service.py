import cv2
import time
import math
import numpy as np

class CameraService:
    def __init__(self, camera_id=0, video_path=None):
        self.camera_id = camera_id
        self.video_path = video_path
        self.cap = None
        self.is_running = False
        self.use_simulation = False
        self._sim_tick = 0

    def start(self):
        if self.cap is None and not self.use_simulation:
            source = self.video_path if self.video_path else self.camera_id
            try:
                self.cap = cv2.VideoCapture(source)
                if not self.cap.isOpened():
                    print(f"Warning: Could not open video source {source}. Falling back to simulation mode.")
                    self.use_simulation = True
                    self.cap = None
                else:
                    self.is_running = True
            except Exception as e:
                print(f"Camera open exception: {e}. Using simulation mode.")
                self.use_simulation = True
        self.is_running = True

    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_running = False

    def get_frame(self):
        if not self.is_running:
            return None

        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            elif self.video_path:
                # Loop recorded classroom video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if ret:
                    return frame

        # Fallback synthetic frame generator if no camera is available
        return self._generate_simulated_frame()

    def _generate_simulated_frame(self):
        """Generates a realistic classroom camera feed with 1 simulated student for testing."""
        self._sim_tick += 1
        frame = np.full((480, 640, 3), 35, dtype=np.uint8)

        # Classroom background
        cv2.putText(frame, "SIMULATED CLASSROOM FEED (LIVE)", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 255), 2)
        cv2.putText(frame, f"Frame: {self._sim_tick}", (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        # Draw Student 1 (Pranav)
        p1_x = 320 + int(10 * math.sin(self._sim_tick * 0.05))
        p1_y = 230
        cv2.circle(frame, (p1_x, p1_y), 50, (120, 160, 200), -1)
        cv2.ellipse(frame, (p1_x, p1_y + 90), (70, 50), 0, 0, 180, (80, 100, 150), -1)

        return frame
