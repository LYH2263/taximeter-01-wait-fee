<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template>
  <div class="page"><h1>记录</h1><table><tr v-for="h in items" :key="h.id"><td>#{{ h.id }}</td><td>{{ h.kind }}</td></tr></table></div>
</template>
