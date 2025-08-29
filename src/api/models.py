from pydantic import BaseModel

# Pydantic models define the structure of your API data.
# They provide data validation and serialization.

class AskRequest(BaseModel):
    """
    Defines the structure of the request body for the /ask endpoint.
    The API will expect a JSON object with a single key "query" of type string.
    """
    query: str

class AskResponse(BaseModel):
    """
    Defines the structure of the response body for the /ask endpoint.
    The API will return a JSON object with a single key "answer" of type string.
    """
    answer: str

