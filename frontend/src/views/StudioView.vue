<script setup lang="ts">
import { ref, computed, markRaw, defineAsyncComponent, onMounted } from 'vue'
import { useStudioStore } from '@/stores/studio'

const store = useStudioStore()
const mounted = ref(false)

// SVG icon paths for each step
const stepIcons = {
  selectSong: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3',
  coverArt: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
  videoSettings: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z',
  lyricSync: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  metadata: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  preview: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
  publish: 'M5 3l14 9-14 9V3z'
}

const steps = [
  { num: 1, name: 'Source', shortName: 'SRC', iconPath: stepIcons.selectSong, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/SongSelectStep.vue'))) },
  { num: 2, name: 'Artwork', shortName: 'ART', iconPath: stepIcons.coverArt, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/CoverArtStep.vue'))) },
  { num: 3, name: 'Video', shortName: 'VID', iconPath: stepIcons.videoSettings, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/VideoSettingsStep.vue'))) },
  { num: 4, name: 'Sync', shortName: 'SYN', iconPath: stepIcons.lyricSync, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/LyricSyncStep.vue'))) },
  { num: 5, name: 'Meta', shortName: 'MTA', iconPath: stepIcons.metadata, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/MetadataStep.vue'))) },
  { num: 6, name: 'Preview', shortName: 'PRV', iconPath: stepIcons.preview, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/PreviewStep.vue'))) },
  { num: 7, name: 'Export', shortName: 'OUT', iconPath: stepIcons.publish, component: markRaw(defineAsyncComponent(() => import('@/components/studio/steps/PublishStep.vue'))) },
]

const totalSteps = steps.length
const currentStep = ref(1)
const currentStepData = computed(() => steps[currentStep.value - 1])
const progressPercent = computed(() => Math.round(((currentStep.value - 1) / (totalSteps - 1)) * 100))

function canProceed() {
  if (currentStep.value === 1) return !!store.selectedSong
  if (currentStep.value === 2) return !!store.cover.path || store.cover.type === 'skip'
  if (currentStep.value === 3) return true
  if (currentStep.value === 4) return true
  if (currentStep.value === 5) return store.metadata.title.length > 0
  if (currentStep.value === 6) return !!store.previewUrl
  return true
}

function nextStep() {
  if (currentStep.value < totalSteps && canProceed()) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

function goToStep(stepNum: number) {
  if (stepNum <= currentStep.value || canProceed()) {
    currentStep.value = stepNum
  }
}

function getStepStatus(stepNum: number): 'completed' | 'active' | 'pending' {
  if (stepNum < currentStep.value) return 'completed'
  if (stepNum === currentStep.value) return 'active'
  return 'pending'
}

onMounted(() => {
  setTimeout(() => {
    mounted.value = true
  }, 100)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <header
      class="flex flex-col lg:flex-row lg:items-end justify-between gap-6"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(-20px)',
        transition: 'all 0.6s ease-out'
      }"
    >
      <div>
        <div class="flex items-center gap-3 mb-3">
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-studio-rose-500 to-studio-amber"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Production</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Video Studio
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Create and publish your music video through the production pipeline.
        </p>
      </div>

      <!-- Status indicator -->
      <div class="flex items-center gap-4 self-start lg:self-auto">
        <div class="flex items-center gap-3 px-5 py-3 rounded-2xl bg-studio-black/60 backdrop-blur-sm border border-studio-graphite/40">
          <div class="led-indicator" :class="currentStep === totalSteps ? 'green' : 'amber'" style="animation: led-pulse 2s ease-in-out infinite;"></div>
          <span class="text-sm font-medium text-studio-sand">
            {{ currentStep === totalSteps ? 'Ready to Export' : 'In Production' }}
          </span>
        </div>

        <!-- VU Meter Progress -->
        <div class="hidden sm:flex items-center gap-1 px-3 py-2 rounded-xl bg-studio-black/60 border border-studio-graphite/40">
          <div
            v-for="i in 7"
            :key="i"
            class="w-1.5 h-6 rounded-sm transition-all duration-300"
            :class="[
              i <= currentStep
                ? i <= 5 ? 'bg-studio-vu-green shadow-[0_0_6px_rgba(74,222,128,0.5)]'
                  : i === 6 ? 'bg-studio-vu-yellow shadow-[0_0_6px_rgba(250,204,21,0.5)]'
                  : 'bg-studio-vu-red shadow-[0_0_6px_rgba(239,68,68,0.5)]'
                : 'bg-studio-charcoal'
            ]"
          ></div>
        </div>
      </div>
    </header>

    <!-- Channel Strip Progress -->
    <div
      class="card-static overflow-hidden"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.1s'
      }"
    >
      <!-- Progress bar background -->
      <div class="absolute top-0 left-0 h-1 bg-studio-charcoal w-full">
        <div
          class="h-full bg-gradient-to-r from-studio-rose-500 via-studio-amber to-studio-gold transition-all duration-500 ease-smooth"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>

      <div class="flex items-stretch -mx-6 -mb-6 mt-2">
        <button
          v-for="(step, index) in steps"
          :key="step.num"
          @click="goToStep(step.num)"
          class="channel-strip flex-1 relative group"
          :class="{
            'channel-active': currentStep === step.num,
            'channel-completed': currentStep > step.num,
            'channel-pending': currentStep < step.num,
            'cursor-pointer': currentStep >= step.num || canProceed(),
            'cursor-not-allowed': currentStep < step.num && !canProceed()
          }"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateY(0)' : 'translateY(10px)',
            transition: `all 0.4s ease-out ${0.1 + index * 0.05}s`
          }"
        >
          <!-- Channel content -->
          <div class="px-2 py-4 flex flex-col items-center gap-3 border-r border-studio-graphite/30 last:border-r-0 transition-all duration-300"
               :class="currentStep === step.num ? 'bg-studio-rose-500/5' : 'hover:bg-studio-graphite/20'">

            <!-- LED indicator -->
            <div
              class="w-2 h-2 rounded-full transition-all duration-300"
              :class="{
                'bg-studio-success shadow-[0_0_8px_rgba(74,222,128,0.6)]': currentStep > step.num,
                'bg-studio-rose-500 shadow-[0_0_8px_rgba(204,122,90,0.6)] animate-pulse': currentStep === step.num,
                'bg-studio-slate/30': currentStep < step.num
              }"
            ></div>

            <!-- Icon knob -->
            <div
              class="w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center transition-all duration-300 border-2"
              :class="{
                'bg-gradient-to-br from-studio-rose-500 to-studio-amber text-studio-void border-studio-rose-400 shadow-lg shadow-studio-rose-500/30 scale-110': currentStep === step.num,
                'bg-studio-charcoal/80 text-studio-amber border-studio-amber/40': currentStep > step.num,
                'bg-studio-charcoal/40 text-studio-slate border-studio-graphite/40': currentStep < step.num
              }"
            >
              <svg v-if="currentStep > step.num" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="step.iconPath" />
              </svg>
            </div>

            <!-- Fader track visualization -->
            <div class="w-1 h-8 rounded-full bg-studio-charcoal/60 overflow-hidden">
              <div
                class="w-full rounded-full transition-all duration-500"
                :class="{
                  'bg-gradient-to-t from-studio-rose-500 to-studio-amber h-full': currentStep >= step.num,
                  'bg-studio-graphite h-0': currentStep < step.num
                }"
              ></div>
            </div>

            <!-- Channel label -->
            <div class="text-center">
              <p
                class="text-[10px] font-mono uppercase tracking-wider transition-colors duration-300"
                :class="{
                  'text-studio-rose-400': currentStep === step.num,
                  'text-studio-amber': currentStep > step.num,
                  'text-studio-slate': currentStep < step.num
                }"
              >{{ step.shortName }}</p>
              <p
                class="text-xs font-medium mt-0.5 hidden md:block transition-colors duration-300"
                :class="{
                  'text-studio-cream': currentStep === step.num,
                  'text-studio-sand': currentStep > step.num,
                  'text-studio-slate': currentStep < step.num
                }"
              >{{ step.name }}</p>
            </div>

            <!-- Step number -->
            <div
              class="text-[9px] font-mono px-1.5 py-0.5 rounded transition-colors duration-300"
              :class="{
                'bg-studio-rose-500/20 text-studio-rose-400': currentStep === step.num,
                'bg-studio-charcoal text-studio-sand': currentStep !== step.num
              }"
            >{{ step.num }}</div>
          </div>
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Step Info Card -->
      <div
        class="lg:col-span-1"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
          transition: 'all 0.5s ease-out 0.2s'
        }"
      >
        <div class="stat-card rose h-full">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-studio-rose-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-studio-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="currentStepData.iconPath" />
              </svg>
            </div>
            <div>
              <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider">Current Step</p>
              <p class="text-lg font-display font-semibold text-studio-cream">{{ currentStepData.name }}</p>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-studio-slate">Progress</span>
              <span class="text-studio-cream font-mono">{{ currentStep }}/{{ totalSteps }}</span>
            </div>
            <div class="vu-meter">
              <div class="vu-meter-fill" :style="{ width: `${progressPercent}%` }"></div>
            </div>
            <p class="text-xs text-studio-slate">
              {{ progressPercent }}% complete
            </p>
          </div>

          <!-- Quick actions -->
          <div class="mt-6 pt-4 border-t border-studio-graphite/30 space-y-2">
            <button
              v-if="currentStep > 1"
              @click="prevStep"
              class="w-full px-4 py-2 text-xs font-condensed uppercase tracking-wider text-studio-sand bg-studio-charcoal/50 rounded-lg hover:bg-studio-charcoal transition-colors flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>
            <button
              v-if="currentStep < totalSteps"
              @click="nextStep"
              :disabled="!canProceed()"
              class="w-full px-4 py-2 text-xs font-condensed uppercase tracking-wider rounded-lg transition-all flex items-center justify-center gap-2"
              :class="canProceed()
                ? 'bg-gradient-to-r from-studio-rose-500 to-studio-amber text-studio-void hover:shadow-lg hover:shadow-studio-rose-500/20'
                : 'bg-studio-charcoal/30 text-studio-slate/50 cursor-not-allowed'"
            >
              Next
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div
        class="lg:col-span-3"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.25s'
        }"
      >
        <div class="card-static min-h-[450px] flex flex-col">
          <!-- Content Header -->
          <div class="flex items-center justify-between mb-6 pb-4 border-b border-studio-graphite/30">
            <div class="flex items-center gap-3">
              <div class="w-2 h-2 rounded-full bg-studio-rose-500" style="box-shadow: 0 0 8px rgba(204, 122, 90, 0.5);"></div>
              <h2 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">
                {{ currentStepData.name }}
              </h2>
            </div>
            <span class="text-xs font-mono text-studio-slate bg-studio-charcoal/50 px-3 py-1 rounded-lg">
              STEP {{ currentStep.toString().padStart(2, '0') }}
            </span>
          </div>

          <!-- Dynamic Step Component -->
          <div class="flex-1">
            <Suspense>
              <component :is="currentStepData.component" />
              <template #fallback>
                <div class="flex-1 flex items-center justify-center h-full">
                  <div class="text-center">
                    <div class="relative w-16 h-16 mx-auto mb-4">
                      <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
                      <div class="absolute inset-0 rounded-full border-4 border-studio-rose-500 border-t-transparent animate-spin"></div>
                    </div>
                    <p class="text-studio-sand font-medium">Loading...</p>
                  </div>
                </div>
              </template>
            </Suspense>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div
      v-if="store.error"
      class="p-4 rounded-xl bg-studio-error/10 border border-studio-error/30"
      :style="{
        opacity: mounted ? 1 : 0,
        transition: 'opacity 0.3s ease-out'
      }"
    >
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-studio-error/20 flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-studio-error text-sm font-medium flex-1">{{ store.error }}</p>
        <button
          @click="store.error = null"
          class="p-2 hover:bg-studio-error/20 rounded-lg transition-colors"
        >
          <svg class="w-4 h-4 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* LED pulse animation */
@keyframes led-pulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 8px currentColor;
  }
  50% {
    opacity: 0.6;
    box-shadow: 0 0 4px currentColor;
  }
}

/* Channel strip hover effects */
.channel-strip:hover .channel-pending {
  opacity: 0.7;
}

/* Smooth transitions for channel content */
.channel-strip > div {
  min-height: 180px;
}
</style>
