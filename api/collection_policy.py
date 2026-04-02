from api.authorization import Principal

OFFICIAL_COLLECTION = "documents_official"


def user_collection(uid: str) -> str:
    return f"documents_user_{uid}"


def resolve_ingest_collection(principal: Principal, target: str) -> str:
    """
    target: "official" | "user"
    """
    if target == "official":
        if principal.role != "admin" or "ingest:official" not in principal.permissions:
            raise PermissionError("Not allowed to ingest into official collection")
        return OFFICIAL_COLLECTION

    # target == "user"
    if "ingest:user" not in principal.permissions:
        raise PermissionError("Not allowed to ingest into user collection")
    return user_collection(principal.sub)


def resolve_search_collections(principal: Principal) -> list[str]:
    if principal.role == "admin" and "search:multi" in principal.permissions:
        return [OFFICIAL_COLLECTION, user_collection(principal.sub)]
    if principal.doc_scope == "official":
        return [OFFICIAL_COLLECTION]
    return [user_collection(principal.sub)]