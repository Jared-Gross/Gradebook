class AssignmentTemplate:
    def __init__(self, name: str = "", worth: float = 0.0) -> None:
        self.name: str = name
        self.worth: float = worth

    def to_dict(self) -> dict:
        return {"name": self.name, "worth": self.worth}

    def from_dict(self, data: dict):
        self.name = data["name"]
        self.worth = float(data["worth"])
