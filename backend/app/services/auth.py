import json
import requests
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.exceptions import AuthException

# Configuration Clerk
CLERK_INSTANCE_URL = "https://dashing-cougar-0.clerk.accounts.dev"
JWKS_URL = f"{CLERK_INSTANCE_URL}/.well-known/jwks.json"
ADMIN_EMAIL = "contact@ibrahima-bah.com"

security = HTTPBearer()

def get_jwks():
    """Recupere les cles publiques de Clerk."""
    response = requests.get(JWKS_URL)
    return response.json()

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
            
            if not email:
                # Fallback : Si l'email n'est pas dans le token, on peut verifier d'autres claims
                # ou demander a l'utilisateur de l'ajouter a son template JWT Clerk
                raise AuthException(
                    message="Acces refuse : Email non trouve dans le token. Verifiez votre configuration Clerk.",
                    location="auth_service.get_current_admin"
                )
            
            if email != ADMIN_EMAIL:
                raise AuthException(
                    message=f"Acces refuse : {email} n'est pas autorise.",
                    location="auth_service.get_current_admin"
                )
            
            return payload

    except JWTError as e:
        raise AuthException(
            message=f"Token invalide ou expire : {str(e)}",
            location="auth_service.get_current_admin"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'authentification serveur : {str(e)}"
        )

    raise AuthException(
        message="Impossible de valider la signature du token.",
        location="auth_service.get_current_admin"
    )
