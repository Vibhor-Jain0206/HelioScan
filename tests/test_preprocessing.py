"""
Unit tests for image loading, validation, CLAHE, bilateral filter, and ROI extraction.
"""

import pytest
import numpy as np
import cv2
import tempfile
import os

from src.preprocessing import PreprocessingEngine
from src.config import PreprocessingConfig


@pytest.fixture
def engine():
    return PreprocessingEngine()


@pytest.fixture
def synthetic_image():
    # 640x512 BGR test image
    img = np.full((512, 640, 3), (85, 55, 30), dtype=np.uint8)
    # Add a quadrilateral border
    cv2.rectangle(img, (20, 20), (620, 492), (180, 180, 190), 4)
    return img


def test_load_and_validate_success(synthetic_image):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        cv2.imwrite(f.name, synthetic_image)
        loaded = PreprocessingEngine.load_and_validate(f.name)
        assert loaded is not None
        assert loaded.shape == (512, 640, 3)
        assert loaded.dtype == np.uint8
    os.remove(f.name)


def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        PreprocessingEngine.load_and_validate("non_existent_file_path.jpg")


def test_load_low_resolution():
    tiny = np.zeros((16, 16, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        cv2.imwrite(f.name, tiny)
        with pytest.raises(ValueError):
            PreprocessingEngine.load_and_validate(f.name)
    os.remove(f.name)


def test_apply_clahe_lab(engine, synthetic_image):
    enhanced = engine.apply_clahe_lab(synthetic_image)
    assert enhanced.shape == synthetic_image.shape
    assert enhanced.dtype == np.uint8
    # Should maintain standard channel depth
    assert not np.array_equal(enhanced, synthetic_image)


def test_apply_bilateral_filter(engine, synthetic_image):
    filtered = engine.apply_bilateral_filter(synthetic_image)
    assert filtered.shape == synthetic_image.shape
    assert filtered.dtype == np.uint8


def test_extract_module_roi(engine, synthetic_image):
    warped, matrix = engine.extract_module_roi(synthetic_image)
    assert warped.shape == synthetic_image.shape
    assert matrix.shape == (3, 3)


def test_complete_preprocessing_pipeline(engine, synthetic_image):
    processed, matrix = engine.process(synthetic_image)
    assert processed.shape == synthetic_image.shape
    assert matrix is not None
