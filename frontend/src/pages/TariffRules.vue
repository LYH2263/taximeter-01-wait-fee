<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'

const t = ref(null)
const rules = ref([])
const err = ref('')
const form = ref({ label: '标准等候', free_min: 3, per_min: 0.5, active: true })

const showErr = (e) => {
  try { err.value = JSON.parse(e.message).detail || e.message } catch { err.value = e.message }
}
const load = async () => {
  t.value = await getJSON('/api/tariff')
  rules.value = (await getJSON('/api/wait-fee/rules')).items
}
const create = async () => {
  err.value = ''
  try {
    await postJSON('/api/wait-fee/rules', form.value)
    await load()
  } catch (e) { showErr(e) }
}
const save = async (r) => {
  err.value = ''
  try {
    await putJSON(`/api/wait-fee/rules/${r.id}`, { label: r.label, free_min: r.free_min, per_min: r.per_min })
    await load()
  } catch (e) { showErr(e) }
}
const toggle = async (r) => {
  err.value = ''
  try {
    if (r.active) await postJSON(`/api/wait-fee/rules/${r.id}/deactivate`, {})
    else await putJSON(`/api/wait-fee/rules/${r.id}`, { active: true })
    await load()
  } catch (e) { showErr(e) }
}
onMounted(load)
</script>
<template>
  <div class="page"><h1>运价表</h1>
    <div class="panel">
      起步 ¥{{ t?.start_price }}（含 {{ t?.start_include_km }}km）· 每公里 ¥{{ t?.per_km }} · 低速每分钟 ¥{{ t?.per_slow_min }} · 夜间系数 ×{{ t?.night_factor }}
    </div>

    <h2>等候规则</h2>
    <p class="muted">免费等候分钟不得为负，每分钟单价必须为正；同一时刻只允许一条启用规则。</p>
    <div class="panel">
      <label>标识 <input v-model="form.label" /></label>
      <label>免费分钟 <input type="number" min="0" v-model.number="form.free_min" /></label>
      <label>每分钟单价 <input type="number" min="0.01" step="0.01" v-model.number="form.per_min" /></label>
      <label><input type="checkbox" v-model="form.active" /> 启用</label>
      <button @click="create">创建</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <table>
      <tr><th>#</th><th>标识</th><th>免费分钟</th><th>每分钟单价</th><th>状态</th><th></th></tr>
      <tr v-for="r in rules" :key="r.id">
        <td>{{ r.id }}</td>
        <td><input v-model="r.label" /></td>
        <td><input type="number" min="0" v-model.number="r.free_min" /></td>
        <td><input type="number" min="0.01" step="0.01" v-model.number="r.per_min" /></td>
        <td>{{ r.active ? '启用' : '停用' }}</td>
        <td>
          <button @click="save(r)">保存</button>
          <button @click="toggle(r)">{{ r.active ? '停用' : '启用' }}</button>
        </td>
      </tr>
    </table>
  </div>
</template>
