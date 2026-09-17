import os, json, hmac, hashlib, secrets, string
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL','https://gfxtool-bb32f-default-rtdb.firebaseio.com/').rstrip('/')
ADMIN_SECRET = os.environ.get('ADMIN_SECRET','SlFVoNDazRPb3A0n1DvWmXuEdcfoIfiMOjL7diW-hVLR-u4DC9MgqkpVK8JSN2NyUrvYVBC-wviN5D6KBoIzlwRvsw4VC9hYR9yi2V6yPzUV4sHhClDRqPVufwqivGXGEUxX9gY74ZxS9m1jSrNq9jP_PWzJwecJox0BeGBS9DA3yuwuVzTG5XLqI2r6pXEaY4CgNNbhz0jkpoKVzWiwnEhAbgFhTVHpaafmXJo1Ipx0PIVklKZdmjVf1t1Pgt-IaYC1ZVq394JxmT6uKTjGdd1Cm7RqOvJyEYNtlx5MfoRglVBJTbIRpSVGUN7cL-bfhGKNR3tarOSZI4eM9EL9rQ').strip()

# Firebase service-account credential embedded directly in this file.
FIREBASE_SERVICE_ACCOUNT_JSON = {'type': 'service_account','project_id': 'gfxtool-bb32f','private_key_id': '063b8bf0f6652c70c745ef33bc98bc569864fc90','private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCnmb4s9Q+c3yrb\n7vX/4YQFlNthVCnio+h3ocJJ4NrM5I9wASoVdHsjrPexKmiaFkUC0afN7g74pocZ\nDk4k+JFHBPpZzzUlu8plaU+XhS9e8wSECgIFrX4NKeUMm8eXS+7nSKqKUthAzLr0\np3N56US9ZeQGJPW6mQgDsH1S+SvnjOCMQAudt/81AYHl007qoJ6CHpvw0xneEXel\n8JhG7wmOFePNcN2Ax3jQRWQ48ydt7ahGBv6Yi4t3UYf3gjIQxvGsaFnBD19rDQu7\n7C3D4aSO9AmAXUMVUu6LwHo7PF/szIWuZXfMDcd/uvs9ZkNRQ0C+U12jjLUqF2pH\nK/bZcs33AgMBAAECggEAASiKm4NfesX/DALKXNHGSUxI9A1BpYyqjNOOg5nxSpXv\nCZkjl6uWKnchk6W4K+GB9PITDeAuCAyHpGuPaal7A2TR2UWUDIur/BefXwfEL/aC\nBeq7cV4U0hRiOKBZQ9fpYSSKeTThM6nM1uexuWhUHIOyovn5YB0LWZIicSyg6uFg\nTEgusNlFjVUbcGcjCCW6PGyGIT2bbEai0xAylUycs+9avTaNQnQGg9vo740lckJL\nBv5l7pSZV9QQBfyR1ZgeqBTYzVTe3VA/nJBGzCkTkY/6CUn1bjdYX0CdRENw1/26\nikg2X3wjI4avkmkUSELfkwjkdsQaRTeVZXZY6g5YEQKBgQDZtdV2d4hPTx4jIZl0\n7vZjuXQXOAhw5YRnk1z5wgLSsNA1d6vcP6sga8sRVPx/WN/WwrQsaj3BNEI+wfIq\nAN6ZiQlXJ3oPYB2JxxgQLNO6KNDmyqW1TsEZJYe1CNRvT+wPasHZaQ+yGoQJeziR\nt1A77k6LvhsvEh6tZHZCIEBAQwKBgQDFE8YImXRDuxpSQ/llng44lcOQjTNbx6q2\n8duSXqaS2cyySjpX64KDNuzgJRWYWQW4Nn1M4p1AtRHTuSJwgJ/owjIh2qP+ptXr\npvJbdpdVLPFhls6ji/FV0sSKzqIw0sLSW3FRAX5xlh2N6enTPurOXKffs+EWq+8B\nGTW22r2qPQKBgADkwyyKTw/sRjZks+mL9YzxPO2/eCFmf8WhEDeiOTq+KQyfIiB0\nTnKCnsHCdIrdRYXvJKguA3TgjwkM6L6NZFyC+HvYGKMphNWE8K9YT8Iq2rinykhV\nO2usAMOYdq7CSDjD+mm3Ca50d2hGjjPi6bxlPQNL03a8/0085VNeKIVbAoGBALNE\nH1lnLQkHQxQd3NiAg3MZWAE/T75my3UKX66vBlqCX962AohDJD7zUVk6ooAoSjmc\n5zFu2ZgonQS4XQl1FwCE1VFSLubPH7vx6nckUtgZv6ADrAe8nlRxGnMhLwu2S51J\nrLQA5eGwqUWTxyxvCOuaAOJOH6udzhRzuBaStwAJAoGAEk+LfuslmpKBSC+9m6Gr\nWl6/uPjxMwphU/yBtd3zDlG4Uwx0DTLmLvRuSaoXbbAPLiABhB7eanhHyOdzKvZM\ncXxBZmA5SJ3BWx8HTq83fnwicJyc08qqRrJgYlgyCqsDxVdSQBuc3Olj8j/KX4l8\nOrTkNV11ZYtR/oCWf2fw25Q=\n-----END PRIVATE KEY-----\n','client_email': 'firebase-adminsdk-70hn7@gfxtool-bb32f.iam.gserviceaccount.com','client_id': '113521204726986896638','auth_uri': 'https://accounts.google.com/o/oauth2/auth','token_uri': 'https://oauth2.googleapis.com/token','auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs','client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-70hn7%40gfxtool-bb32f.iam.gserviceaccount.com','universe_domain': 'googleapis.com'}

