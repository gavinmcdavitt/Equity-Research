import os
import logging

logger = logging.getLogger(__name__)

def validate_filing(file_path: str) -> bool:
    try:
        if not os.path.exists(file_path):
            return False
        if os.path.getsize(file_path) < 10000:
            logger.warning(f"File too small: {file_path}")
            return False
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024).lower()
            if '<html' not in content or '10-k' not in content and '10-q' not in content:
                logger.warning(f"Invalid content in: {file_path}")
                return False
        return True
    except Exception as e:
        logger.error(f"Validation failed for {file_path}: {e}")
        return False