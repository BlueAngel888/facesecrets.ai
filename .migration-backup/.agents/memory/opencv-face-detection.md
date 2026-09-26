---
name: OpenCV face detection compatibility
description: Dependency constraint required by the portrait preflight detector.
---

Keep OpenCV pinned to a release that includes the Haar cascade classifier API used by the portrait preflight.

**Why:** A newer installed wheel exposed basic image functions but omitted `CascadeClassifier`, causing every real analysis to fail before reaching the AI service.

**How to apply:** When updating Python dependencies, verify both `cv2.CascadeClassifier` and the bundled frontal-face cascade are available before accepting the upgrade.