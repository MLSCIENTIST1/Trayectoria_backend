import bcrypt

class PasswordController:
    @staticmethod
    def hash_password(password):
        """
        Hashea la contraseña proporcionada utilizando bcrypt.
        """
        salt = bcrypt.gensalt()  # Genera un salt aleatorio y seguro
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hashea la contraseña
        return hashed_password.decode('utf-8')  # Devuelve el hash como string legible

    @staticmethod
    def verify_password(password, hashed_password):
        """
        Verifica que la contraseña proporcionada coincida con el hash almacenado.
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))