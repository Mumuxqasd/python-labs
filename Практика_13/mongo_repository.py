from exceptions import ServerNotFoundError, StorageUnavailableError
from models import ServerDocument


class MongoServerRepository:
    def __init__(self, uri: str = "mongodb://127.0.0.1:27017", db_name: str = "lab13") -> None:
        try:
            from pymongo import MongoClient
        except ModuleNotFoundError as error:
            raise StorageUnavailableError("Установите pymongo") from error
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=1500)
            self.client.admin.command("ping")
        except Exception as error:
            raise StorageUnavailableError("MongoDB недоступна") from error
        self.collection = self.client[db_name]["servers"]
        self.collection.create_index("hostname", unique=True)
        self.collection.create_index("status")

    def add(self, server: ServerDocument) -> str:
        result = self.collection.insert_one(server.to_dict())
        return str(result.inserted_id)

    def get(self, server_id: str) -> dict:
        from bson import ObjectId
        document = self.collection.find_one({"_id": ObjectId(server_id)})
        if document is None:
            raise ServerNotFoundError("Сервер не найден")
        document["_id"] = str(document["_id"])
        return document

    def list_all(self) -> list[dict]:
        result = []
        for document in self.collection.find().sort("hostname", 1):
            document["_id"] = str(document["_id"])
            result.append(document)
        return result

    def search(self, text: str) -> list[dict]:
        query = {"$or": [{"hostname": {"$regex": text, "$options": "i"}}, {"ip": {"$regex": text, "$options": "i"}}]}
        result = []
        for document in self.collection.find(query):
            document["_id"] = str(document["_id"])
            result.append(document)
        return result

    def by_status(self, status: str) -> list[dict]:
        result = []
        for document in self.collection.find({"history.status": status}):
            document["_id"] = str(document["_id"])
            result.append(document)
        return result

    def update(self, server_id: str, changes: dict) -> dict:
        from bson import ObjectId
        self.collection.update_one({"_id": ObjectId(server_id)}, {"$set": changes})
        return self.get(server_id)

    def delete(self, server_id: str) -> None:
        from bson import ObjectId
        result = self.collection.delete_one({"_id": ObjectId(server_id)})
        if result.deleted_count == 0:
            raise ServerNotFoundError("Сервер не найден")

    def statistics(self) -> list[dict]:
        pipeline = [
            {"$unwind": {"path": "$services", "preserveNullAndEmptyArrays": True}},
            {"$group": {"_id": "$os_name", "servers": {"$addToSet": "$hostname"}, "services": {"$sum": 1}}},
            {"$project": {"_id": 0, "os": "$_id", "servers_count": {"$size": "$servers"}, "services_count": "$services"}},
        ]
        return list(self.collection.aggregate(pipeline))
