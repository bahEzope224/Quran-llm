import json
import requests
import time
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.exceptions import AuthException

# Configuration Clerk
CLERK_INSTANCE_URL = "https://dashing-cougar-0.clerk.accounts.dev"
JWKS_URL = f"{CLERK_INSTANCE_URL}/.well-known/jwks.json"
ADMIN_EMAIL = "contact@ibrahima-bah.com"
ADMIN_USER_IDS = ["user_3Bq0yMWF3aREEtrg18HaJEjealk"] # Vos cles de secours

security = HTTPBearer()

# Cache global pour les cles publiques de Clerk
_JWKS_CACHE = None

def get_jwks():
    """Recupere les cles publiques de Clerk avec mise en cache brute."""
    global _JWKS_CACHE
    if _JWKS_CACHE:
        return _JWKS_CACHE
    
    try:
        response = requests.get(JWKS_URL, timeout=5)
        response.raise_for_status()
        _JWKS_CACHE = response.json()
        return _JWKS_CACHE
    except Exception as e:
        print(f"CRITICAL ERROR (Auth): Impossible de recuperer les cles JWKS : {e}")
        return {"keys": []}

async def get_current_admin(auth: HTTPAuthorizationCredentials = Depends(security)):
    """Verifie le token JWT Clerk et l'identite de l'admin."""
    token = auth.credentials
    jwks = get_jwks()

    try:
        # Recuperation de l'en-tete du token pour trouver la bonne cle
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            # Validation de la signature et des claims
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=None, # Clerk ne met pas toujours l'audience par defaut
                issuer=CLERK_INSTANCE_URL
            )
            
            # Verification de l'identite administrateur
            # Clerk stocke l'email dans la claim 'email' si configuree dans le template JWT
            email = payload.get("email")
            user_id = payload.get("sub") # Toujours present dans Clerk
            
            if not email:
                # Fallback : Si l'email est manquant (config Clerk), on verifie l'ID utilisateur
                if user_id in ADMIN_USER_IDS:
                    print(f"DEBUG (Auth): Acces Admin autorise via fallback ID: {user_id}")
                    return payload
                
                raise AuthException(
                    message="Acces refuse : Email non trouve dans le token. Verifiez votre configuration Clerk.",
                    location="auth_service.get_current_admin"
                )
            
            if email != ADMIN_EMAIL and user_id not in ADMIN_USER_IDS:
                print(f"DEBUG (Auth): Tentative acces refuse pour {email} / {user_id}")
                raise AuthException(
                    message=f"Acces refuse : Votre compte n'est pas autorise.",
                    location="auth_service.get_current_admin"
                )
            
            return payload

    except AuthException as e:
        # On laisse passer nos propres exceptions de diagnostic
        raise e
    except JWTError as e:
        raise AuthException(
            message=f"Session invalide ou expiree : {str(e)}",
            location="auth_service.get_current_admin"
        )
    except Exception as e:
        # On ne renvoie plus d'HTTPException brut pour preserver les headers CORS
        raise AuthException(
            message=f"Erreur interne de securite critique : {str(e)}",
            location="auth_service.get_current_admin"
        )

    raise AuthException(
        message="Impossible de valider la signature du token.",
        location="auth_service.get_current_admin"
    )

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    """Verifie le token JWT Clerk pour n'importe quel utilisateur authentifie."""
    token = auth.credentials
    jwks = get_jwks()

    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=None,
                issuer=CLERK_INSTANCE_URL
            )
            return payload
            
    except JWTError as e:
        raise AuthException(
            message=f"Session invalide ou expiree : {str(e)}",
            location="auth_service.get_current_user"
        )
    except Exception as e:
        raise AuthException(
            message=f"Erreur de securite : {str(e)}",
            location="auth_service.get_current_user"
        )

    raise AuthException(
        message="Impossible de valider la signature du token.",
        location="auth_service.get_current_user"
    )
