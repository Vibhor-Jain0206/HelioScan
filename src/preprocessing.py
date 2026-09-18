"""
Image ingestion, integrity verification, LAB CLAHE enhancement,
bilateral edge-preserving filtering, and perspective rectification.
"""

from pathlib import Path
from typing import Tuple, Optional
import cv2
import numpy as np

from .config import PreprocessingConfig


class PreprocessingEngine:
    """Handles low-level image conditioning and solar panel ROI extraction."""

    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()

    @staticmethod
    def load_and_validate(image_path: str) -> np.ndarray:
        """
        Loads an image from disk and performs dimensional and integrity validation.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Input image not found at path: {image_path}")
        
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None or img.size == 0:
            raise ValueError(f"Corrupt or unreadable image file: {image_path}")

        h, w = img.shape[:2]
        if h < 32 or w < 32:
            raise ValueError(f"Image resolution too low ({w}x{h}) for inspection analysis.")

        return img

    def apply_clahe_lab(self, image: np.ndarray) -> np.ndarray:
        """
        Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the
        perceptual Lightness (L) channel in LAB color space, avoiding color distortion.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=self.config.clahe_clip_limit,
            tileGridSize=self.config.clahe_tile_grid
        )
        enhanced_l = clahe.apply(l_channel)

        merged_lab = cv2.merge([enhanced_l, a_channel, b_channel])
        return cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

    def apply_bilateral_filter(self, image: np.ndarray) -> np.ndarray:
        """
        Applies bilateral filtering to smooth surface texture noise while keeping
        wafer micro-cracks and defect boundaries sharply defined.
        """
        return cv2.bilateralFilter(
            image,
            d=self.config.bilateral_d,
            sigmaColor=self.config.bilateral_sigma_color,
            sigmaSpace=self.config.bilateral_sigma_space
        )

    def extract_module_roi(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detects primary solar module polygon and rectifies perspective if needed.
        Returns the rectified image and the 3x3 homography / transformation matrix.
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 140)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        m_ident = np.eye(3, dtype=np.float32)

        if not contours:
            return image.copy(), m_ident

        best_quad = None
        max_area = 0.0
        frame_area = w * h

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 0.20 * frame_area:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
                if len(approx) == 4 and area > max_area:
                    max_area = area
                    best_quad = approx

        if best_quad is None or not self.config.rectify_module:
            return image.copy(), m_ident

        pts = best_quad.reshape(4, 2).astype(np.float32)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        rect = np.zeros((4, 2), dtype=np.float32)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        dst = np.array([
            [0, 0],
            [w - 1, 0],
            [w - 1, h - 1],
            [0, h - 1]
        ], dtype=np.float32)

        transform_matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, transform_matrix, (w, h))
        return warped, transform_matrix

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Executes complete preprocessing chain:
        CLAHE -> Bilateral edge-preserving smoothing -> Module ROI rectification.
        """
        enhanced = self.apply_clahe_lab(image)
        denoised = self.apply_bilateral_filter(enhanced)
        rectified, matrix = self.extract_module_roi(denoised)
        return rectified, matrix
