from priority import ManualPriorityStrategy
from repository import InMemoryRepository
from service import TaskService
from ui import ConsoleUI

def main() -> None:
    repository = InMemoryRepository()
    strategy = ManualPriorityStrategy()
    service = TaskService(repository, strategy)
    ui = ConsoleUI(service)
    ui.run()

if __name__ == "__main__":
    main()