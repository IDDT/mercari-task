# tesseract-api
This project exposes tesseract cmdline program as an API. Images can be processed both syncronously in the main thread and asyncronously depending on the endpoints used.


### Endpoints
#### Syncronous execution
- TODO


### Async execution
- TODO


#### Running unittests with Docker
```bash
docker build --tag tesseract_api_test --target test .
```


#### Running locally with Docker
```bash
docker build --tag tesseract_api --target prod .
docker run --name tesseract_api -p 5000:5000/tcp tesseract_api:latest
```


### Enviroment variables
- `N_PROCS=<n_cpus - 1>` override number of concurrent tesseract workers.
- `QUEUE_SIZE=1024` limit the number of scheduled tasks.


### Architecture
```
tesseract_api
├── __init__.py      # Webserver logic & endpoints.
├── adapters
│   ├── __init__.py
│   ├── base64.py    # Base64 wrapper.
│   └── tesseract.py # Tesseract cmd wrappers.
├── config.py        # Various configurations.
└── task_pipeline.py # Implemetation for asyncronous OCR pipeline.
tests                # Unittests.
```


### Areas for improvement
- Needs exteral task queue & result storage for horizontal scalability / graceful shutdown.
- Base64 decoding and image writing can be offloaded to workers for faster task submission.
- Tesseract is available as a Python package - it's likely best to use it instead of calling shell.
- Add reporting for various production metrics, e.g. queue size, task processing time etc.
- Limit the number of stored results to prevent OOM crashes.
- Use a production-grade webserver, like uWSGI.
