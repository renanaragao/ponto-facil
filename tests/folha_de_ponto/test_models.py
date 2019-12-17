import unittest
from datetime import datetime, timedelta

from src.folha_de_ponto.models import FolhaDePonto, StatusFolha, FolhaDePontoError, Usuario


def criar_folha(acrescimos: dict = None):
    return FolhaDePonto(Usuario("user", 7.0, acrescimos))


class TestFolhaDePonto(unittest.TestCase):
    def test_deve_inicializar_um_folha_de_ponto_com_usuario(self):
        folha = criar_folha()

        self.assertEqual(folha.data.strftime(
            "%x"), datetime.now().strftime("%x"))
        self.assertEqual(folha.status, StatusFolha.NOVA)

    def test_deve_iniciar_uma_atividade(self):
        folha = criar_folha()

        atividade = folha.iniciar_atividade()

        self.assertEqual(len(folha), 1)
        self.assertEqual(folha[0], atividade)
        self.assertEqual(folha.status, StatusFolha.ATIVIDADE_ATIVA)

    def test_nao_deve_ser_possivel_iniciar_uma_atividade_sem_finalizar_a_anterior(self):
        folha = criar_folha()

        with self.assertRaises(FolhaDePontoError) as ex:
            folha.iniciar_atividade()
            folha.iniciar_atividade()

        self.assertEqual(ex.exception.message,
                         "Existe uma atividade que não foi finalizada.")

    def test_deve_finalizar_uma_atividade(self):
        folha = criar_folha()

        folha.iniciar_atividade()
        atividade = folha.finalizar_atividade()

        self.assertEqual(len(folha), 1)
        self.assertEqual(folha[0], atividade)
        self.assertEqual(folha.status, StatusFolha.ATIVIDADE_FINALIZADA)

    def test_nao_deve_ser_possivel_finalizar_uma_atividade_sem_iniciar_primeiro(self):
        folha = criar_folha()

        with self.assertRaises(FolhaDePontoError) as ex:
            folha.finalizar_atividade()

        self.assertEqual(ex.exception.message,
                         "Nenhuma atividade foi iniciada.")

    def test_deve_calcular_total_de_horas_e_valor_total(self):
        folha = criar_folha()
        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=4)
        folha.finalizar_atividade()

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=3, minutes=20)
        folha.finalizar_atividade()

        folha.fechar()

        self.assertEqual(folha.status, StatusFolha.FECHADA)
        self.assertEqual(round(folha.total_horas, 2), 7.33)
        self.assertEqual(round(folha.valor_total, 2), 51.33)

    def test_deve_calcular_total_de_horas_e_valor_total_com_acrescimos_do_usuario(self):

        acrescimos = {"transporte ida": 4.20, "trasnporte volta": 4.20}

        folha = criar_folha(acrescimos)

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=24)
        folha.finalizar_atividade()

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=3, minutes=20)
        folha.finalizar_atividade()

        folha.fechar()

        self.assertEqual(round(folha.total_horas, 2), 27.33)
        self.assertEqual(round(folha.valor_total, 2), 208.13)
        self.assertEqual(folha.status, StatusFolha.FECHADA)

    def test_deve_adicionar_acrescimo_na_folha_de_ponto(self):
        acrescimo = {"ida": 4.20, "volta": 4.20}

        folha = criar_folha()

        folha.adicionar_acrescimo("ida", acrescimo["ida"])
        folha.adicionar_acrescimo("volta", acrescimo["volta"])

        self.assertEqual(folha.acrescimos, acrescimo)

    def test_deve_adicionar_decrescimo_na_folha_de_ponto(self):
        decrescimo = {"ida": 4.20, "volta": 4.20}

        folha = criar_folha()

        folha.adicionar_decrescimo("ida", decrescimo["ida"])
        folha.adicionar_decrescimo("volta", decrescimo["volta"])

        self.assertEqual(folha.decrescimos, decrescimo)

    def test_deve_calcular_total_de_horas_e_valor_total_com_acrescimos_da_folha(self):

        acrescimos = {"ida": 4.20, "volta": 4.20}

        folha = criar_folha(acrescimos)

        folha.adicionar_acrescimo("ida", acrescimos["ida"])
        folha.adicionar_acrescimo("volta", acrescimos["volta"])

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=24)
        folha.finalizar_atividade()

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=3, minutes=20)
        folha.finalizar_atividade()

        folha.fechar()

        self.assertEqual(round(folha.total_horas, 2), 27.33)
        self.assertEqual(round(folha.valor_total, 2), 216.53)
        self.assertEqual(folha.status, StatusFolha.FECHADA)

    def test_deve_calcular_total_de_horas_e_valor_total_com_decrescimos_da_folha(self):

        acrescimos = {"ida": 4.20, "volta": 4.20}
        decrescimos = {"ida": 4.20, "volta": 4.20}

        folha = criar_folha(acrescimos)

        folha.adicionar_decrescimo("ida", decrescimos["ida"])
        folha.adicionar_decrescimo("volta", decrescimos["volta"])

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=24)
        folha.finalizar_atividade()

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=3, minutes=20)
        folha.finalizar_atividade()

        folha.fechar()

        self.assertEqual(round(folha.total_horas, 2), 27.33)
        self.assertEqual(round(folha.valor_total, 2), 199.73)
        self.assertEqual(folha.status, StatusFolha.FECHADA)


class TestUsuario(unittest.TestCase):
    def test_deve_adicionar_acrescimos(self):
        acrescimo = {"B": 2}

        usuario = Usuario("user", 7.0, None)

        self.assertIsNone(usuario.acrescimos)

        usuario.adicionar_acrescimo('B', acrescimo['B'])
        usuario.adicionar_acrescimo('C', 8)

        self.assertEqual(usuario.acrescimos, {'B': 2, 'C': 8})
        self.assertEqual(usuario.total_acrescimos, 10)
