<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
const route = useRoute()
const trip = ref(null)
const fare = ref(null)
const wait_min = ref(0)
const load = async () => {
  trip.value = await getJSON(`/api/trips/${route.params.id}`)
  await recalc()
}
// 只读试算：persist=false，不新增 calc_runs 记录
const recalc = async () => {
  fare.value = await postJSON('/api/fare', { distance_km: trip.value.distance_km, slow_min: trip.value.slow_min, wait_min: wait_min.value, night: !!trip.value.night, trip_id: trip.value.id, persist: false })
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template>
  <div class="page" v-if="trip"><h1>{{ trip.label }}</h1>
    <div class="panel">
      <label>等候分钟（只读试算，不增记录） <input type="number" min="0" v-model.number="wait_min" @change="recalc" /></label>
      <button @click="recalc">重算</button>
    </div>
    <p class="hero-num">¥{{ fare?.total }}</p>
    <p>起步 {{ fare?.start }} · 里程 {{ fare?.mileage }} · 低速 {{ fare?.slow_fee }} · 等候费 {{ fare?.wait_fee }}</p>
    <p class="muted" v-if="fare">
      等候 {{ fare.wait_min }} 分钟，计入 {{ fare.wait_billable_min }} 分钟
      <template v-if="fare.wait_rule_id">（规则 #{{ fare.wait_rule_id }} {{ fare.wait_rule_label }}）</template>
    </p>
  </div>
</template>
