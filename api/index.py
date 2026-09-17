import os, json, hmac, hashlib, secrets, string
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL','https://gfxtool-bb32f-default-rtdb.firebaseio.com/').rstrip('/')
ADMIN_SECRET = os.environ.get('ADMIN_SECRET','SlFVoNDazRPb3A0n1DvWmXuEdcfoIfiMOjL7diW-hVLR-u4DC9MgqkpVK8JSN2NyUrvYVBC-wviN5D6KBoIzlwRvsw4VC9hYR9yi2V6yPzUV4sHhClDRqPVufwqivGXGEUxX9gY74ZxS9m1jSrNq9jP_PWzJwecJox0BeGBS9DA3yuwuVzTG5XLqI2r6pXEaY4CgNNbhz0jkpoKVzWiwnEhAbgFhTVHpaafmXJo1Ipx0PIVklKZdmjVf1t1Pgt-IaYC1ZVq394JxmT6uKTjGdd1Cm7RqOvJyEYNtlx5MfoRglVBJTbIRpSVGUN7cL-bfhGKNR3tarOSZI4eM9EL9rQ').strip()

# Firebase service-account credential embedded directly in this file.
FIREBASE_SERVICE_ACCOUNT_JSON = {'type': 'service_account', 'project_id': 'gfxtool-bb32f', 'private_key_id': '8b07653a4d5470369e7c98e24c4bf5ff93553a4e', 'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDATKIkEeGiELno\nEJxiEV7/tGx6inlfbKW9IYvDevCbW6NoOeYy/GIpA12Pot0XLvUA4oijWH6sQqyH\nrzyXm4OTpuI/Xu/TFktx/BDKDGfgtk3oK0Mv1pND8LDPj2Zu4b5vnBn7QyzJIZvN\nXHtgcUU1S2gIQWWrc4VHBdsskmxKAX4ZqI9asFAyyjJrzTNO8U7LSk/vliudMNG1\n6lEDELIvViL5r9ZdeKfLs3JZOh1+JDKrax0hAXEIv37n9ZMfprD7P5QEjYM9BnC3\ng42CuSCJx+Vfx4bEyW/e//KGIxfabEwY81ticjuD7uWbHQurrM/Vgb/6vyI37HKg\n4Zaxgo7TAgMBAAECggEALrhPqmjHw3rB2B51CCSFSqXYtzr+ew8oA1frn342h+BP\nRqrOgXOtG57MM/ITOic38lOXc+wztoFqbnrGQ2VOpehlTpUvuj7P7K0bnSM/d6qD\nKhWcuLouxFJtergx4F2rSW2JKHEtJ96o/k9qUEek02pzJ5JP88RYzKUhF2aptZ7U\nTeQ0lGPsvlsCjc9MmZ2rvIW6OQlE2MJa1cwbgAmNH2y8me/DOSisXhuBL+xp+iJo\nGxHHI3e1M4RZDCHHUwlDTxbxXFSAgbnplcRRuJyCKIzJRvMj3OAPRgOT8nUcMhVp\n3S6YDNWv4hiWMv865FABwnIgTqHutoLp+zwzVq+FCQKBgQDne3nL0HZnS/oUvYby\nMUVp3bAtKFuN2jsaBuz7VV8jST4gYqP1yUaKdRlfqeVwOzx3FZCW5qtx5dtfZwxM\nE6uEO2n3JP5m8Mu7pIdmPKWjsZH9oAehuI1PcoyXXLTE7GFDGKJcGlZ7S8SpWttw\npUKf4URdyCRWRUcNaPbx86wdewKBgQDUqrs2bEHJKMzvGRcVVER/8qrN/s9xaQh0\na1fEmPG7ADTelsBK5zUe6M7eNTWqB2chR0AwfybWZj2UT0YKH2bd7g/zwPT9mfeX\n37TEkJG8IEvvSzXegPxRt5vpxaSHLgoSQrPfVgk70lH1g9lLSUCNcIw3psWCkb4f\njwHsUGXYiQKBgETCVbRn8LPQSrGcdpg8cHz439saEM/7EfEyO3SQsFjf6bde9YsN\nxYldLTNQWRnUTqqk2jUowaZse5REHNAAS8NUjq5d67+SKUJMpfeFbkJIfbATuBCe\nrEL8KKzRWdTgzidLCvdGz4eCQyF3HpXAUSECnfcpezmxDGD8W9YU5nw/AoGBAMHe\nYoxaZB5dc3UECmcHSurY7Zycjb91YJ/Au2Idi0BOD+RayTF/VI247dzj5Of7l6he\nq8WKJH2O9tQc8FyKA9yNCT3MyYnmsi9hYAlRQYmeZ5rdlV4hd+OG3jteUX5qGgRL\nim4uoHxIXy7R42UeghpuX2TcQ3GkKw3Z8IbdQ/sBAoGBAL5bZ0BZPCb4mSgxdZef\nHvTN7Q6kaZyfr7EtrUhakf/VM/xofVUNz8pZSiVbKg52xqPntJimVut2xuRIdlK0\nclIlUHS7AKxjy20Gp8Lc/8vKAGPc3Eq1pzZjvEgTzxYclYQXsSkpZ6Hy+BNalsAt\nTf6pG3KNZCqS1UqfQuad83mb\n-----END PRIVATE KEY-----\n', 'client_email': 'firebase-adminsdk-fbsvc@gfxtool-bb32f.iam.gserviceaccount.com', 'client_id': '103349116553867583112', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token', 'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs', 'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40gfxtool-bb32f.iam.gserviceaccount.com', 'universe_domain': 'googleapis.com'}

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
