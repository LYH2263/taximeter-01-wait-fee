<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const distance_km = ref(8)
const slow_min = ref(3)
const wait_min = ref(0)
const night = ref(false)
const out = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''
  try {
    out.value = await postJSON('/api/fare', { distance_km: distance_km.value, slow_min: slow_min.value, wait_min: wait_min.value, night: night.value, persist: true })
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>打表试算</h1>
    <div class="panel">
      <label>公里 <input type="number" min="0" v-model.number="distance_km" /></label>
      <label>低速分钟 <input type="number" min="0" v-model.number="slow_min" /></label>
      <label>等候分钟 <input type="number" min="0" v-model.number="wait_min" /></label>
      <label><input type="checkbox" v-model="night" /> 夜间</label>
      <button @click="run">计算</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <template v-if="out">
      <p class="hero-num">¥{{ out.total }}</p>
      <p>起步 {{ out.start }} · 里程 {{ out.mileage }} · 低速 {{ out.slow_fee }} · 等候费 {{ out.wait_fee }}</p>
      <p class="muted">
        等候 {{ out.wait_min }} 分钟，计入 {{ out.wait_billable_min }} 分钟
        <template v-if="out.wait_rule_id">（规则 #{{ out.wait_rule_id }} {{ out.wait_rule_label }}）</template>
        <template v-else>（无启用等候规则，等候费为 0）</template>
      </p>
    </template>
  </div>
</template>
