from fastapi import APIRouter

from schemas.hello import HelloResponse

router = APIRouter()


@router.get(
    "/hello/{name}",
    response_model=HelloResponse,
    summary="Spersonalizowane powitanie",
    description="Zwraca spersonalizowane powitanie dla podanego imienia",
)
async def hello(name: str) -> HelloResponse:
    """
    Endpoint zwracający spersonalizowane powitanie.
    
    Args:
        name: Imię użytkownika do powitania
    
    Returns:
        HelloResponse: Komunikat powitalny z imieniem
    """
    return HelloResponse(message=f"Hello {name}")

