"""Pydantic schemas for prompt template API."""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PromptTemplateBase(BaseModel):
    """Base schema for prompt template."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    template: str = Field(..., min_length=1, description="Prompt template text")
    model: Optional[str] = Field(None, max_length=100, description="Target model identifier")
    tags: Optional[list[str]] = Field(default_factory=list, description="Template tags")
    category: Optional[str] = Field(None, max_length=100, description="Template category")
    is_default: bool = Field(default=False, description="Whether this is the default template")


class PromptTemplateCreate(PromptTemplateBase):
    """Schema for creating a prompt template."""
    pass


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a prompt template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None


class PromptTemplateResponse(PromptTemplateBase):
    """Schema for prompt template response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptTemplateListResponse(BaseModel):
    """Schema for paginated prompt template list response."""
    items: list[PromptTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PromptTemplateSearchParams(BaseModel):
    """Query parameters for searching prompt templates."""
    q: Optional[str] = Field(None, description="Search query (name, description, template)")
    model: Optional[str] = Field(None, description="Filter by model")
    tags: Optional[list[str]] = Field(None, description="Filter by tags")
    category: Optional[str] = Field(None, description="Filter by category")
    is_default: Optional[bool] = Field(None, description="Filter by default status")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

