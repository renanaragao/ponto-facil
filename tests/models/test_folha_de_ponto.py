import unittest
from datetime import datetime, timedelta

from src.models.models import FolhaDePonto, StatusFolha, FolhaDePontoError, Usuario


def criar_folha(acrescimos: dict=None):
    return FolhaDePonto(Usuario("user", 7.0, acrescimos))


class TestFolhaDePonto(unittest.TestCase):
    def test_deve_inicializar_um_folha_de_ponto_com_usuario(self):
        folha = criar_folha()

        self.assertEqual(folha.data.strftime("%x"), datetime.now().strftime("%x"))
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

        self.assertEqual(ex.exception.message, "Existe uma atividade que não foi finalizada.")

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

        self.assertEqual(ex.exception.message, "Nenhuma atividade foi iniciada.")

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

    def test_deve_calcular_total_de_horas_e_valor_total_com_acrescimos(self):

        acrescimos = {"transporte ida": 4.20, "trasnporte volta": 4.20}

        folha = criar_folha(acrescimos)

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(days=1)
        folha.finalizar_atividade()

        atividade = folha.iniciar_atividade()
        atividade.data_inicial = datetime.now() - timedelta(hours=3, minutes=20)
        folha.finalizar_atividade()

        folha.fechar()

        self.assertEqual(round(folha.total_horas, 2), 27.33)
        self.assertEqual(round(folha.valor_total, 2), 208.11)
        self.assertEqual(folha.status, StatusFolha.FECHADA)
