<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ title }}</h1>
        <p class="page-subtitle">{{ subtitle }}</p>
      </div>
    </div>
    <n-card size="small">
      <n-empty description="页面骨架已就绪" />
    </n-card>
  </section>
</template>

<script setup lang="ts">
import { NCard, NEmpty } from 'naive-ui'

defineProps<{
  title: string
  subtitle: string
}>()
</script>

