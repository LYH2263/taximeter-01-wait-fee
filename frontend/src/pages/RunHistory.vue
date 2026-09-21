<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const parse = (h) => { try { return JSON.parse(h.result_json) } catch { return {} } }
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template>
  <div class="page"><h1>记录</h1>
    <table>
      <tr><th>#</th><th>类型</th><th>等候规则</th><th>等候费</th><th>应付</th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td><td>{{ h.kind }}</td>
        <td>{{ parse(h).wait_rule_id ? `#${parse(h).wait_rule_id} ${parse(h).wait_rule_label}` : '—' }}</td>
        <td>{{ parse(h).wait_fee ?? '—' }}</td>
        <td>{{ parse(h).total ?? '—' }}</td>
      </tr>
    </table>
  </div>
</template>
