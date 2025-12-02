# Mini YouTube Studio - Step Components

This directory contains the 6 wizard step components for the Mini YouTube Studio feature.

## Components Overview

### 1. SongSelectStep.vue
**Purpose**: Select a downloaded song to create a video for

**Features**:
- Search/filter songs by title or genre
- Grid display of downloaded songs
- Visual selection state with amber highlighting
- Empty state when no songs available
- Loading state with spinner

**Store Methods Used**:
- `store.selectSong(song)` - Set selected song

### 2. CoverArtStep.vue
**Purpose**: Choose or create cover art for the video thumbnail

**Features**:
- Three creation methods:
  - **Template**: Genre-based templates (free & instant)
  - **AI Generated**: Custom AI-generated cover art
  - **Upload**: Upload your own image
- Genre-specific template suggestions
- Live preview of selected/generated cover
- Skip option for default cover

**Store Methods Used**:
- `store.generateTemplateCover(templateId)` - Generate from template
- `store.generateAICover(prompt?)` - AI generation
- `store.uploadCover(file)` - Upload custom image

### 3. VideoSettingsStep.vue
**Purpose**: Customize video visual style and appearance

**Features**:
- Visual style selection:
  - Waveform (animated audio waves)
  - Spectrum (frequency bars)
  - Particles (particle effects)
  - Static Cover (just the image)
- Color theme selection:
  - Genre-based
  - Monochrome
  - Neon
  - Warm/Cool
  - Custom (with color picker)
- Additional toggles:
  - Show title overlay
  - Show artist name
  - High quality (1080p vs 720p)

**Store Methods Used**:
- `store.updateVideoSettings(settings)` - Update any video setting

### 4. MetadataStep.vue
**Purpose**: Edit YouTube video metadata (title, description, tags)

**Features**:
- Title input (max 100 chars)
- Description textarea (max 5000 chars)
- Tag management:
  - Add/remove tags
  - Suggested tags based on genre
  - Max 15 tags
  - Keyboard shortcuts (Enter to add, Backspace to remove)
- Category dropdown (Music, Entertainment, etc.)
- Privacy selection (Public, Unlisted, Private)
- Live preview of metadata

**Store Methods Used**:
- `store.updateMetadata(metadata)` - Update metadata fields

### 5. PreviewStep.vue
**Purpose**: Generate and preview the video before publishing

**Features**:
- Configuration summary display
- Video generation with progress tracking:
  - Real-time progress bar (0-100%)
  - Step-by-step status updates
  - 5 generation stages tracked
- Video player with controls
- Actions:
  - Play/Pause
  - Download video
  - Regenerate
- Video information display (duration, resolution, format, file size)
- Success confirmation when ready

**Store Methods Used**:
- `store.generateVideo()` - Start video generation
- `store.checkVideoStatus()` - Poll for generation status

### 6. PublishStep.vue
**Purpose**: Final review and publish to YouTube

**Features**:
- Pre-publish checklist validation
- Publishing summary (all metadata, settings, file size)
- Publishing options:
  - **Publish Now**: Immediate upload
  - **Schedule**: Set date/time for later
- Upload progress tracking (4 stages)
- Success state with:
  - YouTube URL display
  - Copy link button
  - Next action buttons (Create Another, Go to Dashboard)

**Store Methods Used**:
- `store.publishToYouTube(scheduleDate?)` - Upload to YouTube
- `store.updateSongStatus(status)` - Update song status
- `store.reset()` - Reset wizard for next video

## Usage in StudioWizard Component

```vue
<script setup lang="ts">
import { useStudioStore } from '@/stores/studio'
import {
  SongSelectStep,
  CoverArtStep,
  VideoSettingsStep,
  MetadataStep,
  PreviewStep,
  PublishStep
} from './steps'

const store = useStudioStore()
</script>

<template>
  <component :is="currentStepComponent" />
</template>
```

## Design Patterns

All step components follow these patterns:

### 1. Consistent Header Structure
```vue
<h2 class="text-2xl font-bold text-white mb-2">Step Title</h2>
<p class="text-slate-400 mb-6">Step description</p>
```

### 2. Amber/Gold Theme for Selection
```vue
:class="[
  'p-4 rounded-xl border-2 transition-all',
  isSelected
    ? 'bg-amber-500/20 border-amber-500 ring-2 ring-amber-500/30'
    : 'bg-slate-700/30 border-slate-600 hover:border-slate-500'
]"
```

### 3. Loading States
```vue
<div v-if="isLoading" class="flex justify-center py-12">
  <div class="animate-spin w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full"></div>
</div>
```

### 4. Success/Error States
```vue
<!-- Success -->
<div class="p-4 bg-emerald-500/20 border border-emerald-500 rounded-xl">
  <div class="flex items-center gap-3">
    <div class="text-2xl">✓</div>
    <div class="text-emerald-300">Success message</div>
  </div>
</div>

<!-- Error -->
<div class="p-4 bg-red-500/20 border border-red-500 rounded-xl">
  <div class="flex items-center gap-3">
    <div class="text-2xl">✗</div>
    <div class="text-red-300">Error message</div>
  </div>
</div>
```

### 5. Progress Tracking
```vue
<div class="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
  <div
    class="bg-gradient-to-r from-amber-500 to-orange-500 h-full transition-all duration-500"
    :style="{ width: progress + '%' }"
  ></div>
</div>
```

## Store Integration

All components rely on the `useStudioStore()` for state management. Key store properties:

```typescript
interface StudioStore {
  // Selection
  selectedSong: Song | null

  // Cover art
  cover: {
    type: 'template' | 'ai' | 'upload' | 'skip'
    path: string | null
  }

  // Video settings
  videoSettings: {
    visualStyle: 'waveform' | 'spectrum' | 'particles' | 'static_cover'
    colorTheme: 'genre_based' | 'monochrome' | 'neon' | 'warm' | 'cool' | 'custom'
    customColors?: { primary: string, secondary: string, accent: string }
    showTitle: boolean
    showArtist: boolean
    highQuality: boolean
  }

  // Metadata
  metadata: {
    title: string
    description: string
    tags: string[]
    category: string
    privacy: 'public' | 'unlisted' | 'private'
  }

  // Generated video
  generatedVideo: {
    song_id: string
    status: 'pending' | 'generating' | 'completed' | 'failed'
    progress: number
    message: string
    video_path: string | null
    error?: string
  }

  // Wizard state
  currentStep: number
  isLoading: boolean
}
```

## Mobile Responsiveness

All components use responsive grid layouts:

```vue
<!-- 2-column on desktop, 1-column on mobile -->
<div class="grid gap-4 md:grid-cols-2">

<!-- 3-column on desktop, 1-column on mobile -->
<div class="grid gap-3 md:grid-cols-3">
```

## Accessibility

- All interactive elements are keyboard accessible
- Color contrast meets WCAG AA standards
- Loading states announced via aria-live regions (implicit)
- Form inputs have proper labels

## Next Steps

1. Ensure the `useStudioStore()` is implemented with all required methods
2. Connect the wizard navigation in `StudioWizard.vue`
3. Implement backend API endpoints for:
   - Cover generation
   - Video rendering
   - YouTube upload
4. Test each step individually before integration
5. Add error boundaries for graceful failure handling