if not firebase_admin._apps:
    firebase_admin.initialize_app(
        credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_JSON),
        {'databaseURL': DATABASE_URL}
    )

def now_ms(): return int(datetime.now(timezone.utc).timestamp()*1000)
def clean(k): return str(k or '').strip().upper()
def kid(k): return hashlib.sha256(clean(k).encode()).hexdigest()
def auth(): return bool(ADMIN_SECRET) and hmac.compare_digest(request.headers.get('x-admin-secret',''), ADMIN_SECRET)
def get(k): return db.reference(f'licenses/{kid(k)}').get()
def newkey(): return 'ENC-' + ''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(16))

def check(k, app_id, device_id):
    k=clean(k); app_id=str(app_id or '').strip(); device_id=str(device_id or '').strip()
    if not k or not app_id or not device_id: return False,'missing_fields',None
    lic=get(k)
    if not lic: return False,'invalid_license',None
    if lic.get('revoked') is True: return False,'revoked',lic
    if int(lic.get('expires_at',0) or 0) and now_ms() >= int(lic['expires_at']): return False,'expired',lic
    if str(lic.get('app_id','') or '') and lic.get('app_id') != app_id: return False,'app_mismatch',lic
    devices=lic.get('devices') or {}; limit=int(lic.get('max_devices', 1))
    if device_id not in devices:
        if limit != 0 and len(devices) >= limit: return False,'device_limit',lic
        devices[device_id]={'bound_at':now_ms()}
        db.reference(f'licenses/{kid(k)}').update({'devices':devices})
    return True,'ok',lic

@app.get('/')
def home(): return jsonify(ok=True,service='license-api',database='firebase-realtime-database')

@app.post('/verify')
def verify():
    d=request.get_json(silent=True) or {}; ok,reason,lic=check(d.get('license_key'),d.get('app_id'),d.get('device_id'))
    if not ok: return jsonify(ok=False,reason=reason),403
    return jsonify(ok=True,license_key=clean(d.get('license_key')),app_id=d.get('app_id'),expires_at=lic.get('expires_at'),max_devices=lic.get('max_devices'))

@app.post('/admin/create-key')
def create_key():
    if not auth(): return jsonify(ok=False,error='unauthorized'),401
    d=request.get_json(silent=True) or {}
    try:
        days = int(d.get('days', 30))
        limit = int(d.get('max_devices', 1))
    except (TypeError, ValueError):
        return jsonify(ok=False, error='days and max_devices must be integers'), 400
    app_id = str(d.get('app_id', '') or '').strip()
    if days < 1 or limit < 0:
        return jsonify(ok=False, error='invalid parameters'), 400
    k=newkey(); created=now_ms(); rec={'app_id':app_id,'created_at':created,'expires_at':created+days*86400000,'max_devices':limit,'revoked':False,'devices':{}}
    db.reference(f'licenses/{kid(k)}').set(rec)
    return jsonify(ok=True,license_key=k,**rec),201

@app.get('/admin/status/<key>')
def status(key):
    if not auth(): return jsonify(ok=False,error='unauthorized'),401
    lic=get(key)
    if not lic: return jsonify(ok=False,error='not_found'),404
    return jsonify(ok=True,license_key=clean(key),**lic)

@app.post('/admin/revoke/<key>')
def revoke(key):
    if not auth(): return jsonify(ok=False,error='unauthorized'),401
    if not get(key): return jsonify(ok=False,error='not_found'),404
    db.reference(f'licenses/{kid(key)}').update({'revoked':True,'revoked_at':now_ms()})
    return jsonify(ok=True,license_key=clean(key),revoked=True)

@app.post('/admin/unrevoke/<key>')
def unrevoke(key):
    if not auth(): return jsonify(ok=False,error='unauthorized'),401
    if not get(key): return jsonify(ok=False,error='not_found'),404
    db.reference(f'licenses/{kid(key)}').update({'revoked':False,'unrevoked_at':now_ms()})
    return jsonify(ok=True,license_key=clean(key),revoked=False)

@app.post('/admin/reset-devices/<key>')
def reset_devices(key):
    if not auth(): return jsonify(ok=False,error='unauthorized'),401
    if not get(key): return jsonify(ok=False,error='not_found'),404
    db.reference(f'licenses/{kid(key)}').update({'devices':{},'devices_reset_at':now_ms()})
    return jsonify(ok=True,license_key=clean(key),devices={})

@app.get('/admin/list')
def list_keys():
    if not auth(): return jsonify(ok=False,error='unauthorized'),401
    data=db.reference('licenses').get() or {}
    return jsonify(ok=True,count=len(data),licenses=[dict(v or {},id=k) for k,v in data.items()])

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(ok=False, error='method_not_allowed', allowed=list(e.valid_methods or [])), 405

@app.errorhandler(404)
def not_found(e):
    return jsonify(ok=False, error='not_found'), 404


application=app
