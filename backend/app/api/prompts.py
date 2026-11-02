"""Prompt template API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, text
from sqlalchemy.orm import Session

from app.core.database import get_db, PromptTemplate
from app.schemas.prompt import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    PromptTemplateListResponse,
    PromptTemplateSearchParams,
)

router = APIRouter(prefix="/prompts", tags=["prompts"])


def apply_search_filters(query, params: PromptTemplateSearchParams):
    """Apply search filters to a query."""
    if params.q:
        search_term = f"%{params.q}%"
        query = query.where(
            or_(
                PromptTemplate.name.ilike(search_term),
                PromptTemplate.description.ilike(search_term),
                PromptTemplate.template.ilike(search_term),
            )
        )
    if params.model:
        query = query.where(PromptTemplate.model == params.model)
    if params.category:
        query = query.where(PromptTemplate.category == params.category)
    if params.is_default is not None:
        query = query.where(PromptTemplate.is_default == params.is_default)
    if params.tags:
        # For SQLite JSON array - use json_each to check if all tags are present
        for tag in params.tags:
            query = query.where(
                text("EXISTS (SELECT 1 FROM json_each(tags) WHERE value = :tag)")
            ).params(tag=tag)
    return query


@router.post("", response_model=PromptTemplateResponse, status_code=201)
async def create_prompt(
    prompt: PromptTemplateCreate,
    db: Session = Depends(get_db),
) -> PromptTemplateResponse:
    """Create a new prompt template."""
    # If setting as default, unset other defaults for the same model
    if prompt.is_default and prompt.model:
        db.execute(
            PromptTemplate.__table__.update()
            .where(PromptTemplate.model == prompt.model)
            .where(PromptTemplate.is_default == True)
            .values(is_default=False)
        )
    elif prompt.is_default and not prompt.model:
        # Unset global default
        db.execute(
            PromptTemplate.__table__.update()
            .where(PromptTemplate.is_default == True)
            .where(PromptTemplate.model.is_(None))
            .values(is_default=False)
        )

    db_prompt = PromptTemplate(**prompt.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return PromptTemplateResponse.model_validate(db_prompt)


@router.get("", response_model=PromptTemplateListResponse)
async def list_prompts(
    q: Optional[str] = Query(None, description="Search query (name, description, template)"),
    model: Optional[str] = Query(None, description="Filter by model"),
    tags: Optional[list[str]] = Query(None, description="Filter by tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_default: Optional[bool] = Query(None, description="Filter by default status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> PromptTemplateListResponse:
    """List prompt templates with search, filter, and pagination."""
    params = PromptTemplateSearchParams(
        q=q, model=model, tags=tags, category=category,
        is_default=is_default, page=page, page_size=page_size
    )

    query = select(PromptTemplate)
    query = apply_search_filters(query, params)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Apply pagination
    query = query.order_by(PromptTemplate.created_at.desc())
    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)

    items = db.execute(query).scalars().all()

    total_pages = (total + params.page_size - 1) // params.page_size

    return PromptTemplateListResponse(
        items=[PromptTemplateResponse.model_validate(item) for item in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )


@router.get("/{prompt_id}", response_model=PromptTemplateResponse)
async def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
) -> PromptTemplateResponse:
    """Get a prompt template by ID."""
    prompt = db.get(PromptTemplate, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(prompt)


@router.get("/model/{model}", response_model=PromptTemplateResponse)
async def get_default_prompt_for_model(
    model: str,
    db: Session = Depends(get_db),
) -> PromptTemplateResponse:
    """Get the default prompt template for a specific model."""
    # First try model-specific default
    prompt = db.execute(
        select(PromptTemplate)
        .where(PromptTemplate.model == model)
        .where(PromptTemplate.is_default == True)
    ).scalar_one_or_none()

    if prompt:
        return PromptTemplateResponse.model_validate(prompt)

    # Fallback to global default
    prompt = db.execute(
        select(PromptTemplate)
        .where(PromptTemplate.is_default == True)
        .where(PromptTemplate.model.is_(None))
    ).scalar_one_or_none()

    if prompt:
        return PromptTemplateResponse.model_validate(prompt)

    raise HTTPException(
        status_code=404,
        detail=f"No default prompt template found for model '{model}'"
    )


@router.patch("/{prompt_id}", response_model=PromptTemplateResponse)
async def update_prompt(
    prompt_id: int,
    prompt_update: PromptTemplateUpdate,
    db: Session = Depends(get_db),
) -> PromptTemplateResponse:
    """Update a prompt template."""
    prompt = db.get(PromptTemplate, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    update_data = prompt_update.model_dump(exclude_unset=True)

    # Handle default flag changes
    if update_data.get("is_default") is True:
        model = update_data.get("model", prompt.model)
        if model:
            db.execute(
                PromptTemplate.__table__.update()
                .where(PromptTemplate.model == model)
                .where(PromptTemplate.is_default == True)
                .where(PromptTemplate.id != prompt_id)
                .values(is_default=False)
            )
        else:
            db.execute(
                PromptTemplate.__table__.update()
                .where(PromptTemplate.is_default == True)
                .where(PromptTemplate.model.is_(None))
                .where(PromptTemplate.id != prompt_id)
                .values(is_default=False)
            )

    for field, value in update_data.items():
        setattr(prompt, field, value)

    db.commit()
    db.refresh(prompt)
    return PromptTemplateResponse.model_validate(prompt)


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a prompt template."""
    prompt = db.get(PromptTemplate, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    db.delete(prompt)
    db.commit()
