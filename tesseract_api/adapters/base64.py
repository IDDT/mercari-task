import base64
import logging
from typing import Optional


def b64decode(b64:str) -> Optional[bytes]:
    '''Decode b64 data into bytes or return None on error.
    '''
    try:
        return base64.b64decode(b64)
    except Exception as e:
        logging.error(f'Failed to decode b64 data exc:{type(e)} msg:{str(e)}')
    return None
