from __future__ import annotations

from pydantic import BaseModel, Field


class DomainRequest(BaseModel):
    domain: str = Field(..., min_length=1, max_length=253, examples=["example.com"])

