<template>
  <div class="min-h-screen flex items-center justify-center p-4 overflow-hidden relative">
    <!-- Animated background -->
    <div class="absolute inset-0 bg-studio-void">
      <!-- Gradient mesh -->
      <div class="absolute inset-0 bg-mesh-rose opacity-50"></div>

      <!-- Floating orbs -->
      <div
        class="absolute top-1/4 left-1/4 w-96 h-96 rounded-full animate-float"
        style="background: radial-gradient(circle, rgba(204, 122, 90, 0.15) 0%, transparent 60%); animation-duration: 8s;"
      ></div>
      <div
        class="absolute bottom-1/4 right-1/4 w-72 h-72 rounded-full animate-float"
        style="background: radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, transparent 60%); animation-delay: -3s; animation-duration: 10s;"
      ></div>
      <div
        class="absolute top-1/2 right-1/3 w-48 h-48 rounded-full animate-float"
        style="background: radial-gradient(circle, rgba(201, 162, 39, 0.1) 0%, transparent 60%); animation-delay: -5s; animation-duration: 7s;"
      ></div>

      <!-- Grid lines -->
      <div class="absolute inset-0 opacity-[0.02]" style="background-image: linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px); background-size: 60px 60px;"></div>

      <!-- Noise texture -->
      <div class="noise-overlay"></div>
    </div>

    <!-- Login container -->
    <div
      class="w-full max-w-md relative z-10"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.98)',
        transition: 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1)'
      }"
    >
      <!-- Branding -->
      <div class="text-center mb-10">
        <!-- Animated vinyl disc logo -->
        <div
          class="relative w-24 h-24 mx-auto mb-6"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'scale(1) rotate(0)' : 'scale(0.5) rotate(-90deg)',
            transition: 'all 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s'
          }"
        >
          <!-- Outer glow ring -->
          <div class="absolute -inset-4 rounded-full bg-studio-rose-500/10 blur-xl animate-pulse-soft"></div>

          <!-- Vinyl disc -->
          <div class="absolute inset-0 vinyl-disc animate-spin-slower">
            <div class="vinyl-label w-8 h-8"></div>
          </div>

          <!-- Light reflection -->
          <div class="absolute inset-0 rounded-full" style="background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(0,0,0,0.2) 100%);"></div>
        </div>

        <!-- Brand text -->
        <h1
          class="font-display text-5xl font-semibold italic tracking-tight text-studio-cream mb-3"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateY(0)' : 'translateY(10px)',
            transition: 'all 0.6s ease-out 0.4s'
          }"
        >
          Songflow
        </h1>
        <p
          class="text-studio-sand font-body text-lg"
          :style="{
            opacity: mounted ? 1 : 0,
            transition: 'opacity 0.6s ease-out 0.5s'
          }"
        >
          AI Song Automation Pipeline
        </p>
      </div>

      <!-- Login Card -->
      <div class="relative">
        <!-- Animated border glow -->
        <div class="absolute -inset-px bg-gradient-to-r from-studio-rose-500/40 via-studio-violet-500/20 to-studio-rose-500/40 rounded-3xl blur-sm opacity-60 animate-gradient-shift" style="background-size: 200% 200%;"></div>

        <!-- Card content -->
        <div
          class="relative bg-studio-black/80 backdrop-blur-xl rounded-3xl p-8 border border-studio-graphite/30"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateY(0)' : 'translateY(20px)',
            transition: 'all 0.6s ease-out 0.3s'
          }"
        >
          <!-- Card header -->
          <div class="flex items-center gap-3 mb-8">
            <div class="w-1 h-6 rounded-full bg-gradient-to-b from-studio-rose-500 to-studio-violet-500"></div>
            <h2 class="font-display text-2xl font-semibold text-studio-cream">Sign In</h2>
          </div>

          <!-- Error Message -->
          <Transition name="slide-fade">
            <div
              v-if="errorMessage"
              class="mb-6 p-4 rounded-xl bg-studio-error-dim/30 border border-studio-error/30 flex items-start gap-3"
            >
              <div class="w-5 h-5 rounded-full bg-studio-error/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg class="w-3 h-3 text-studio-error" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <p class="text-sm text-studio-error">{{ errorMessage }}</p>
            </div>
          </Transition>

          <!-- Login Form -->
          <form @submit.prevent="handleLogin" class="space-y-6">
            <!-- Username field -->
            <div
              :style="{
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
                transition: 'all 0.5s ease-out 0.5s'
              }"
            >
              <label for="username" class="input-label">Username</label>
              <div class="input-group">
                <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <input
                  id="username"
                  v-model="credentials.username"
                  type="text"
                  required
                  autocomplete="username"
                  placeholder="Enter your username"
                  class="input-field with-icon"
                  :disabled="isLoading"
                />
              </div>
            </div>

            <!-- Password field -->
            <div
              :style="{
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
                transition: 'all 0.5s ease-out 0.55s'
              }"
            >
              <label for="password" class="input-label">Password</label>
              <div class="input-group">
                <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <input
                  id="password"
                  v-model="credentials.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  autocomplete="current-password"
                  placeholder="Enter your password"
                  class="input-field with-icon pr-12"
                  :disabled="isLoading"
                />
                <!-- Password visibility toggle -->
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-studio-slate hover:text-studio-cream transition-colors"
                >
                  <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Remember Me -->
            <div
              class="flex items-center justify-between"
              :style="{
                opacity: mounted ? 1 : 0,
                transition: 'opacity 0.5s ease-out 0.6s'
              }"
            >
              <label class="flex items-center gap-3 cursor-pointer group">
                <div class="relative">
                  <input
                    id="remember"
                    v-model="rememberMe"
                    type="checkbox"
                    class="sr-only peer"
                  />
                  <div class="w-5 h-5 rounded-md border border-studio-graphite/60 bg-studio-charcoal/50 peer-checked:bg-studio-rose-500/20 peer-checked:border-studio-rose-500/50 transition-all"></div>
                  <svg
                    class="absolute top-0.5 left-0.5 w-4 h-4 text-studio-rose-500 opacity-0 peer-checked:opacity-100 transition-opacity"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-sm text-studio-sand group-hover:text-studio-cream transition-colors">Remember me</span>
              </label>

              <a href="#" class="text-sm text-studio-rose-400 hover:text-studio-rose-300 transition-colors">
                Forgot password?
              </a>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full btn btn-lg relative overflow-hidden group"
              :class="[
                isLoading
                  ? 'bg-studio-charcoal text-studio-slate cursor-not-allowed'
                  : 'bg-gradient-to-r from-studio-rose-600 to-studio-rose-500 text-white shadow-lg shadow-studio-rose-500/25 hover:shadow-glow-rose'
              ]"
              :style="{
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateY(0)' : 'translateY(10px)',
                transition: 'all 0.5s ease-out 0.65s'
              }"
            >
              <!-- Shimmer effect -->
              <div
                v-if="!isLoading"
                class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"
              ></div>

              <!-- Button content -->
              <span class="relative flex items-center justify-center gap-2">
                <svg v-if="isLoading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                {{ isLoading ? 'Signing in...' : 'Sign In' }}
              </span>
            </button>
          </form>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="text-center mt-8"
        :style="{
          opacity: mounted ? 1 : 0,
          transition: 'opacity 0.5s ease-out 0.8s'
        }"
      >
        <div class="flex items-center justify-center gap-2 text-sm text-studio-stone">
          <svg class="w-4 h-4 text-studio-success" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Protected by enterprise-grade security
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Animation state
const mounted = ref(false)

onMounted(() => {
  setTimeout(() => {
    mounted.value = true
  }, 100)
})

// Form state
const credentials = reactive({
  username: '',
  password: ''
})

const rememberMe = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

// Handle login submission
const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    await authStore.login(credentials.username, credentials.password)
    router.push('/')
  } catch (error: any) {
    errorMessage.value = error.message || 'Invalid username or password. Please try again.'
    credentials.password = ''
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Slide fade transition for error message */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
