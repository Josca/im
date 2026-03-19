import os

import numpy as np
import pytest
from PIL import Image

from im.im import border, convert, crop, flip, gray, info, resize, stack


@pytest.fixture
def sample_image(tmp_path):
    """Create a simple test RGB image."""
    img = Image.fromarray(np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8))
    path = str(tmp_path / "test.png")
    img.save(path)
    return path


@pytest.fixture
def sample_image_jpg(tmp_path):
    """Create a simple test RGB image in JPEG format."""
    img = Image.fromarray(np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8))
    path = str(tmp_path / "test.jpg")
    img.save(path)
    return path


def test_gray(sample_image, tmp_path):
    gray(files=[sample_image], overwrite=False)
    out = str(tmp_path / "test_gray.png")
    assert os.path.exists(out)
    img = Image.open(out)
    assert img.mode == "L"


def test_gray_overwrite(sample_image):
    gray(files=[sample_image], overwrite=True)
    img = Image.open(sample_image)
    assert img.mode == "L"


def test_resize(sample_image, tmp_path):
    resize(files=[sample_image], overwrite=False, size=50, width=0, height=0)
    out = str(tmp_path / "test_resized.png")
    assert os.path.exists(out)
    img = Image.open(out)
    assert max(img.size) == 50


def test_resize_explicit_dims(sample_image, tmp_path):
    resize(files=[sample_image], overwrite=False, size=1000, width=80, height=60)
    out = str(tmp_path / "test_resized.png")
    img = Image.open(out)
    assert img.size == (80, 60)


def test_flip_horizontal(sample_image, tmp_path):
    flip(files=[sample_image], vertical=False, overwrite=False)
    out = str(tmp_path / "test_flipped.png")
    assert os.path.exists(out)
    original = np.asarray(Image.open(sample_image))
    flipped = np.asarray(Image.open(out))
    np.testing.assert_array_equal(flipped, original[:, ::-1, :])


def test_flip_vertical(sample_image, tmp_path):
    flip(files=[sample_image], vertical=True, overwrite=False)
    out = str(tmp_path / "test_flipped.png")
    original = np.asarray(Image.open(sample_image))
    flipped = np.asarray(Image.open(out))
    np.testing.assert_array_equal(flipped, original[::-1, :, :])


def test_crop(sample_image, tmp_path):
    crop(files=[sample_image], x=10, y=20, width=50, height=30, overwrite=False)
    out = str(tmp_path / "test_cropped.png")
    assert os.path.exists(out)
    img = Image.open(out)
    assert img.size == (50, 30)


def test_border(sample_image, tmp_path):
    border(files=[sample_image], width=5, color="red", overwrite=False)
    out = str(tmp_path / "test_border.png")
    assert os.path.exists(out)
    img = Image.open(out)
    assert img.size == (160, 110)  # 150+2*5, 100+2*5


def test_convert(sample_image, tmp_path):
    convert(files=[sample_image], extension=".jpg", overwrite=False)
    out = str(tmp_path / "test.jpg")
    assert os.path.exists(out)


def test_stack_horizontal(tmp_path):
    img1 = Image.fromarray(np.zeros((100, 50, 3), dtype=np.uint8))
    img2 = Image.fromarray(np.zeros((100, 80, 3), dtype=np.uint8))
    p1 = str(tmp_path / "a.png")
    p2 = str(tmp_path / "b.png")
    img1.save(p1)
    img2.save(p2)
    out = str(tmp_path / "stacked.png")
    stack(files=[p1, p2], output=out, vertical=False)
    assert os.path.exists(out)
    result = Image.open(out)
    assert result.size[1] == 100  # height preserved


def test_info(sample_image, capsys):
    info(files=[sample_image])
    captured = capsys.readouterr()
    assert "Size" in captured.out
    assert "Mode" in captured.out
