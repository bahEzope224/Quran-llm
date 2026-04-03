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
                # Log interne pour Railway
                keys_found = list(payload.keys())
                print(f"DEBUG (Auth): ID Utilisateur: {user_id} | Champs presents: {keys_found}")
                
                # Le message est renvoye au frontend : l'utilisateur pourra copier son ID (sub)
                raise AuthException(
                    message=f"Acces refuse : Email non trouve. Votre ID unique est : {user_id}. Champs presents: {keys_found}. Transmettez cet ID a l'assistant pour debloquer l'acces.",
                    location="auth_service.get_current_admin"
                )
            
            if email != ADMIN_EMAIL:
                print(f"DEBUG (Auth): Tentative acces par {email} au lieu de {ADMIN_EMAIL}")
                raise AuthException(
                    message=f"Acces refuse : {email} n'est pas autorise.",
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
