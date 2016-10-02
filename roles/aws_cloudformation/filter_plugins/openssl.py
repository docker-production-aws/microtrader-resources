from subprocess import Popen, PIPE, STDOUT
import random, base64

class FilterModule(object):
  ''' OpenSSL Encryption/Decryption filters '''
  def filters(self):
    return {
        'encrypt': encrypt,
        'decrypt': decrypt,
    }

def encrypt(data, key, salt=None, cipher='aes-256-cbc'):
  ''' Encrypts data using OpenSSL '''
  salt = salt or ''.join([random.choice('0123456789abcdef') for x in range(16)])
  process=Popen(
    ["openssl", cipher, "-a", "-S", salt, "-k", key],
    stdout=PIPE,
    stdin=PIPE,
    stderr=PIPE
  )
  return base64.b64encode(process.communicate(input=data)[0])

def decrypt(data, key, cipher='aes-256-cbc'):
  ''' Decrypts data using OpenSSL '''
  process=Popen(
    ["openssl", cipher, "-a", "-d", "-k", key],
    stdout=PIPE,
    stdin=PIPE,
    stderr=PIPE
  )
  result = process.communicate(input=base64.b64decode(data))
  if result[1]:
    raise ValueError('Decryption error - ' + result[1])
  return result[0]