from datetime import datetime
from itertools import groupby
from enum import IntEnum

from bson import ObjectId

from src.base.base_model import Serializable


def calcular_total_acrescimos(acrescimos):
    if acrescimos is not None:
        return sum(acrescimos.values())
    return 0

class Usuario(Serializable):
    def __init__(self, email: str, valor_hora: float, acrescimos: dict):
        super().__init__()
        self._id = email
        self.email = email
        self.valor_hora = valor_hora
        self.acrescimos = acrescimos
        self.total_acrescimos = 0

        self.total_acrescimos = calcular_total_acrescimos(self.acrescimos)

    def adicionar_acrescimo(self, descricao, valor):
        self.acrescimos = self.acrescimos or {}
        self.acrescimos[descricao] = valor
        self.total_acrescimos = calcular_total_acrescimos(self.acrescimos)


def retornar_datas(atividades):
    for atividade in atividades:
        yield atividade.data_inicial
        yield atividade.data_final


def calcular_total_dias(atividades):
    datas = list(retornar_datas(atividades))
    def group_by_date(date): return datetime(date.year, date.month, date.day)
    group = groupby(sorted(datas, key=group_by_date), key=group_by_date)
    return len(list(group))


class FolhaDePonto(Serializable):
    def __init__(self,
                 usuario: Usuario,
                 valor_total=0,
                 total_horas=0,
                 data=datetime.now(),
                 atividades=None,
                 status=None,
                 _id=None,
                 acrescimos=None,
                 decrescimos=None):
        super().__init__()
        self.decrescimos = decrescimos or {}
        self.acrescimos = acrescimos or {}
        self._id = _id or ObjectId()
        self.valor_total = valor_total
        self.total_horas = total_horas
        self.data = data
        self.usuario = usuario
        self.atividades = atividades or []
        self.status = status or StatusFolha.NOVA

    def iniciar_atividade(self):
        if self.status is StatusFolha.ATIVIDADE_ATIVA:
            raise FolhaDePontoError(
                "Existe uma atividade que não foi finalizada.")

        atividade = Atividade()
        self.atividades.append(atividade)
        self.status = StatusFolha.ATIVIDADE_ATIVA
        return atividade

    def finalizar_atividade(self):
        if self.status is not StatusFolha.ATIVIDADE_ATIVA:
            raise FolhaDePontoError("Nenhuma atividade foi iniciada.")

        atividade = self.atividades[-1]
        atividade.finalizar()
        self.status = StatusFolha.ATIVIDADE_FINALIZADA

        self.total_horas += atividade.total_horas
        self.valor_total = self.total_horas * self.usuario.valor_hora

        return atividade

    def __len__(self):
        return len(self.atividades)

    def __getitem__(self, item):
        return self.atividades[item]

    def fechar(self):
        self.status = StatusFolha.FECHADA

        if self.usuario.acrescimos is not None:
            total_dias_trabalhados = calcular_total_dias(self.atividades)
            self.valor_total += self.usuario.total_acrescimos * total_dias_trabalhados

        if self.acrescimos is not None:
            self.valor_total += sum(self.acrescimos.values())

        if self.decrescimos is not None:
            self.valor_total -= sum(self.decrescimos.values())

    @property
    def id(self):
        return self._id

    def adicionar_acrescimo(self, descricao, valor):
        self.acrescimos[descricao] = valor

    def adicionar_decrescimo(self, descricao, valor):
        self.decrescimos[descricao] = valor


class Atividade(Serializable):
    def __init__(self, data_final=None, data_inicial=datetime.now(), total_horas=0):
        super().__init__()
        self.data_final = data_final
        self.data_inicial = data_inicial
        self.total_horas = total_horas

    def finalizar(self):
        self.data_final = datetime.now()
        self.total_horas = (
            self.data_final - self.data_inicial).total_seconds() / 3600


class StatusFolha(IntEnum):
    NOVA = 0
    ATIVIDADE_ATIVA = 1
    ATIVIDADE_FINALIZADA = 2
    FECHADA = 3


class FolhaDePontoError(Exception):
    def __init__(self, message=None):
        self.message = message
