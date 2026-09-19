import os
import json
import hmac
import hashlib
import secrets
import string
import traceback
from datetime import datetime, timezone

from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "FIREBASE_DATABASE_URL",
    "https://gfxtool-bb32f-default-rtdb.firebaseio.com/",
).strip().rstrip("/")
ADMIN_SECRET = os.environ.get('ADMIN_SECRET','SlFVoNDazRPb3A0n1DvWmXuEdcfoIfiMOjL7diW-hVLR-u4DC9MgqkpVK8JSN2NyUrvYVBC-wviN5D6KBoIzlwRvsw4VC9hYR9yi2V6yPzUV4sHhClDRqPVufwqivGXGEUxX9gY74ZxS9m1jSrNq9jP_PWzJwecJox0BeGBS9DA3yuwuVzTG5XLqI2r6pXEaY4CgNNbhz0jkpoKVzWiwnEhAbgFhTVHpaafmXJo1Ipx0PIVklKZdmjVf1t1Pgt-IaYC1ZVq394JxmT6uKTjGdd1Cm7RqOvJyEYNtlx5MfoRglVBJTbIRpSVGUN7cL-bfhGKNR3tarOSZI4eM9EL9rQ').strip()
SERVICE_ACCOUNT_FILENAME = "gfxtool-bb32f-firebase-adminsdk-70hn7-440af8a6f8.json"

_db_ready = False
_db_error = None


def _load_credentials():
    # Keep the Firebase service-account JSON embedded directly in index.py.
    FIREBASE_SERVICE_ACCOUNT_JSON = {'type': 'service_account', 'project_id': 'gfxtool-bb32f', 'private_key_id': '26f8b6707b066b6b30bd5ede7d7d26247443c53a', 'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQClwp/7KwAl3Dz1\nklNea+vRDGXfwaH4WhPrfzrRRvqsyvk8EKqtKrBD9+/CT5SKOkU1m7JADA/VFlJh\neFEm+vCytZmnYScrLadRTR8Orwn/6n900RRTJw987hqLqMP4/lpYUwRCbeEK7Z3S\niszzgkDhgsqPYRdlcLrs0c2oHCwnrQE3WkJLGKlIcfyEUI+vg4tHUK/CxacZXDCg\njb48eInRBhGFE+Qf+gpGipSvq6zrZ9Fw8oKGek+zg2MSt8qpAVKazZG0CQE1XXYL\nRHaI+1Xd7lcrjh7Sfk3sSdZbLblZDhy18wccqml7hj4vXUy0S6b222aaIoJoyppK\nGAM5AeHFAgMBAAECggEAI6nyytMPJpYypXF0r4GPzLwapSBfrXQQCiCnMoTPhWLs\nafB6EGT5ZL5RHyEJKA5ueqDDosUVmPbDBcahyz29kO3CoAEmsMMTV0o9Duc5Qw8c\nmjEr6tIiInKGUpsegxGStaMy7OoAO94xES4c952EQSDnXR76LjCpfy+KzIs3MtfN\nG918Vej9vPrxgRxYa4fo82oSoKLYQxts+pQ1hCPA/MF3WY/XUxx8PZC/ZY0P56oL\nQeD3QhhojccMZryZXKr+RNfoX8rV0P6200XOfrOjHwTRo1nMFuzwe0otCu0FZjD0\n32He/K7w+ZqRekp7gZh5K8uhntdX2NJyED8QJFowEQKBgQDSdBfpVAqtTZl5R/zv\n4HDrQY9xRe6Zth4D7X8iPINm6baK/c6jlcpQSz5mnMkb5YOY5mna1+DmFb80dG9/\n9fF+VYkMbGMqd0HP2cH27fQF33Oh2FatF/rTEOvMTJwigojNs+he04/K5trO3lkh\nwQMz0o5cZGUoBB9vbHGYpr1PDQKBgQDJolwiM4PkSaC0CU29ySFEimpzlp8G0Ph5\nen2VGoFB3g1f218yvhibuYn7SakbAkeM5sugsz54M2Rfdc4RZW6Z96++DFI/3YjP\ny/SJYdGMa+J/8fWYg3T1ENKwz/DH9Bk11qVVpCnioFVuaUgb4UOf6sweudtn6n7o\nHTNgcTNvmQKBgC9Fto1JvHA7KwssGWvEbXjarB7Uh4jteIaHVXRaRWXbf45u/niO\nT/iDPkwMUbw7bLjuoL5wmWr1XZKpyNXkZ89p5TPuMMQ8L4NBtakCwDqFe9LR5n5R\nEZ1RgrXMS5IQ4ivaioqqWPVJr8Kh/UFwuohsdl/YiURY0LrVkBqq8YENAoGAAO9v\n3fi/M9/jjvI8GhVEwjyiIcchFbcCcA3RZ0+oKdYN2dP6rRGUq6RAr5m33xgznMO1\nThmGwKf8XzT8r7f4u14awpbsCr/MUqpvh/OcNTqK4m0M5pg1gq2BTLCqPUM0mrtU\nKQGJ8DMuMkTqwLZayfMc30edbO35iLoZ8uiThIECgYA8sLBDcfaMavRFdbxjpLI5\nzv5uUsvhTMuEfiFoaQ7BymHLKNeJeKtTJp9ol97g1ru2XqqLfFJfIjNruxLV3/63\ntxIh3FG90MILJGhL+rYB0KkYxF+P1AvniLwXHRk0CzspPy7hjAzO829VL27PpjQ+\n+HeaoICpWaTQIn2vETsP3w==\n-----END PRIVATE KEY-----\n', 'client_email': 'firebase-adminsdk-fbsvc@gfxtool-bb32f.iam.gserviceaccount.com', 'client_id': '107506211168764398777', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token', 'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs', 'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40gfxtool-bb32f.iam.gserviceaccount.com', 'universe_domain': 'googleapis.com'}
    return credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_JSON)
