

from abc import ABC, abstractmethod


class JWTVerifierInterface(ABC):
    
    
    @abstractmethod
    def verify_access_token(
        self,
        token: str,
        claims_to_verify=("iss", "aud", "exp"),
    ):
        ...