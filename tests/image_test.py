import os
import re
import time
import shutil
import base64
import unittest
import tempfile
from typing import Union
from PIL import Image, ImageDraw, ImageFont
from tesseract_api import app


app.config.update({"TESTING": True})


TEXTS = [
    'this is some text to check api is working',
    'this is to test newlines'
]


class ImageTest(unittest.TestCase):

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

    def test_get_missing_task_id(self):
        resp = self.client.get('/image', json={})
        self.assertEqual(resp.status_code, 400, 'Unexpected status')
        resp.close()

    def test_get_unknown_task_id(self):
        resp = self.client.get('/image', json={'task_id': 'zzz'})
        self.assertEqual(resp.status_code, 404, 'Unexpected status')
        resp.close()

    def test_post_missing_image_data(self):
        resp = self.client.post('/image', json={})
        self.assertEqual(resp.status_code, 400, 'Unexpected status')
        resp.close()

    def test_image(self):
        for ext in self.extensions:
            with open(os.path.join(self.temp_dir, f'img.{ext}'), 'rb') as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
            #Submit image and get a task_id.
            resp = self.client.post('/image', json={'image_data': img_b64})
            self.assertEqual(resp.status_code, 200, 'Unexpected status')
            self.assertTrue('task_id' in resp.get_json(), 'Missing key')
            task_id = resp.get_json()['task_id']
            resp.close()
            #Wait for result indefinitely.
            result = None
            while result is None:
                resp = self.client.get('/image', json={'task_id': task_id})
                self.assertEqual(resp.status_code, 200, 'Unexpected status')
                self.assertTrue('task_id' in resp.get_json(), 'Missing key')
                result = resp.get_json()['task_id']
                resp.close()
                self.assertIsInstance(result, Union[None, str], 'Wrong type')
                time.sleep(1)
            #Verify result.
            txt, txt_recv = self.clean_text(self.text), self.clean_text(result)
            self.assertSequenceEqual(txt, txt_recv, seq_type=str)
