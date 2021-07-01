"""
Helpers for dealing with HTML input.
"""
def save_token(token):
    """
    Takes in token which and splits to extract the token code only
    """
    token = token['token']
    convert_token = str(token).split("'")[1]
    return convert_token