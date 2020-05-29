# -*- coding: utf-8 -*-

import bcrypt


class PasswordCipher:
    @staticmethod
    def __encoder(password: str) -> str:
        return str(password).encode('utf-8')

    def hashpw(self, password: str) -> bytes:
        return bcrypt.hashpw(self.__encoder(password), bcrypt.gensalt())

    def checkpw(self, password, hashed) -> bool:
        return bcrypt.checkpw(self.__encoder(password), hashed)
