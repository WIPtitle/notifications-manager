from abc import ABC, abstractmethod


class FirebaseService(ABC):
    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    def set_credentials(self, credentials_dict: dict) -> None:
        pass

    @abstractmethod
    def delete_credentials(self) -> None:
        pass

    @abstractmethod
    def register_device_token(self, token: str) -> None:
        pass

    @abstractmethod
    def send_notification(self, title: str, body: str) -> None:
        pass
