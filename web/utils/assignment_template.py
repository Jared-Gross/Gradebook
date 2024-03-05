from typing import Union


class AssignmentTemplate:
    def __init__(self, name: str = "", worth: float = 0.0) -> None:
        self.name: str = name
        self.worth: float = worth

    def to_dict(self) -> dict[str, Union[str, float]]:
        return {"name": self.name, "worth": self.worth}

    def from_dict(self, data: dict[str, Union[str, float]]):
        self.name: str = data["name"]
        self.worth: float = float(data["worth"])
