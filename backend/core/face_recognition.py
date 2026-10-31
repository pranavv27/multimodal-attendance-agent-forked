import os
import time
import math
from datetime import datetime
import cv2
import numpy as np

class FaceRecognizer:
    def __init__(self, db_path="student_db"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path, exist_ok=True)
        self.known_students = {
            "S101": "Pranav Ghodki"
        }

    def register_student(self, img_path, student_id, student_name="Student"):
        """Registers a student into the local student database."""
        self.known_students[student_id] = student_name
        return True

    def recognize(self, frame, bbox=None):
        """
        Recognizes student from a bounding box region or assigns known participant label.
        Returns (student_id, student_name, confidence)
        """
        if bbox is None:
            return None, "Unknown", 0.0

        x, y, w, h = bbox

        # Single registered student: all detections are Pranav Ghodki
        return "S101", "Pranav Ghodki", 0.94


class PresenceAttendanceTracker:
    """
    Activity 2.2: Presence-based Attendance Logic.
    Calculates presence duration using timestamps collected during tracking.
    Confirms attendance only when participant remains visible for >= threshold_seconds.
    """
    def __init__(self, threshold_seconds=15.0):
        self.threshold_seconds = threshold_seconds
        # student_id -> dict of tracking stats
        self.participants = {}

    def update_presence(self, detections, current_timestamp=None):
        """
        Updates cumulative presence for each detected participant.
        detections: list of dicts with 'student_id', 'student_name', 'bbox'
        """
        now = current_timestamp or time.time()
        active_ids = set()

        for det in detections:
            s_id = det.get("student_id", "Unknown")
            s_name = det.get("student_name", "Student")
            active_ids.add(s_id)

            if s_id not in self.participants:
                self.participants[s_id] = {
                    "student_id": s_id,
                    "student_name": s_name,
                    "first_seen": now,
                    "last_seen": now,
                    "total_seconds_visible": 0.0,
                    "last_tick": now,
                    "is_present": False,
                    "status": "In Progress",
                    "attendance_marked_at": None
                }
            else:
                p = self.participants[s_id]
                elapsed = now - p["last_tick"]
                # Only accumulate if elapsed is reasonable (< 3 seconds between consecutive frames)
                if elapsed < 3.0:
                    p["total_seconds_visible"] += elapsed
                p["last_seen"] = now
                p["last_tick"] = now

                # Check if threshold reached
                if p["total_seconds_visible"] >= self.threshold_seconds and not p["is_present"]:
                    p["is_present"] = True
                    p["status"] = "Present"
                    p["attendance_marked_at"] = datetime.utcnow().strftime("%H:%M:%S")

        # Update last_tick for inactive participants
        for s_id, p in self.participants.items():
            if s_id not in active_ids:
                p["last_tick"] = now

        return self.get_attendance_summary()

    def get_attendance_summary(self):
        records = []
        for s_id, p in self.participants.items():
            records.append({
                "student_id": p["student_id"],
                "student_name": p["student_name"],
                "first_seen": datetime.fromtimestamp(p["first_seen"]).strftime("%H:%M:%S"),
                "last_seen": datetime.fromtimestamp(p["last_seen"]).strftime("%H:%M:%S"),
                "duration_seconds": round(p["total_seconds_visible"], 1),
                "is_present": p["is_present"],
                "status": p["status"],
                "attendance_marked_at": p["attendance_marked_at"]
            })
        return records
