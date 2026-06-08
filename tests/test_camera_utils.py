"""Unit test untuk camera_utils (lintas platform, tanpa kamera fisik)."""

import sys
import os
from unittest import mock

import cv2
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import camera_utils


class FakeCapture:
    """Tiruan cv2.VideoCapture untuk pengujian."""

    def __init__(self, opened=True):
        self._opened = opened
        self.props = {}
        self.released = False

    def isOpened(self):
        return self._opened

    def set(self, prop, value):
        self.props[prop] = value
        return True

    def release(self):
        self.released = True


def test_get_backend_explicit():
    assert camera_utils.get_backend("any") == cv2.CAP_ANY
    assert camera_utils.get_backend("v4l2") == cv2.CAP_V4L2
    assert camera_utils.get_backend("dshow") == cv2.CAP_DSHOW


def test_get_backend_auto_per_os():
    with mock.patch("camera_utils.platform.system", return_value="Windows"):
        assert camera_utils.get_backend("auto") == cv2.CAP_DSHOW
    with mock.patch("camera_utils.platform.system", return_value="Linux"):
        assert camera_utils.get_backend("auto") == cv2.CAP_ANY
    with mock.patch("camera_utils.platform.system", return_value="Darwin"):
        assert camera_utils.get_backend("auto") == cv2.CAP_ANY


def test_open_camera_success_sets_resolution():
    fake = FakeCapture(opened=True)
    with mock.patch("camera_utils.cv2.VideoCapture", return_value=fake):
        cap = camera_utils.open_camera(0, width=1920, height=1080, backend="any")
    assert cap is fake
    assert cap.props[cv2.CAP_PROP_FRAME_WIDTH] == 1920
    assert cap.props[cv2.CAP_PROP_FRAME_HEIGHT] == 1080


def test_open_camera_auto_resolution_not_set():
    fake = FakeCapture(opened=True)
    with mock.patch("camera_utils.cv2.VideoCapture", return_value=fake):
        cap = camera_utils.open_camera(0, width="auto", height="auto", backend="any")
    assert cap is fake
    assert cv2.CAP_PROP_FRAME_WIDTH not in cap.props
    assert cv2.CAP_PROP_FRAME_HEIGHT not in cap.props


def test_open_camera_failure_returns_none_and_releases():
    fake = FakeCapture(opened=False)
    with mock.patch("camera_utils.cv2.VideoCapture", return_value=fake):
        cap = camera_utils.open_camera(3, backend="any")
    assert cap is None
    assert fake.released is True


def test_find_camera_returns_first_available():
    caps = [FakeCapture(opened=False), FakeCapture(opened=True)]

    def factory(index, backend):
        return caps[index]

    with mock.patch("camera_utils.cv2.VideoCapture", side_effect=factory):
        index, cap = camera_utils.find_camera(max_scan=2, backend="any")
    assert index == 1
    assert cap is caps[1]


def test_find_camera_none_when_no_camera():
    with mock.patch("camera_utils.cv2.VideoCapture",
                    return_value=FakeCapture(opened=False)):
        index, cap = camera_utils.find_camera(max_scan=3, backend="any")
    assert index is None
    assert cap is None


def test_resolve_camera_auto_scans():
    fake = FakeCapture(opened=True)
    with mock.patch("camera_utils.cv2.VideoCapture", return_value=fake):
        index, cap = camera_utils.resolve_camera("auto", max_scan=3, backend="any")
    assert index == 0
    assert cap is fake


def test_resolve_camera_explicit_index():
    fake = FakeCapture(opened=True)
    with mock.patch("camera_utils.cv2.VideoCapture", return_value=fake):
        index, cap = camera_utils.resolve_camera(2, backend="any")
    assert index == 2
    assert cap is fake


def test_resolve_camera_explicit_index_failure():
    with mock.patch("camera_utils.cv2.VideoCapture",
                    return_value=FakeCapture(opened=False)):
        index, cap = camera_utils.resolve_camera(2, backend="any")
    assert index is None
    assert cap is None
