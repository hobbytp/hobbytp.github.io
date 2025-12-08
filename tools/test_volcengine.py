import os
import json
import time
import hashlib
import hmac
import requests
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_env():
    """Load .env file manually"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"').strip("'")
        logger.info("Loaded .env file")
    except Exception as e:
        logger.error(f"Failed to load .env: {e}")

def sign_request(access_key, secret_key, method, url, query_params, headers, payload):
    # Get current time
    now = datetime.now(timezone.utc)
    date_stamp = now.strftime('%Y%m%d')
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    
    # Parse URL
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    # Calculate payload hash
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    # Canonical Request
    # Sort query params
    canonical_querystring = '&'.join([f"{k}={v}" for k, v in sorted(query_params.items())])
    
    # Headers
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    canonical_headers = f"content-type:{headers['Content-Type']}\nhost:{host}\nx-content-sha256:{payload_hash}\nx-date:{amz_date}\n"
    
    canonical_request = f"{method}\n{path}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    
    # String to Sign
    algorithm = 'HMAC-SHA256'
    region = "cn-north-1"
    service = "cv"
    credential_scope = f"{date_stamp}/{region}/{service}/request"
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    
    # Signing Key
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(key.encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region_name.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service_name.encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        return k_signing
    
    signing_key = get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Authorization Header
    authorization_header = f"{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    return authorization_header, amz_date, payload_hash

def test_volcengine():
    load_env()
    
    access_key = os.getenv("VOLCENGINE_ACCESS_KEY")
    secret_key = os.getenv("VOLCENGINE_SECRET_KEY")
    
    if not access_key or not secret_key:
        logger.error("Missing VOLCENGINE_ACCESS_KEY or VOLCENGINE_SECRET_KEY")
        return

    logger.info(f"Testing with Access Key: {access_key[:10]}...")
    logger.info(f"Testing with Secret Key: {secret_key[:5]}...{secret_key[-2:]}")

    url = "https://visual.volcengineapi.com"
    params = {
        "Action": "CVSync2AsyncSubmitTask",
        "Version": "2022-08-31"
    }
    
    body = {
        "req_key": "jimeng_t2i_v40",
        "prompt": "智谱AI(GLM)产品线收集整理分析",
        "force_single": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Host": "visual.volcengineapi.com"
    }
    
    payload = json.dumps(body, ensure_ascii=False)
    
    try:
        auth, date, hash = sign_request(access_key, secret_key, 'POST', url, params, headers, payload)
        
        headers['Authorization'] = auth
        headers['X-Date'] = date
        headers['X-Content-Sha256'] = hash
        
        submit_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        logger.info(f"Sending request to {submit_url}")
        response = requests.post(submit_url, headers=headers, data=payload)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 403:
            logger.error("❌ Permission Denied (403). Please check your IAM policies.")
            logger.error("Required Action: cv:CVSync2AsyncSubmitTask")
        elif response.status_code == 200:
            logger.info("✅ Success! API call worked.")
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Exception: {e}")

if __name__ == "__main__":
    test_volcengine()
