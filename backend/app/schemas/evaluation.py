"""Pydantic schemas for jailbreak evaluation API."""
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


class EvaluationCreate(BaseModel):
    """Schema for creating an evaluation run."""
    prompt_id: int = Field(..., description="Prompt template ID to evaluate")
    model: str = Field(..., max_length=100, description="Model identifier to test against")
    test_cases: Optional[List[str]] = Field(
        default=None,
        description="List of test case prompts; if None, uses prompt's template",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(
        default=1000,
        ge=1,
        description="Maximum tokens to generate",
    )


class EvaluationResult(BaseModel):
    """Schema for a single evaluation result."""
    prompt_id: int
    model: str
    test_case: str
    success: bool = Field(
        description="Whether the prompt was effective (jailbreak succeeded)",
    )
    refusal: bool = Field(
        description="Whether the model refused the prompt",
    )
    token_usage: int = Field(
        ge=0,
        description="Number of tokens consumed",
    )
    latency_ms: float = Field(
        ge=0,
        description="Response latency in milliseconds",
    )
    evaluated_at: Union[datetime, str] = Field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z",
        description="When the evaluation was run",
    )


class EvaluationRunResponse(BaseModel):
    """Schema for an evaluation run response."""
    id: int
    prompt_id: int
    model: str
    status: str = Field(description="Evaluation status: completed, running, failed")
    created_at: datetime
    results: List[EvaluationResult] = Field(
        default_factory=list,
        description="List of evaluation results",
    )

    class Config:
        from_attributes = True


class EvaluationSearchParams(BaseModel):
    """Query parameters for searching evaluation runs."""
    prompt_id: Optional[int] = Field(
        None,
        description="Filter by prompt template ID",
    )
    model: Optional[str] = Field(
        None,
        description="Filter by model identifier",
    )
    status: Optional[str] = Field(
        None,
        description="Filter by status",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page",
    )
