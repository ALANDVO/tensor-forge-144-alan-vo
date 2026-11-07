# Changelog

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-11-02

### Added
- Prompt Template Management (CRUD + Search) feature
- PromptTemplate SQLAlchemy model with name, description, template, model, tags, category, is_default fields
- RESTful API endpoints: POST/GET/PATCH/DELETE /api/v1/prompts
- Search and filter by query text, model, tags, category, default status
- Pagination support with page/page_size parameters
- Model-specific default prompt selection with fallback to global default
- SQLite persistence with UTC timestamps (created_at, updated_at)
- Comprehensive test suite (17 tests covering all CRUD operations, search, filter, pagination, default handling)

## [1.2.0] - 2026-11-06

### Added
- Model-Specific Prompt Swapping feature marked complete
- Documented existing implementation for per-model prompt templates with '小码辉' default persona
- GET /api/v1/prompts/model/{model} endpoint with model-specific default lookup and global fallback
- Updated feature plan and project documentation

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
