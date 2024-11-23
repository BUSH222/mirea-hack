import secrets
import string
import settings_loader
setting =settings_loader.get_processor_settings
def generate_secure_key():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secure_key = ''.join(secrets.choice(alphabet) for _ in range(setting['pass_gen_len']))
    return secure_key
