from abc import ABC, abstractmethod

from typing import Optional

class ITokenGenerator(ABC):
    @abstractmethod
    def get_token(self, access_token_url: str, installation_id: Optional[int] = None) -> str:
        pass
