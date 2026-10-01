"""Pydantic models for retro-digitised SSRQ volume metadata."""

from pydantic import BaseModel, Field


class RegisterVolume(BaseModel):
    """Metadata shared by register-volume conversion and display."""

    canton: str = Field(pattern=r"^[A-Z]{2}(?:[-/][A-Z]{2})?$")
    volume: str = Field(min_length=1)
    title: str = Field(min_length=1)
    editors: list[str] = Field(min_length=1)
