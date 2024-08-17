def generate_unique_token(length: int = 250) -> str:
    random_uuid = uuid.uuid4()
    uuid_bytes = random_uuid.bytes
    hashed_token = hashlib.sha256(uuid_bytes).hexdigest()
    while len(hashed_token) < length:
        hashed_token += hashlib.sha256(hashed_token.encode()).hexdigest()

    hashed_token = hashed_token[:length]

    return hashed_token