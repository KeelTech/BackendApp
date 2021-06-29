

def save_token(token):
    token = token['token']
    convert_token = str(token).split("'")[1]
    return convert_token