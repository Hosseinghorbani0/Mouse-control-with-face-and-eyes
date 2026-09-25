# Face Mouse

Control the cursor with your head and click with a deliberate blink. Face Mouse is a small, local-first computer-vision utility built with OpenCV and PyAutoGUI.

> Use it as an accessibility experiment, a hands-free pointer, or a starting point for gesture-driven interfaces.

## Features

- Real-time face tracking from a webcam
- Smooth cursor movement with a configurable deadzone
- Largest-face selection for predictable tracking
- Blink-to-click gesture with a cooldown against accidental clicks
- Mirrored preview with tracking, eye, and status overlays
- Safe camera/window cleanup on exit and errors
- Command-line configuration without editing source code
- Unit tests for pure movement and geometry logic

## Requirements

- Windows, macOS, or Linux
- Python 3.9+
- A webcam, display, and permission to control the mouse

## Quick start

```bash
python -m venv .venv
# Windows PowerShell
.\\.venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python Mouse-control-with-face-and-eyes.py
```

Press `Q` or `Esc` in the preview window to stop the application.

## Tuning

The defaults work best with the camera at eye level and a well-lit face:

```bash
python Mouse-control-with-face-and-eyes.py --camera 0 --smoothing 0.25 --deadzone 0.1
```

| Option | Default | Purpose |
| --- | ---: | --- |
| `--camera` | `0` | Webcam device index |
| `--face-scale` | `1.1` | Detection pyramid step |
| `--face-neighbors` | `6` | Detection strictness |
| `--eye-scale` | `1.08` | Eye detection pyramid step |
| `--eye-neighbors` | `6` | Eye detection strictness |
| `--tracking-alpha` | `0.35` | Temporal face-box stabilization |
| `--lost-frames` | `8` | Frames tolerated during short tracking loss |
| `--smoothing` | `0.35` | Cursor responsiveness from 0 to 1 |
| `--deadzone` | `0.08` | Center area where the cursor does not move |
| `--sensitivity` | `0.08` | Maximum cursor movement scale |
| `--click-cooldown` | `0.8` | Minimum seconds between blink clicks |
| `--closed-frames` | `3` | Frames without detected eyes to trigger a click |

## Troubleshooting

- **Camera could not be opened:** close other camera applications and try `--camera 1`.
- **Cursor feels too sensitive:** increase `--deadzone` or decrease `--smoothing`.
- **False clicks:** increase `--closed-frames` and `--click-cooldown`; improve lighting.
- **No face detected:** move closer, face the camera, and avoid strong backlighting.

The bundled models are named `face_cascade.xml` and `eye_cascade.xml` and are loaded relative to the Python script.

## Development

```bash
python -m pytest -q
ruff check .
python -m py_compile Mouse-control-with-face-and-eyes.py
```

The Haar cascade files are loaded relative to the script, so the command can be run from any working directory.

## Safety and privacy

Video frames are processed locally and are not recorded or uploaded. Mouse control is powerful: keep the preview visible and stop with `Q` or `Esc` if tracking behaves unexpectedly.

## License

The project code is released under the MIT License. The bundled OpenCV Haar cascades retain their original Intel Open Source Computer Vision license notice.