import jwt

def create_jwt(objects):
    username = objects.email
    token = jwt.encode({'username': username}, "secret", algorithm="HS256")
    return token


def decode(token):
    decode = jwt.decode(token, "secret", algorithms=["HS256"])
    return decode
