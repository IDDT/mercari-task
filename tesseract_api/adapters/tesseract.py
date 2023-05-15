import subprocess
import logging


def _run_tesseract(filepath:str, stdin:bytes=b'') -> str:
    '''Run tesseract cmd in shell.
    Arguments:
        filepath: image filepath or 'stdin' to use stdin argument.
        stdin: image bytes, ignored if filepath is not set to 'stdin'.
    Returns:
        str: parsed image text.
    '''
    try:
        out = subprocess.run([
            'tesseract', '--psm', '1', '--oem', '1', filepath, 'stdout'
        ], input=stdin, capture_output=True, check=True, timeout=30)
    except subprocess.CalledProcessError as e:
        code, msg = e.returncode, e.stderr.decode('utf-8').replace('\n', ';')
        logging.error(f'tesseract cmd failed with code:{code} msg:{msg}')
    except Exception as e:
        logging.error(f'tesseract cmd failed with exc:{type(e)} msg:{str(e)}')
    else:
        return out.stdout.decode('utf-8')
    return ''


def ocr_image_file(filepath:str) -> str:
    '''Run OCR on image file by specifying filepath.
    '''
    return _run_tesseract(filepath)


def ocr_image_bytes(b:bytes):
    '''Run OCR on image file by feeding image file bytes.
    '''
    return _run_tesseract('stdin', b)
