import abc


class BaseScraper(abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    async def login_to_page(self) -> None:
        pass

    @abc.abstractmethod
    async def get_job_entires(self):
        pass

    @abc.abstractmethod
    async def go_to_next_page(self):
        pass

    @abc.abstractmethod
    async def go_to_next_job(self):
        pass

    @abc.abstractmethod
    async def apply_for_job(self):
        pass

    @abc.abstractmethod
    async def process_job(self):
        pass

    async def evaluate_job(self):
        pass
