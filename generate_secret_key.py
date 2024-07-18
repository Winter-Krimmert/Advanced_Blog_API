import secrets
import string

def generate_secret_key(length=32):
    alphabet = string.ascii_lowercase + string.digits + '_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def save_secret_key(filename='secret_key.txt'):
    secret_key = generate_secret_key()
    with open(filename, 'w') as f:
        f.write(secret_key)

if __name__ == '__main__':
    save_secret_key()
    print(f'Secret key saved to secret_key.txt')
