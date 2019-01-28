import unittest

from im.im import _rename


class TestRename(unittest.TestCase):

    def test_01_rename(self):
        _rename('./data/pyramids.jpg', pattern='%Y_%m_%d-%H_%M_%S-ORIG_NAME.jpg', overwrite=False)
