from dataclasses import dataclass
from typing import Callable, Iterable

from fastapi import Depends, HTTPException, status

from api.auth import require_auth


@dataclass
class Principal:
    sub: str
    role: str                  # "user" | "admin"
    permissions: set[str]      # ex: {"chat:query", "ingest:user"}
    doc_scope: str             # "official" | "user" | "both"


REQUIRED_CLAIMS = {"sub", "role"}


def _normalize_permissions(value) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, list):
        return {str(v) for v in value}
    if isinstance(value, str):
        # support "perm1 perm2"
        return {p.strip() for p in value.split() if p.strip()}
    return set()


def _claims_to_principal(claims: dict) -> Principal:
    missing = [k for k in REQUIRED_CLAIMS if k not in claims]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required claims: {', '.join(missing)}",
        )

    role = str(claims.get("role", "user"))
    doc_scope = str(claims.get("doc_scope", "user"))
    perms = _normalize_permissions(claims.get("permissions"))

    # RBAC baseline
    if role == "admin":
        perms |= {"chat:query", "ingest:official", "ingest:user", "search:multi"}
        if doc_scope == "user":
            doc_scope = "both"
    else:
        perms |= {"chat:query", "ingest:user"}
        if doc_scope not in {"user", "official", "both"}:
            doc_scope = "user"

    return Principal(
        sub=str(claims["sub"]),
        role=role,
        permissions=perms,
        doc_scope=doc_scope,
    )


def require_principal(claims: dict = Depends(require_auth)) -> Principal:
    return _claims_to_principal(claims)


def require_permission(permission: str) -> Callable[[Principal], Principal]:
    def _dep(principal: Principal = Depends(require_principal)) -> Principal:
        if permission not in principal.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return principal

    return _dep