def init_firebase():
    global _db_ready, _db_error
    if _db_ready:
        return True
    if _db_error:
        return False
    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(
                _load_credentials(),
                {"databaseURL": DATABASE_URL},
            )
        _db_ready = True
        return True
    except Exception as exc:
        _db_error = f"{type(exc).__name__}: {exc}"
        print("[FIREBASE INIT ERROR]", _db_error)
        traceback.print_exc()
        return False


def require_firebase():
    if init_firebase():
        return None
    return jsonify(
        ok=False,
        error="firebase_not_configured",
        message=(_db_error or "Firebase initialization failed")[:1000],
    ), 503


def firebase_error(operation, exc):
    msg = f"{type(exc).__name__}: {exc}"
    print(f"[FIREBASE ERROR] {operation}: {msg}")
    traceback.print_exc()
    return jsonify(
        ok=False,
        error="firebase_error",
        operation=operation,
        message=msg[:1000],
    ), 502


def now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def clean(k):
    return str(k or "").strip().upper()


def kid(k):
    return hashlib.sha256(clean(k).encode()).hexdigest()


def auth():
    supplied = request.headers.get("x-admin-secret", "")
    return bool(ADMIN_SECRET) and hmac.compare_digest(supplied, ADMIN_SECRET)


def get(k):
    return db.reference(f"licenses/{kid(k)}").get()


def newkey():
    return "ENC-" + "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )


def check(k, app_id, device_id):
    k = clean(k)
    app_id = str(app_id or "").strip()
    device_id = str(device_id or "").strip()
    if not k or not app_id or not device_id:
        return False, "missing_fields", None

    lic = get(k)
    if not lic:
        return False, "invalid_license", None
    if lic.get("revoked") is True:
        return False, "revoked", lic
    if int(lic.get("expires_at", 0) or 0) and now_ms() >= int(lic["expires_at"]):
        return False, "expired", lic
    if str(lic.get("app_id", "") or "") and lic.get("app_id") != app_id:
        return False, "app_mismatch", lic

    devices = lic.get("devices") or {}
    limit = int(lic.get("max_devices", 1) or 0)
    if device_id not in devices:
        if limit != 0 and len(devices) >= limit:
            return False, "device_limit", lic
        devices[device_id] = {"bound_at": now_ms()}
        db.reference(f"licenses/{kid(k)}").update({"devices": devices})
    return True, "ok", lic


@app.get("/")
def home():
    return jsonify(
        ok=True,
        service="license-api",
        database="firebase-realtime-database",
        firebase_configured=init_firebase(),
        firebase_error=_db_error if not _db_ready else None,
    )


