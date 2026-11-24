<script setup>
import { ref, watch } from "vue";
import { api, all, usePolling, latency, formatTime } from "../api";
import StatusBadge from "../components/StatusBadge.vue";
import LatencyChart from "../components/LatencyChart.vue";
import ResultTable from "../components/ResultTable.vue";
const data = ref(null),
  nodes = ref([]),
  checks = ref([]),
  selected = ref(""),
  series = ref([]);
const { error, loading, refresh } = usePolling(async () => {
  const [d, n, c] = await Promise.all([
    api("dashboard/"),
    all("nodes/"),
    all("checks/"),
  ]);
  data.value = d;
  nodes.value = n;
  checks.value = c;
  if (!selected.value && c.length) selected.value = String(c[0].id);
  if (selected.value)
    series.value = await api(`checks/${selected.value}/series/`);
  else series.value = [];
});
watch(selected, () => {
  series.value = [];
  refresh();
});
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">СЕТЬ В РЕАЛЬНОМ ВРЕМЕНИ</div>
      <h1>Обзор сети</h1>
      <p class="muted">Доступность, задержки и события в одном месте.</p>
    </div>
    <div class="worker" :class="data?.worker.running ? 'online' : ''">
      <i class="dot" :class="data?.worker.running ? 'UP' : 'UNKNOWN'"></i
      >Worker: {{ data?.worker.running ? "Работает" : "Нет данных о работе" }}
    </div>
  </div>
  <p v-if="error" class="error">{{ error }}</p>
  <p v-if="loading" class="muted">Загрузка данных…</p>
  <template v-if="data"
    ><div class="kpis">
      <article class="kpi card">
        <small>Всего узлов</small><strong>{{ data.total_nodes }}</strong
        ><span>В рабочей области</span>
      </article>
      <article class="kpi card">
        <small>Доступно</small><strong class="green">{{ data.up }}</strong
        ><span>Все проверки успешны</span>
      </article>
      <article class="kpi card">
        <small>Недоступно</small><strong class="red">{{ data.down }}</strong
        ><span>Требуют внимания</span>
      </article>
      <article class="kpi card">
        <small>Нет данных / пауза</small
        ><strong>{{ data.unknown + data.paused }}</strong
        ><span>Из них на паузе: {{ data.paused }}</span>
      </article>
      <article class="kpi card">
        <small>Инциденты</small
        ><strong :class="data.open_incidents ? 'red' : 'green'">{{
          data.open_incidents
        }}</strong
        ><span>Открыто сейчас</span>
      </article>
    </div>
    <div class="dashboard-grid">
      <section class="card chart-card">
        <div class="section-head">
          <div>
            <h2>Задержка соединения</h2>
            <small class="muted"
              >Последние 60 измерений · ошибки отмечены ×</small
            >
          </div>
          <select v-model="selected" aria-label="Проверка для графика">
            <option value="" disabled>Выберите проверку</option>
            <option v-for="c in checks" :key="c.id" :value="String(c.id)">
              {{ c.node_name }} / {{ c.name }}
            </option>
          </select>
        </div>
        <LatencyChart :series="series" />
      </section>
      <section class="card node-overview">
        <div class="section-head">
          <h2>Узлы сети</h2>
          <RouterLink to="/nodes" class="green">Все →</RouterLink>
        </div>
        <RouterLink
          v-for="n in nodes.slice(0, 5)"
          :key="n.id"
          :to="'/nodes/' + n.id"
          class="node-mini"
          ><div>
            <strong>{{ n.name }}</strong
            ><small class="muted block mono">{{ n.host }}</small>
          </div>
          <StatusBadge :status="n.status"
        /></RouterLink>
        <p v-if="!nodes.length" class="empty">
          Узлов пока нет.<br /><RouterLink to="/nodes" class="green"
            >Добавьте первый узел →</RouterLink
          >
        </p>
      </section>
    </div>
    <section class="card">
      <div class="section-head">
        <div>
          <h2>Последние проверки</h2>
          <small class="muted">Фактические результаты мониторинга</small>
        </div>
        <RouterLink to="/history" class="green">Вся история →</RouterLink>
      </div>
      <ResultTable :rows="data.latest_results" /></section
  ></template>
</template>
