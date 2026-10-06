---
name: OpenCV distribution collisions
description: Why successful dependency synchronization can still leave the Python face-detection runtime unavailable.
---

Do not treat installed OpenCV package metadata as proof that `cv2` works. The GUI and headless distributions overlap on disk; uninstalling a legacy distribution can remove files owned by the retained distribution.

**Why:** A production dependency synchronization succeeded but removed the shared `cv2` files when pruning a legacy GUI distribution. The API then crashed on import, although headless OpenCV was still listed as installed.

**How to apply:** When cleaning or switching OpenCV distributions, restore the retained distribution after removing the obsolete one. Verify actual image operations and bundled detector data as part of the build, rather than relying only on dependency resolution.
