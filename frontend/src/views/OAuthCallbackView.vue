<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
    <div class="w-full max-w-md">
      <!-- Branding -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold gradient-text mb-2">SONGFLOW</h1>
        <p class="text-gray-400">AI Song Automation Pipeline</p>
      </div>

      <!-- Callback Card -->
      <div class="card-static text-center">
        <!-- Loading State -->
        <div v-if="isProcessing" class="space-y-4">
          <div class="flex justify-center">
            <svg
              class="animate-spin h-12 w-12 text-indigo-500"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-white">Processing Authorization</h2>
          <p class="text-gray-400">Please wait while we complete the connection...</p>
        </div>

        <!-- Success State -->
        <div v-else-if="isSuccess" class="space-y-4">
          <div class="flex justify-center">
            <svg
              class="h-12 w-12 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-white">Authorization Successful</h2>
          <p class="text-gray-400">{{ successMessage }}</p>
          <button @click="redirectToSettings" class="btn-primary">
            Continue to Settings
          </button>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="space-y-4">
          <div class="flex justify-center">
            <svg
              class="h-12 w-12 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-white">Authorization Failed</h2>
          <p class="text-red-400">{{ errorMessage }}</p>
          <button @click="redirectToSettings" class="btn-secondary">
            Return to Settings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api/client'

const router = useRouter()
const route = useRoute()

const isProcessing = ref(true)
const isSuccess = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(async () => {
  // Get OAuth parameters from URL
  const code = route.query.code as string
  const error = route.query.error as string
  const state = route.query.state as string

  // Handle OAuth error
  if (error) {
    isProcessing.value = false
    errorMessage.value = getErrorMessage(error, route.query.error_description as string)
    return
  }

  // Handle missing authorization code
  if (!code) {
    isProcessing.value = false
    errorMessage.value = 'No authorization code received. Please try again.'
    return
  }

  try {
    // Exchange authorization code for tokens via backend
    const response = await api.post('/youtube/oauth/callback', {
      code,
      state
    })

    isProcessing.value = false
    isSuccess.value = true
    successMessage.value = response.message || 'YouTube account connected successfully!'

  } catch (err: any) {
    isProcessing.value = false
    errorMessage.value = err.message || 'Failed to complete authorization. Please try again.'
  }
})

function getErrorMessage(error: string, description?: string): string {
  const errorMessages: Record<string, string> = {
    'access_denied': 'You denied access to your YouTube account.',
    'invalid_request': 'Invalid authorization request.',
    'unauthorized_client': 'Application is not authorized.',
    'server_error': 'Server error occurred. Please try again.',
  }
  return description || errorMessages[error] || `Authorization error: ${error}`
}

function redirectToSettings() {
  router.push('/settings')
}
</script>
