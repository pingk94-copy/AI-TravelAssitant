from pydantic import BaseModel, Field


class PlaceSearchRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=120)
    city: str | None = Field(default=None, max_length=80)


class PlaceItem(BaseModel):
    name: str
    address: str
    location: str | None = None


class PlaceSearchResponse(BaseModel):
    source: str
    keyword: str
    city: str | None
    items: list[PlaceItem]


class WeatherRequest(BaseModel):
    city: str = Field(min_length=1, max_length=80)


class WeatherForecastItem(BaseModel):
    date: str
    weather: str
    temperature: str
    wind: str | None = None


class WeatherResponse(BaseModel):
    source: str
    city: str
    forecast: list[WeatherForecastItem]


class RouteRequest(BaseModel):
    origin: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    city: str | None = Field(default=None, max_length=80)
    mode: str = Field(default="walking", pattern="^(walking|driving)$")


class RouteStep(BaseModel):
    instruction: str
    distance: str | None = None
    duration: str | None = None


class RouteResponse(BaseModel):
    source: str
    origin: str
    destination: str
    mode: str
    steps: list[RouteStep]
