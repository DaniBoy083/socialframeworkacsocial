from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=512)

    @field_validator("email")
    @classmethod
    def email_is_valid(cls, value: str) -> str:
        value = value.strip().lower()
        if (
            value.count("@") != 1
            or any(c.isspace() for c in value)
            or "." not in value.split("@")[-1]
        ):
            raise ValueError("Informe um e-mail válido.")
        return value
