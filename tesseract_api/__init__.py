from flask import Flask, request, jsonify
from .adapters import b64decode, ocr_image_bytes
from .task_pipeline import TaskPipeline


tasks = TaskPipeline()
app = Flask(__name__)


@app.route('/image-sync', methods=['POST'])
def image_sync():
    '''Run tesseract on b64-encoded image a blocking fashion.
        request: '{"image_data": "<b64 encoded image>"}'
        response: '{"text": "<recognized text>"}'
    '''
    if (img_b64 := request.get_json().get('image_data')) is None:
        return jsonify({'error': 'image_data is missing'}), 400
    if (img_bytes := b64decode(img_b64)) is None:
        return jsonify({'error': 'malformed b64 data'}), 400
    return jsonify({'text': ocr_image_bytes(img_bytes)})


@app.route('/image', methods=['POST', 'GET'])
def image():
    '''Submit a job to run tesseract on b64-encoded image or check the result.
    POST request adds image to the processing queue.
        request: '{"image_data": "<b64 encoded image>"}'
        response: '{"task_id": "<task id>"}'
    GET request get the resulting text or null if the result is not ready.
        request: '{"task_id": "<task id>"}'
        response: '{"task_id": "<recognized text>" or null}'
    '''
    #GET request
    if request.method == 'GET':
        if (task_id := request.get_json().get('task_id')) is None:
            return jsonify({'error': 'task_id is missing'}), 400
        if task_id not in tasks:
            return jsonify({'error': 'task_id not created'}), 404
        return jsonify({'task_id': tasks[task_id]})
    #POST request
    if (img_b64 := request.get_json().get('image_data')) is None:
        return jsonify({'error': 'image_data is missing'}), 400
    if (img_bytes := b64decode(img_b64)) is None:
        return jsonify({'error': 'malformed b64 data'}), 400
    return jsonify({'task_id': tasks.append(img_bytes)})
