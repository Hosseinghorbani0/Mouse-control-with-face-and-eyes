import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Mouse-control-with-face-and-eyes.py")
SPEC = importlib.util.spec_from_file_location("face_mouse", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_largest_face_prefers_area():
    faces = [(10, 10, 20, 20), (4, 5, 40, 30)]
    assert MODULE.largest_face(faces) == (4, 5, 40, 30)


def test_largest_face_returns_none_for_empty_input():
    assert MODULE.largest_face([]) is None


def test_normalized_offset_uses_face_center():
    assert MODULE.normalized_offset((25, 25, 50, 50), (100, 100)) == (0.0, 0.0)
    assert MODULE.normalized_offset((0, 0, 20, 20), (100, 100)) == (-0.4, -0.4)


def test_movement_respects_deadzone():
    assert MODULE.movement(0.05, 0.1, 1000) == 0
    assert MODULE.movement(-0.25, 0.1, 1000) < 0
    assert MODULE.movement(0.25, 0.1, 1000) > 0
