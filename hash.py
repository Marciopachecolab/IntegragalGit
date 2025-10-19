import hashlib

def gerar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

print(gerar_hash("admin"))
print(gerar_hash("1234"))
