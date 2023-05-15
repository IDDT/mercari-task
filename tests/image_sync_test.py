import os
import re
import shutil
import base64
import unittest
import tempfile
from PIL import Image, ImageDraw, ImageFont
from tesseract_api import app


app.config.update({"TESTING": True})


TEXTS = [
    'this is some text to check api is working',
    'this is to test newlines'
]


class ImageSyncTest(unittest.TestCase):

    def setUp(self):
        self.text = '\n'.join(TEXTS)
        self.client = app.test_client()
        self.temp_dir = tempfile.mkdtemp()
        self.extensions = ('jpg', 'png', 'tif')
        self.clean_text = lambda x: re.sub('\n+', ';', x).strip(';')
        #Generate test images.
        font = ImageFont.truetype('LiberationMono-Regular.ttf', size=22)
        img = Image.new("RGB", (640, 480), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((28, 36), self.text, font=font, fill=(0, 0, 0))
        for ext in self.extensions:
            img.save(os.path.join(self.temp_dir, f'img.{ext}'))
        img.close()

    def tearDown(self):
        #Remove test images.
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_image_sync(self):
        for ext in self.extensions:
            with open(os.path.join(self.temp_dir, f'img.{ext}'), 'rb') as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
            #Send request and get result.
            resp = self.client.post('/image-sync', json={'image_data': img_b64})
            self.assertEqual(resp.status_code, 200, 'Unexpected status')
            self.assertTrue('text' in resp.get_json(), 'Missing key')
            result = resp.get_json()['text']
            resp.close()
            #Verify result.
            txt, txt_recv = self.clean_text(self.text), self.clean_text(result)
            self.assertSequenceEqual(txt, txt_recv, seq_type=str)
