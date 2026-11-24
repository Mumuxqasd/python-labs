<script setup>
import { ref, reactive, watch } from "vue";
import { useRoute } from "vue-router";
import { api, all, usePolling, query } from "../api";
import ResultTable from "../components/ResultTable.vue";
import IncidentTable from "../components/IncidentTable.vue";
import Pager from "../components/Pager.vue";
const route = useRoute(),
  tab = ref(route.query.tab || "results"),
  nodes = ref([]),
  checks = ref([]),
  rows = ref([]),
  page = ref(1),
  count = ref(0),
  filters = reactive({
    node_id: "",
    check_id: route.query.check_id || "",
    status: "",
    state: "",
    from: "",
    to: "",
  });
function params() {
  let p = { ...filters, page: page.value };
  if (tab.value === "incidents") {
    delete p.from;
    delete p.to;
    delete p.status;
  } else {
    delete p.state;
    for (let k of ["from", "to"]) if (p[k]) p[k] = new Date(p[k]).toISOString();
  }
  return p;
}
const { error, loading, refresh } = usePolling(async () => {
  let [n, c, d] = await Promise.all([
    all("nodes/"),
    all("checks/"),
    api(tab.value + "/?" + query(params())),
  ]);
  nodes.value = n;
  checks.value = c;
  rows.value = d.results;
  count.value = d.count;
});
watch(filters, () => {
  page.value = 1;
  refresh();
});
watch(tab, () => {
  page.value = 1;
  rows.value = [];
  refresh();
});
watch(page, refresh);
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">СОБЫТИЯ И ИЗМЕРЕНИЯ</div>
      <h1>История мониторинга</h1>
      <p class="muted">
        Измерения за 7 суток. Инциденты сохраняются без ограничения.
      </p>
    </div>
  </div>
  <div class="tabs">
    <button :class="{ active: tab === 'results' }" @click="tab = 'results'">
      Результаты проверок</button
    ><button
      :class="{ active: tab === 'incidents' }"
      @click="tab = 'incidents'"
    >
      Инциденты
    </button>
  </div>
  <div class="toolbar wrap">
    <label
      >Узел<select v-model="filters.node_id">
        <option value="">Все узлы</option>
        <option v-for="n in nodes" :key="n.id" :value="n.id">
          {{ n.name }}
        </option>
      </select></label
    ><label
      >Проверка<select v-model="filters.check_id">
        <option value="">Все проверки</option>
        <option
          v-for="c in checks.filter(
            (c) =>
              !filters.node_id || String(c.node) === String(filters.node_id),
          )"
          :key="c.id"
          :value="c.id"
        >
          {{ c.node_name }} / {{ c.name }}
        </option>
      </select></label
    ><template v-if="tab === 'results'"
      ><label
        >Статус<select v-model="filters.status">
          <option value="">Все статусы</option>
          <option value="UP">Доступен</option>
          <option value="DOWN">Недоступен</option>
        </select></label
      ><label>С<input type="datetime-local" v-model="filters.from" /></label
      ><label
        >По<input
          type="datetime-local"
          v-model="filters.to" /></label></template
    ><label v-else
      >Состояние<select v-model="filters.state">
        <option value="">Все</option>
        <option value="open">Открытые</option>
        <option value="closed">Закрытые</option>
      </select></label
    >
  </div>
  <p v-if="error" class="error">{{ error }}</p>
  <p v-if="loading" class="muted">Загрузка…</p>
  <section class="card">
    <ResultTable v-if="tab === 'results'" :rows="rows" /><IncidentTable
      v-else
      :rows="rows"
    /><Pager :page="page" :count="count" :size="50" @change="page = $event" />
  </section>
</template>
