from abc import ABC, abstractmethod


class ObservadorRede(ABC):
    @abstractmethod
    def atualizar(self, pacote):
        pass