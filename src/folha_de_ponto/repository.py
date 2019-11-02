from pymongo import MongoClient
from src.folha_de_ponto.models import FolhaDePonto


class FolhaDePontoRepository:
    def __init__(self, client: MongoClient):
        self.client = client
        self.db = self.client["folhas"]
        self.collection = self.db[FolhaDePonto.__name__]

    def inserir(self, model: FolhaDePonto):
        self.collection.insert_one(vars(model))

    def alterar(self, model: FolhaDePonto):
        self.collection.replace_one({"_id": model.id}, vars(model))
