from datetime import datetime
from itertools import groupby
from enum import Enum


class Usuario:
    def __init__(self, email: str, valor_hora: float, acrescimos: dict):
        self.email = email
        self.valor_hora = valor_hora
        self.acrescimos = acrescimos
        self.total_acrescimos = 0

        if acrescimos is not None:
            self.total_acrescimos = sum(self.acrescimos.values())


def calcular_total_dias(atividades):
    datas = list(map(lambda x: x.data_inicial, atividades))

    group_by_date = lambda date: datetime(date.year, date.month, date.day)

    group = groupby(sorted(datas, key=group_by_date), key=group_by_date)

    return len(list(group))


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

        self.total_horas += atividade.total_horas
        self.valor_total = self.total_horas * self._usuario.valor_hora

        return atividade

    def __len__(self):
        return len(self._atividades)

    def __getitem__(self, item):
        return self._atividades[item]

    def fechar(self):
        self.status = StatusFolha.FECHADA

        if self._usuario.acrescimos is not None:
            total_dias_trabalhados = calcular_total_dias(self._atividades)
            self.valor_total += self._usuario.total_acrescimos * total_dias_trabalhados


class Atividade:
    def __init__(self):
        self.data_final = None
        self.data_inicial = datetime.now()
        self.total_horas = 0

    def finalizar(self):
        self.data_final = datetime.now()
        self.total_horas = (self.data_final - self.data_inicial).total_seconds() / 3600


class StatusFolha(Enum):
    NOVA = 0
    ATIVIDADE_ATIVA = 1
    ATIVIDADE_FINALIZADA = 2
    FECHADA = 3


class FolhaDePontoError(Exception):
    def __init__(self, message=None):
        self.message = message
