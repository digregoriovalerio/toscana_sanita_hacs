from pydantic import BaseModel, ConfigDict


class CamelCaseModel(BaseModel):
    """Base model configured to handle camelCase aliases mapping to snake_case properties."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
