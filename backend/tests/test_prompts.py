"""Tests for prompt template API."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_prompt(client: AsyncClient):
    """Test creating a prompt template."""
    prompt_data = {
        "name": "Test Prompt",
        "description": "A test prompt template",
        "template": "You are a helpful assistant. User: {input}",
        "model": "gpt-4",
        "tags": ["test", "chat"],
        "category": "general",
        "is_default": True,
    }
    response = await client.post("/api/v1/prompts", json=prompt_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Prompt"
    assert data["template"] == "You are a helpful assistant. User: {input}"
    assert data["model"] == "gpt-4"
    assert data["tags"] == ["test", "chat"]
    assert data["category"] == "general"
    assert data["is_default"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_prompt_minimal(client: AsyncClient):
    """Test creating a prompt template with only required fields."""
    prompt_data = {
        "name": "Minimal Prompt",
        "template": "Hello {input}",
    }
    response = await client.post("/api/v1/prompts", json=prompt_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Prompt"
    assert data["template"] == "Hello {input}"
    assert data["model"] is None
    assert data["tags"] == []
    assert data["is_default"] is False


@pytest.mark.asyncio
async def test_list_prompts(client: AsyncClient):
    """Test listing prompt templates."""
    # Create a few prompts
    for i in range(3):
        await client.post("/api/v1/prompts", json={
            "name": f"Prompt {i}",
            "template": f"Template {i}",
            "model": "gpt-4" if i % 2 == 0 else "claude-3",
            "tags": ["tag1"] if i == 0 else ["tag2"],
        })

    response = await client.get("/api/v1/prompts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 3
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_list_prompts_with_pagination(client: AsyncClient):
    """Test listing prompt templates with pagination."""
    # Create 5 prompts
    for i in range(5):
        await client.post("/api/v1/prompts", json={
            "name": f"Prompt {i}",
            "template": f"Template {i}",
        })

    response = await client.get("/api/v1/prompts?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_list_prompts_with_search(client: AsyncClient):
    """Test searching prompt templates by query."""
    await client.post("/api/v1/prompts", json={
        "name": "Special Prompt",
        "template": "Special template content",
        "model": "gpt-4",
    })
    await client.post("/api/v1/prompts", json={
        "name": "Another Prompt",
        "template": "Different content",
        "model": "claude-3",
    })

    response = await client.get("/api/v1/prompts?q=Special")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Special Prompt"


@pytest.mark.asyncio
async def test_list_prompts_filter_by_model(client: AsyncClient):
    """Test filtering prompt templates by model."""
    await client.post("/api/v1/prompts", json={
        "name": "GPT Prompt",
        "template": "GPT template",
        "model": "gpt-4",
    })
    await client.post("/api/v1/prompts", json={
        "name": "Claude Prompt",
        "template": "Claude template",
        "model": "claude-3",
    })

    response = await client.get("/api/v1/prompts?model=gpt-4")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["model"] == "gpt-4"


@pytest.mark.asyncio
async def test_list_prompts_filter_by_tags(client: AsyncClient):
    """Test filtering prompt templates by tags."""
    await client.post("/api/v1/prompts", json={
        "name": "Tagged Prompt",
        "template": "Tagged template",
        "tags": ["important", "reviewed"],
    })
    await client.post("/api/v1/prompts", json={
        "name": "Untagged Prompt",
        "template": "Untagged template",
        "tags": ["draft"],
    })

    response = await client.get("/api/v1/prompts?tags=important")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert "important" in data["items"][0]["tags"]


@pytest.mark.asyncio
async def test_get_prompt(client: AsyncClient):
    """Test getting a prompt template by ID."""
    create_response = await client.post("/api/v1/prompts", json={
        "name": "Get Test Prompt",
        "template": "Get template",
    })
    prompt_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/prompts/{prompt_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == prompt_id
    assert data["name"] == "Get Test Prompt"


@pytest.mark.asyncio
async def test_get_prompt_not_found(client: AsyncClient):
    """Test getting a non-existent prompt template."""
    response = await client.get("/api/v1/prompts/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_default_prompt_for_model(client: AsyncClient):
    """Test getting the default prompt for a specific model."""
    # Create model-specific default
    await client.post("/api/v1/prompts", json={
        "name": "GPT Default",
        "template": "GPT default template",
        "model": "gpt-4",
        "is_default": True,
    })
    # Create global default
    await client.post("/api/v1/prompts", json={
        "name": "Global Default",
        "template": "Global default template",
        "is_default": True,
    })

    response = await client.get("/api/v1/prompts/model/gpt-4")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "GPT Default"
    assert data["model"] == "gpt-4"
    assert data["is_default"] is True


@pytest.mark.asyncio
async def test_get_default_prompt_fallback_to_global(client: AsyncClient):
    """Test fallback to global default when model-specific not found."""
    # Create only global default
    await client.post("/api/v1/prompts", json={
        "name": "Global Default",
        "template": "Global default template",
        "is_default": True,
    })

    response = await client.get("/api/v1/prompts/model/unknown-model")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Global Default"
    assert data["model"] is None


@pytest.mark.asyncio
async def test_get_default_prompt_not_found(client: AsyncClient):
    """Test getting default prompt when none exists."""
    response = await client.get("/api/v1/prompts/model/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt(client: AsyncClient):
    """Test updating a prompt template."""
    create_response = await client.post("/api/v1/prompts", json={
        "name": "Original Name",
        "template": "Original template",
        "model": "gpt-4",
    })
    prompt_id = create_response.json()["id"]

    response = await client.patch(f"/api/v1/prompts/{prompt_id}", json={
        "name": "Updated Name",
        "template": "Updated template",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["template"] == "Updated template"
    assert data["model"] == "gpt-4"  # unchanged


@pytest.mark.asyncio
async def test_update_prompt_not_found(client: AsyncClient):
    """Test updating a non-existent prompt template."""
    response = await client.patch("/api/v1/prompts/99999", json={
        "name": "Updated",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt_default_flag(client: AsyncClient):
    """Test updating prompt to be default unsets other defaults."""
    # Create two prompts for same model, first is default
    p1 = await client.post("/api/v1/prompts", json={
        "name": "First Default",
        "template": "Template 1",
        "model": "gpt-4",
        "is_default": True,
    })
    p1_id = p1.json()["id"]

    p2 = await client.post("/api/v1/prompts", json={
        "name": "Second",
        "template": "Template 2",
        "model": "gpt-4",
    })
    p2_id = p2.json()["id"]

    # Update second to be default
    response = await client.patch(f"/api/v1/prompts/{p2_id}", json={
        "is_default": True,
    })
    assert response.status_code == 200
    assert response.json()["is_default"] is True

    # Verify first is no longer default
    response = await client.get(f"/api/v1/prompts/{p1_id}")
    assert response.status_code == 200
    assert response.json()["is_default"] is False


@pytest.mark.asyncio
async def test_delete_prompt(client: AsyncClient):
    """Test deleting a prompt template."""
    create_response = await client.post("/api/v1/prompts", json={
        "name": "To Delete",
        "template": "Delete template",
    })
    prompt_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/prompts/{prompt_id}")
    assert response.status_code == 204

    # Verify deleted
    response = await client.get(f"/api/v1/prompts/{prompt_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_prompt_not_found(client: AsyncClient):
    """Test deleting a non-existent prompt template."""
    response = await client.delete("/api/v1/prompts/99999")
    assert response.status_code == 404
