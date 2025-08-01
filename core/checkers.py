def contains_number(password):
    for char in password:
        if char.isdigit():
            return True
    return False

def contains_symbol(password):
    for char in password:
        if char.isalnum():
            return True
    return False