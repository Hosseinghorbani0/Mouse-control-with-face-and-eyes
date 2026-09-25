
"""Control the mouse with head movement and a deliberate blink gesture."""

from __future__ import annotations

import argparse
import math
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parent
FACE_CASCADE_FILE = ROOT / "face_cascade.xml"
EYE_CASCADE_FILE = ROOT / "eye_cascade.xml"


@dataclass(frozen=True)
class Settings:
    camera: int = 0
    face_scale: float = 1.1
    face_neighbors: int = 6
    eye_scale: float = 1.08
    eye_neighbors: int = 6
    tracking_alpha: float = 0.35
    lost_frames: int = 8
    smoothing: float = 0.35
    deadzone: float = 0.08
    sensitivity: float = 0.08
    click_cooldown: float = 0.8
    closed_frames: int = 3


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--face-scale", type=float, default=1.1)
    parser.add_argument("--face-neighbors", type=int, default=6)
    parser.add_argument("--eye-scale", type=float, default=1.08)
    parser.add_argument("--eye-neighbors", type=int, default=6)
    parser.add_argument("--tracking-alpha", type=float, default=0.35)
    parser.add_argument("--lost-frames", type=int, default=8)
    parser.add_argument("--smoothing", type=float, default=0.35)
    parser.add_argument("--deadzone", type=float, default=0.08)
    parser.add_argument("--sensitivity", type=float, default=0.08)
    parser.add_argument("--click-cooldown", type=float, default=0.8)
    parser.add_argument("--closed-frames", type=int, default=3)
    args = parser.parse_args()
    if not 0 < args.smoothing <= 1 or not 0 <= args.deadzone < 0.5:
        parser.error("smoothing must be in (0, 1] and deadzone must be in [0, 0.5)")
    if args.face_neighbors < 1 or args.eye_neighbors < 1 or args.lost_frames < 1:
        parser.error("neighbor and lost-frame values must be positive")
    if not 0 < args.tracking_alpha <= 1:
        parser.error("tracking-alpha must be in (0, 1]")
    if not 0 < args.sensitivity <= 0.3:
        parser.error("sensitivity must be in (0, 0.3]")
    return Settings(
        camera=args.camera,
        face_scale=args.face_scale,
        face_neighbors=args.face_neighbors,
        eye_scale=args.eye_scale,
        eye_neighbors=args.eye_neighbors,
        tracking_alpha=args.tracking_alpha,
        lost_frames=args.lost_frames,
        smoothing=args.smoothing,
        deadzone=args.deadzone,
        sensitivity=args.sensitivity,
        click_cooldown=args.click_cooldown,
        closed_frames=args.closed_frames,
    )


def largest_face(faces: Sequence[tuple[int, int, int, int]]) -> tuple[int, int, int, int] | None:
    return max(faces, key=lambda face: face[2] * face[3], default=None)


def smooth_face(previous, current, alpha: float):
    if previous is None:
        return current
    return tuple(round(old + (new - old) * alpha) for old, new in zip(previous, current))


def normalized_offset(face: tuple[int, int, int, int], frame_size: tuple[int, int]) -> tuple[float, float]:
    x, y, width, height = face
    frame_width, frame_height = frame_size
    center_x = (x + width / 2) / frame_width
    center_y = (y + height / 2) / frame_height
    return center_x - 0.5, center_y - 0.5


def movement(offset: float, deadzone: float, screen_size: int, sensitivity: float = 0.08) -> int:
    if abs(offset) <= deadzone:
        return 0
    active_range = max(0.01, 0.5 - deadzone)
    return round((offset - math.copysign(deadzone, offset)) / active_range * screen_size * 0.12)
    return round((offset - math.copysign(deadzone, offset)) / active_range * screen_size * sensitivity)