@app.get("/health")
def health():
    ok = init_firebase()
    return jsonify(
        ok=ok,
        service="license-api",
        firebase_configured=ok,
        database_url=DATABASE_URL,
        error=_db_error if not ok else None,
    ), (200 if ok else 503)


@app.post("/verify")
def verify():
    problem = require_firebase()
    if problem:
        return problem
    try:
        d = request.get_json(silent=True) or {}
        ok, reason, lic = check(
            d.get("license_key"), d.get("app_id"), d.get("device_id")
        )
        if not ok:
            return jsonify(ok=False, reason=reason), 403
        return jsonify(
            ok=True,
            license_key=clean(d.get("license_key")),
            app_id=d.get("app_id"),
            expires_at=lic.get("expires_at"),
            max_devices=lic.get("max_devices"),
        )
    except Exception as exc:
        return firebase_error("verify", exc)


# ---------------- Runtime anti-tamper ----------------

def _runtime_device_record(device_id):
    return hashlib.sha256(str(device_id or "").encode()).hexdigest()


@app.post("/runtime/check")
def runtime_check():
    problem = require_firebase()
    if problem:
        return problem
    try:
        d = request.get_json(silent=True) or {}
        app_id = str(d.get("app_id", "") or "").strip()
        device_id = str(d.get("device_id", "") or "").strip()
        if not app_id or not device_id:
            return jsonify(ok=False, blocked=True, reason="missing_fields"), 400

        ref = db.reference(f"runtime_devices/{_runtime_device_record(device_id)}")
        rec = ref.get() or {}
        if rec.get("blocked") is True:
            # Legacy versions treated every generic `runtime_signal` as a
            # permanent block.  Migrate that false-positive state once.
            if rec.get("reason") == "runtime_signal":
                now = now_ms()
                ref.update({
                    "blocked": False,
                    "unblocked_at": now,
                    "unblock_reason": "legacy_runtime_signal_migration",
                })
                rec = ref.get() or {}
            else:
                return jsonify(
                    ok=False,
                    blocked=True,
                    reason=rec.get("reason", "runtime_blocked"),
                ), 403

        now = now_ms()
        update = {
            "device_id_hash": _runtime_device_record(device_id),
            "app_id": app_id,
            "last_seen_at": now,
            "blocked": False,
        }
        if not rec:
            update["first_seen_at"] = now
        ref.update(update)
        return jsonify(ok=True, blocked=False)
    except Exception as exc:
        return firebase_error("runtime_check", exc)


@app.post("/runtime/event")
def runtime_event():
    problem = require_firebase()
    if problem:
        return problem
    try:
        d = request.get_json(silent=True) or {}
        app_id = str(d.get("app_id", "") or "").strip()
        device_id = str(d.get("device_id", "") or "").strip()
        event = str(d.get("event", "") or "").strip()
        reason = str(d.get("reason", "") or "").strip()[:200]
        details = str(d.get("details", "") or "").strip()[:1000]
        if not app_id or not device_id or not event:
            return jsonify(ok=False, error="missing_fields"), 400

        device_hash = _runtime_device_record(device_id)
        now = now_ms()
        db.reference(f"runtime_events/{device_hash}/{now}_{secrets.token_hex(4)}").set({
            "app_id": app_id,
            "device_id_hash": device_hash,
            "event": event,
            "reason": reason,
            "details": details,
            "ts": now,
        })

        if event == "tamper" and reason:
            db.reference(f"runtime_devices/{device_hash}").update({
                "app_id": app_id,
                "blocked": True,
                "reason": reason,
                "blocked_at": now,
                "last_event_details": details,
            })
            return jsonify(ok=True, blocked=True)

        db.reference(f"runtime_devices/{device_hash}").update({
            "app_id": app_id,
            "last_seen_at": now,
        })
        return jsonify(ok=True, blocked=False)
    except Exception as exc:
        return firebase_error("runtime_event", exc)


# ---------------- Admin license endpoints ----------------

def admin_guard():
    if not auth():
        return jsonify(ok=False, error="unauthorized"), 401
    return None


