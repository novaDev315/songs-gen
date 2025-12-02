/**
 * API module exports
 *
 * Central export point for all API-related functionality.
 */

// Main API client
export { api } from './client'

// Re-export types if needed
export type {
  Song,
  SongCreate,
  SongUpdate,
  SongList,
  VideoProject,
  StudioProject,
  Template,
  User,
  TokenResponse
} from './client'
