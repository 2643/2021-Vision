# Galactic Search Challenge

[ProbablyanAsian's](https://github.com/probablyanasian) code for finding markers and power cells on a co-processor running Python 3.x

Each code has debug constants and values inside at the top, so tweak with them to make the code work.

---

[ball_tracking.py](./ball_tracking.py) tracks the power cell

This code currently uses:

 - [OpenCV](https://pypi.org/project/opencv-python/)
 - [Numpy](https://pypi.org/project/numpy/)
 - [Network Tables](https://pypi.org/project/pynetworktables/)
- [imutils](https://pypi.org/project/imutils/)
- ... and various other standard Python libraries



---

[marker_tracking.py](./marker_tracking.py) was branched off from ball tracking, and recognizes FRC Team 2643's markers... or something blue over something red... such as duct tape on 2x4s.

This code uses the same libraries as ball tracking, being a variant with more complex math to validate markers being... markers.