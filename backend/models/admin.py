# models/admin.py
from dataclasses import dataclass

@dataclass
class Admin:
    id: int
    name: str
    email: str
    department: str = None
    role: str = "Admin"

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Admin(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            department=row["department"] if "department" in row.keys() else None,
            role=row["role"]
        )
