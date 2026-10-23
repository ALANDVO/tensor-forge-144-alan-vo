/// <reference types="vitest" />
/// <reference types="@testing-library/jest-dom" />
import { beforeEach, describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

// Mock fetch for health check
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders header with product name', () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy', service: 'tensor-forge-backend' })
    })

    render(<App />)

    expect(screen.getByText('Tensor Forge 144')).toBeInTheDocument()
    expect(screen.getByText('Jailbreak Evaluation Framework for LLMs')).toBeInTheDocument()
  })

  it('shows checking status initially', () => {
    let resolveFn: (value: Response) => void
    const promise = new Promise<Response>((resolve) => {
      resolveFn = resolve
    })
    mockFetch.mockReturnValue(promise)

    render(<App />)

    expect(screen.getByText('Checking...')).toBeInTheDocument()
    resolveFn!({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy', service: 'tensor-forge-backend' })
    } as Response)
  })

  it('shows healthy status when API responds ok', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy', service: 'tensor-forge-backend' })
    })

    render(<App />)

    await screen.findByText('Healthy')
    expect(screen.getByText('Healthy')).toBeInTheDocument()
  })
})