@app.post("/admin/unblock-runtime")
def unblock_runtime():
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        d = request.get_json(silent=True) or {}
        device_id = str(d.get("device_id", "") or "").strip()
        if not device_id:
            return jsonify(ok=False, error="missing_device_id"), 400
        device_hash = _runtime_device_record(device_id)
        ref = db.reference(f"runtime_devices/{device_hash}")
        rec = ref.get() or {}
        if not rec:
            return jsonify(ok=False, error="not_found"), 404
        now = now_ms()
        ref.update({
            "blocked": False,
            "unblocked_at": now,
            "unblock_reason": "admin_manual_unblock",
        })
        return jsonify(ok=True, blocked=False, device_id_hash=device_hash)
    except Exception as exc:
        return firebase_error("admin_unblock_runtime", exc)


@app.post("/admin/create-key")
def create_key():
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        d = request.get_json(silent=True) or {}
        try:
            days = int(d.get("days", 30))
            limit = int(d.get("max_devices", 1))
        except (TypeError, ValueError):
            return jsonify(ok=False, error="days and max_devices must be integers"), 400

        app_id = str(d.get("app_id", "") or "").strip()
        if days < 1 or days > 36500:
            return jsonify(ok=False, error="days must be between 1 and 36500"), 400
        if limit < 0:
            return jsonify(ok=False, error="max_devices cannot be negative"), 400
        if len(app_id) > 100:
            return jsonify(ok=False, error="app_id is too long"), 400

        k = newkey()
        created = now_ms()
        rec = {
            "app_id": app_id,
            "created_at": created,
            "expires_at": created + days * 86400000,
            "max_devices": limit,
            "revoked": False,
            "devices": {},
        }
        db.reference(f"licenses/{kid(k)}").set(rec)
        return jsonify(ok=True, license_key=k, **rec), 201
    except Exception as exc:
        return firebase_error("admin_create_key", exc)


@app.get("/admin/status/<key>")
def status(key):
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        lic = get(key)
        if not lic:
            return jsonify(ok=False, error="not_found"), 404
        return jsonify(ok=True, license_key=clean(key), **lic)
    except Exception as exc:
        return firebase_error("admin_status", exc)


@app.post("/admin/revoke/<key>")
def revoke(key):
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        if not get(key):
            return jsonify(ok=False, error="not_found"), 404
        db.reference(f"licenses/{kid(key)}").update({
            "revoked": True,
            "revoked_at": now_ms(),
        })
        return jsonify(ok=True, license_key=clean(key), revoked=True)
    except Exception as exc:
        return firebase_error("admin_revoke", exc)


@app.post("/admin/unrevoke/<key>")
def unrevoke(key):
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        if not get(key):
            return jsonify(ok=False, error="not_found"), 404
        db.reference(f"licenses/{kid(key)}").update({
            "revoked": False,
            "unrevoked_at": now_ms(),
        })
        return jsonify(ok=True, license_key=clean(key), revoked=False)
    except Exception as exc:
        return firebase_error("admin_unrevoke", exc)


@app.post("/admin/reset-devices/<key>")
def reset_devices(key):
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        if not get(key):
            return jsonify(ok=False, error="not_found"), 404
        db.reference(f"licenses/{kid(key)}").update({
            "devices": {},
            "devices_reset_at": now_ms(),
        })
        return jsonify(ok=True, license_key=clean(key), devices={})
    except Exception as exc:
        return firebase_error("admin_reset_devices", exc)


@app.get("/admin/list")
def list_keys():
    denied = admin_guard()
    if denied:
        return denied
    problem = require_firebase()
    if problem:
        return problem
    try:
        data = db.reference("licenses").get() or {}
        if not isinstance(data, dict):
            data = {}
        licenses = [dict(v or {}, id=k) for k, v in data.items() if isinstance(v, dict)]
        return jsonify(ok=True, count=len(licenses), licenses=licenses)
    except Exception as exc:
        return firebase_error("admin_list", exc)


@app.errorhandler(404)
def not_found(e):
    return jsonify(ok=False, error="not_found"), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(
        ok=False,
        error="method_not_allowed",
        allowed=list(e.valid_methods or []),
    ), 405


@app.errorhandler(500)
def server_error(e):
    print("[UNHANDLED 500]")
    traceback.print_exc()
    return jsonify(
        ok=False,
        error="internal_server_error",
        message="Unhandled server exception. Check Vercel logs.",
    ), 500


application = app
