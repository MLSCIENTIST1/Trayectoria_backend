from werkzeug.security import check_password_hash

stored_hash = "pbkdf2:sha256:1000000$fBBytLHw3bXgwzZR$74a8dc902733cc4bb85b133c6fd92c9a142ccc85c926e9ba74ec8420f2358873"
password_attempt = "123456"

print("Verificación manual:", check_password_hash(stored_hash, password_attempt))