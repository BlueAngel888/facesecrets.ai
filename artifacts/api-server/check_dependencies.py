"""Fail the production build if the face-detection runtime is unavailable."""

import cv2
import numpy as np


def main():
    # OpenCV's GUI and headless distributions share the same cv2 files. Removing
    # a legacy GUI installation can erase an otherwise "installed" headless one.
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if gray.shape != (16, 16):
        raise RuntimeError("OpenCV image conversion failed")

    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    if cascade.empty():
        raise RuntimeError("OpenCV face-detection data is missing")

    print(f"OpenCV {cv2.__version__}: image conversion and face detector ready")


if __name__ == "__main__":
    main()
