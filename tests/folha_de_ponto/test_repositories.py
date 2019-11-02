import unittest

from pymongo import MongoClient
from src.folha_de_ponto.models import Usuario, FolhaDePonto, StatusFolha
from src.folha_de_ponto.repository import FolhaDePontoRepository


def criar_folha(acrescimos: dict = None):
    return FolhaDePonto(Usuario("user", 7.0, acrescimos))


class FolhaDePontoRepositoryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = MongoClient("mongodb://localhost:27017")
        cls.db = cls.client["folhas"]
        cls.collection = cls.db[FolhaDePonto.__name__]

    @classmethod
    def tearDownClass(cls):
        cls.collection.delete_many({})

    def test_deve_inserir_folha_de_ponto(self):
        folha = criar_folha()

        self.repo = FolhaDePontoRepository(self.client)
        d = vars(folha)
        self.repo.inserir(folha)

        found = self.repo.collection.find_one({"_id": folha._id})

        self.assertEqual(folha, FolhaDePonto(**found))

    def test_deve_alterar_folha_de_ponto(self):
        folha = criar_folha()

        self.repo = FolhaDePontoRepository(self.client)

        self.repo.collection.insert_one(vars(folha))

        folha.status = StatusFolha.FECHADA

        self.repo.alterar(folha)

        found = self.repo.collection.find_one({"_id": folha._id})

        self.assertEqual(folha.status, found["status"])


if __name__ == '__main__':
    unittest.main()
