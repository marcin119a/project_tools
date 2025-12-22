from fastapi import APIRouter

from schemas.hello import HelloResponse

router = APIRouter()


@router.get(
    "/hello",
    response_model=HelloResponse,
    summary="Hello World",
    description="Returns classic Hello World message",
)
async def hello_world() -> HelloResponse:
    """
    Endpoint that returns a classic Hello World message.
    
    Returns:
        HelloResponse: Hello World message
    """
    return HelloResponse(message="Hello World")


@router.get(
    "/hello/{name}",
    response_model=HelloResponse,
    summary="Personalized greeting",
    description="Returns a personalized greeting for the given name",
)
async def hello(name: str) -> HelloResponse:
    """
    Endpoint that returns a personalized greeting.
    
    Args:
        name: User's name for greeting
    
    Returns:
        HelloResponse: Greeting message with the name
    """
    return HelloResponse(message=f"Hello {name}")

