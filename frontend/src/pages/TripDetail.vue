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
  await calc()
}
const calc = async () => {
  fare.value = await postJSON('/api/fare', {
    distance_km: trip.value.distance_km,
    slow_min: trip.value.slow_min,
    wait_min: wait_min.value,
    night: !!trip.value.night,
    trip_id: trip.value.id,
    persist: false,
  })
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template>
  <div class="page" v-if="trip"><h1>{{ trip.label }}</h1>
    <p class="hero-num">¥{{ fare?.total }}</p>
    <p>起步 {{ fare?.start }} · 里程 {{ fare?.mileage }} · 低速 {{ fare?.slow_fee }}</p>
    <div class="panel">
      <label>等候分钟（只读试算，不留记录） <input type="number" min="0" v-model.number="wait_min" @change="calc" /></label>
      <p v-if="fare">计入 {{ fare.charged_min }} 分钟，等候费 {{ fare.wait_fee }}
        <span v-if="fare.wait_rule_id">（规则 #{{ fare.wait_rule_id }}）</span>
      </p>
    </div>
  </div>
</template>
