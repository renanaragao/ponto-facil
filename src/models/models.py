from datetime import datetime
from enum import Enum


class Usuario:
    def __init__(self, email: str, valor_hora: float):
        self.email = email
        self.valor_hora = valor_hora


class FolhaDePonto:
    def __init__(self, usuario: Usuario):
        self.valor_total = 0
        self.total_horas = 0
        self.data = datetime.now()
        self._usuario = usuario
        self._atividades = []
        self.status = StatusFolha.NOVA

    def iniciar_atividade(self):
        if self.status is StatusFolha.ATIVIDADE_ATIVA:
            raise FolhaDePontoError("Existe uma atividade que não foi finalizada.")

        atividade = Atividade()
        self._atividades.append(atividade)
        self.status = StatusFolha.ATIVIDADE_ATIVA
        return atividade

    def finalizar_atividade(self):
        if self.status is not StatusFolha.ATIVIDADE_ATIVA:
            raise FolhaDePontoError("Nenhuma atividade foi iniciada.")

        atividade = self._atividades[-1]
        atividade.finalizar()
        self.status = StatusFolha.ATIVIDADE_FINALIZADA

        self.total_horas += (atividade.data_final - atividade.data_inicial).total_seconds() / 3600
        self.valor_total = self.total_horas * self._usuario.valor_hora

        return atividade

    def __len__(self):
        return len(self._atividades)

    def __getitem__(self, item):
        return self._atividades[item]


class Atividade:
    def __init__(self):
        self.data_final = None
        self.data_inicial = datetime.now()

    def finalizar(self):
        self.data_final = datetime.now()


class StatusFolha(Enum):
    NOVA = 0
    ATIVIDADE_ATIVA = 1
    ATIVIDADE_FINALIZADA = 2


class FolhaDePontoError(Exception):
    def __init__(self, message=None):
        self.message = message
