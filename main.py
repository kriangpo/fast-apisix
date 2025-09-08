from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import requests
from typing import Dict

app = FastAPI()

# URL ของ OpenID Connect discovery endpoint ของ Casdoor
CASDOOR_DISCOVERY_URL = "https://172.26.8.178/.well-known/openid-configuration"

# สร้างตัวแปรสำหรับ OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ตัวแปรสำหรับเก็บ Public Key ของ Casdoor
# เราจะดึงค่านี้มาเมื่อแอปพลิเคชันเริ่มทำงาน
_jwks = None

def get_jwks():
    """
    ดึง JSON Web Key Set (JWKS) จาก Casdoor เพื่อใช้ตรวจสอบลายเซ็นของ Token
    """
    global _jwks
    if _jwks is None:
        # ดึงข้อมูลจาก discovery endpoint
        try:
            res = requests.get(CASDOOR_DISCOVERY_URL, timeout=10)
            res.raise_for_status()
            discovery_data = res.json()
            jwks_uri = discovery_data.get("jwks_uri")

            if not jwks_uri:
                raise RuntimeError("jwks_uri not found in discovery endpoint")

            # ดึง JWKS จาก URL ที่ได้
            jwks_res = requests.get(jwks_uri, timeout=10)
            jwks_res.raise_for_status()
            _jwks = jwks_res.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Casdoor discovery endpoint: {e}"
            )
    return _jwks

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    ฟังก์ชันสำหรับตรวจสอบ Token และดึงข้อมูลผู้ใช้
    """
    try:
        jwks = get_jwks()
        # ถอดรหัสและตรวจสอบ Token ด้วย Public Key จาก Casdoor
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"], # ต้องตรงกับ token_signing_alg ที่ตั้งค่าไว้ใน Casdoor
            options={"verify_aud": False} # ตั้งค่าตามความเหมาะสม
        )
        # ตัวอย่างข้อมูลที่ได้จาก payload: {'sub': 'user_id', 'name': 'John Doe', 'email': 'john@example.com', ...}
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )

@app.get("/api")
def get_protected_data(current_user: Dict = Depends(get_current_user)):
    """
    Endpoint ที่มีการป้องกันและสามารถเข้าถึงข้อมูลของผู้ใช้ได้
    """
    return {
        "message": f"Hello, {current_user.get('name', 'User')}!",
        "user_id": current_user.get('sub'),
        "token_payload": current_user
    }