def draw_status(frame, face, eyes, tracking, click_ready):
    height, width = frame.shape[:2]
    color = (60, 220, 120) if tracking else (80, 150, 240)
    cv2.rectangle(frame, (12, 12), (width - 12, height - 12), color, 2)
    if face is not None:
        x, y, face_width, face_height = face
        cv2.rectangle(frame, (x, y), (x + face_width, y + face_height), (255, 180, 40), 2)
        for eye_x, eye_y, eye_width, eye_height in eyes:
            cv2.rectangle(frame, (x + eye_x, y + eye_y),
                          (x + eye_x + eye_width, y + eye_y + eye_height), (200, 80, 220), 2)
    status = "TRACKING" if tracking else "SEARCHING"
    if click_ready:
        status += " | BLINK TO CLICK"
    cv2.putText(frame, status, (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, "Q / ESC: quit", (24, height - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)


def run(settings: Settings) -> None:
    import pyautogui

    face_model = cv2.CascadeClassifier(str(FACE_CASCADE_FILE))
    eye_model = cv2.CascadeClassifier(str(EYE_CASCADE_FILE))
    if face_model.empty() or eye_model.empty():
        raise RuntimeError("Could not load face_cascade.xml or eye_cascade.xml")

    camera = cv2.VideoCapture(settings.camera)
    if not camera.isOpened():
        raise RuntimeError(f"Could not open camera {settings.camera}")
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    screen_width, screen_height = pyautogui.size()
    previous_x, previous_y = pyautogui.position()
    closed_count = 0
    last_click = 0.0
    stable_face = None
    lost_count = 0
    eyes_were_open = False
    blink_armed = True

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Warning: camera frame could not be read")
                continue
            frame = cv2.flip(frame, 1)
            gray = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            faces = face_model.detectMultiScale(
                gray, scaleFactor=settings.face_scale, minNeighbors=settings.face_neighbors,
                minSize=(80, 80)
            )
            detected_face = largest_face(faces)
            if detected_face is not None:
                stable_face = smooth_face(stable_face, detected_face, settings.tracking_alpha)
                lost_count = 0
            else:
                lost_count += 1
                if lost_count > settings.lost_frames:
                    stable_face = None
            face = stable_face
            eyes = []
            now = time.monotonic()
            if face is not None and detected_face is not None:
                x, y, width, height = face
                face_gray = gray[y:y + height, x:x + width]
                eye_region = face_gray[:round(height * 0.65), :]
                eyes = list(eye_model.detectMultiScale(
                    eye_region, settings.eye_scale, settings.eye_neighbors,
                    minSize=(max(16, width // 8), max(12, height // 12))
                ))
                offset_x, offset_y = normalized_offset(face, (frame.shape[1], frame.shape[0]))
                target_x = previous_x + movement(offset_x, settings.deadzone, screen_width, settings.sensitivity)
                target_y = previous_y + movement(offset_y, settings.deadzone, screen_height, settings.sensitivity)
                target_x = max(0, min(screen_width - 1, target_x))
                target_y = max(0, min(screen_height - 1, target_y))
                cursor_x = round(previous_x + (target_x - previous_x) * settings.smoothing)
                cursor_y = round(previous_y + (target_y - previous_y) * settings.smoothing)
                pyautogui.moveTo(cursor_x, cursor_y, duration=0)
                previous_x, previous_y = cursor_x, cursor_y
                if eyes:
                    eyes_were_open = True
                    blink_armed = True
                    closed_count = 0
                elif eyes_were_open:
                    closed_count += 1
                if (closed_count >= settings.closed_frames and blink_armed
                        and now - last_click >= settings.click_cooldown):
                    pyautogui.click()
                    last_click = now
                    closed_count = 0
                    blink_armed = False
            draw_status(frame, face, eyes, detected_face is not None,
                        now - last_click >= settings.click_cooldown)
            cv2.imshow("Face Mouse", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


def main() -> int:
    try:
        run(parse_args())
    except KeyboardInterrupt:
        print("Stopped")
    except RuntimeError as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






