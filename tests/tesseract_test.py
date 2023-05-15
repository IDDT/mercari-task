import os
import re
import shutil
import unittest
import tempfile
from PIL import Image, ImageDraw, ImageFont
from tesseract_api.adapters.tesseract import ocr_image_file, ocr_image_bytes


TEXTS = [
    'this is some text to check api is working',
    'this is to test newlines'
]


class TesseractTest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.extensions = ('jpg', 'png', 'tif')
        self.clean_text = lambda x: re.sub('\n+', ';', x).strip(';')
        #Generate test images.
        font = ImageFont.truetype('LiberationMono-Regular.ttf', size=22)
        for t, text in enumerate(TEXTS):
            img = Image.new("RGB", (640, 480), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.text((28, 36), text, font=font, fill=(0, 0, 0))
            for ext in self.extensions:
                img.save(os.path.join(self.temp_dir, f'{t}.{ext}'))
            img.close()

    def tearDown(self):
        #Remove test images.
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ocr_image_file(self):
        for t, text in enumerate(TEXTS):
            for ext in self.extensions:
                filepath = os.path.join(self.temp_dir, f'{t}.{ext}')
                result = ocr_image_file(filepath)
                #Verify result.
                txt, txt_recv = self.clean_text(text), self.clean_text(result)
                self.assertSequenceEqual(txt, txt_recv, seq_type=str)

    def test_ocr_image_bytes(self):
        for t, text in enumerate(TEXTS):
            for ext in self.extensions:
                filepath = os.path.join(self.temp_dir, f'{t}.{ext}')
                with open(filepath, 'rb') as f:
                    result = ocr_image_bytes(f.read())
                #Verify result.
                txt, txt_recv = self.clean_text(text), self.clean_text(result)
                self.assertSequenceEqual(txt, txt_recv, seq_type=str)
