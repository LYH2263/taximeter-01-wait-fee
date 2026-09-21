<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, patchJSON } from '../api'

const t = ref(null)
const items = ref([])
const free_min = ref(5)
const per_min_price = ref(1.0)
const active = ref(false)
const error = ref('')

const load = async () => {
  t.value = await getJSON('/api/tariff')
  items.value = (await getJSON('/api/wait-rules')).items
}
onMounted(load)

const create = async () => {
  error.value = ''
  try {
    await postJSON('/api/wait-rules', {
      free_min: Number(free_min.value),
      per_min_price: Number(per_min_price.value),
      active: active.value,
    })
    await load()
  } catch (e) {
    error.value = JSON.parse(e.message)?.detail || e.message
  }
}

const save = async (x) => {
  error.value = ''
  try {
    await patchJSON(`/api/wait-rules/${x.id}`, {
      free_min: Number(x.free_min),
      per_min_price: Number(x.per_min_price),
    })
    await load()
  } catch (e) {
    error.value = e.message
  }
}

const toggle = async (x) => {
  error.value = ''
  try {
    if (x.active) await postJSON(`/api/wait-rules/${x.id}/disable`)
    else await patchJSON(`/api/wait-rules/${x.id}`, { active: true })
    await load()
  } catch (e) {
    error.value = JSON.parse(e.message)?.detail || e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>运价表</h1>
    <pre v-if="t" class="panel">{{ t }}</pre>

    <h2>等候规则</h2>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="panel">
      <label>免费等候分钟 <input type="number" min="0" v-model.number="free_min" /></label>
      <label>超出后每分钟单价 <input type="number" min="0" step="0.1" v-model.number="per_min_price" /></label>
      <label><input type="checkbox" v-model="active" /> 同时启用</label>
      <button @click="create">新建规则</button>
    </div>
    <table>
      <tr><th>#</th><th>免费分钟</th><th>每分钟单价</th><th>状态</th><th></th></tr>
      <tr v-for="x in items" :key="x.id">
        <td>#{{ x.id }}</td>
        <td><input type="number" min="0" v-model.number="x.free_min" /></td>
        <td><input type="number" min="0" step="0.1" v-model.number="x.per_min_price" /></td>
        <td>{{ x.active ? '启用中' : '已停用' }}</td>
        <td>
          <button @click="save(x)">保存</button>
          <button @click="toggle(x)">{{ x.active ? '停用' : '启用' }}</button>
        </td>
      </tr>
    </table>
  </div>
</template>
