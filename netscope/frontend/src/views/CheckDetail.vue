<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { api, usePolling, latency, formatTime } from "../api";
import StatusBadge from "../components/StatusBadge.vue";
import LatencyChart from "../components/LatencyChart.vue";
import ResultTable from "../components/ResultTable.vue";
import IncidentTable from "../components/IncidentTable.vue";
import EditModal from "../components/EditModal.vue";
import Pager from "../components/Pager.vue";
const route = useRoute(),
  check = ref(null),
  series = ref([]),
  results = ref([]),
  incidents = ref([]),
  page = ref(1),
  count = ref(0),
  modal = ref(false),
  notice = ref("");
const { error, refresh } = usePolling(async () => {
  let id = route.params.id;
  let [c, s, r, i] = await Promise.all([
    api(`checks/${id}/`),
    api(`checks/${id}/series/`),
    api(`results/?check_id=${id}&page=${page.value}`),
    api(`incidents/?check_id=${id}`),
  ]);
  check.value = c;
  series.value = s;
  results.value = r.results;
  count.value = r.count;
  incidents.value = i.results;
});
watch(page, refresh);
watch(
  () => route.params.id,
  () => {
    page.value = 1;
    refresh();
  },
);
async function run() {
  try {
    notice.value = (
      await api(`checks/${check.value.id}/run/`, { method: "POST" })
    ).detail;
    refresh();
  } catch (e) {
    notice.value = e.message;
  }
}
</script>
<template>
  <p v-if="error" class="error">{{ error }}</p>
  <template v-if="check"
    ><RouterLink :to="'/nodes/' + check.node" class="back muted"
      >← {{ check.node_name }}</RouterLink
    >
    <div class="page-heading">
      <div>
        <div class="eyebrow">{{ check.check_type }} · ПРОВЕРКА</div>
        <h1>{{ check.name }}</h1>
        <p class="mono muted">
          {{ check.node_host }} · Интервал {{ check.interval_seconds }} с ·
          Тайм-аут {{ check.timeout_seconds }} с
        </p>
      </div>
      <div class="actions">
        <StatusBadge :status="check.status" /><button
          class="ghost"
          @click="modal = true"
        >
          Изменить</button
        ><button
          class="primary"
          :disabled="
            check.status === 'PAUSED' ||
            !!check.manual_requested_at ||
            check.running
          "
          @click="run"
        >
          Проверить сейчас
        </button>
      </div>
    </div>
    <p v-if="notice || check.manual_requested_at" class="notice" role="status">
      {{ check.manual_requested_at ? "Проверка запрошена…" : notice }}
    </p>
    <div class="info-strip card">
      <span
        >Последняя задержка
        <b class="green">{{ latency(check.last_latency_ms) }}</b></span
      ><span
        >Последнее измерение
        <b>{{ formatTime(check.last_checked_at) }}</b></span
      ><span v-if="check.check_type === 'HTTP'"
        >{{ check.scheme }}://{{ check.node_host
        }}{{ check.port ? ":" + check.port : "" }}{{ check.path }} · ожидается
        {{ check.expected_http_status }}</span
      ><span v-else-if="check.port">Порт {{ check.port }}</span>
    </div>
    <p v-if="check.last_error" class="error">{{ check.last_error }}</p>
    <section class="card chart-card">
      <div class="section-head">
        <h2>Задержка · последние 60 измерений</h2>
        <span class="live">LIVE · 5 с</span>
      </div>
      <LatencyChart :series="series" />
    </section>
    <section class="card">
      <div class="section-head"><h2>Результаты проверки</h2></div>
      <ResultTable :rows="results" /><Pager
        :page="page"
        :count="count"
        :size="50"
        @change="page = $event"
      />
    </section>
    <section class="card">
      <div class="section-head">
        <h2>Последние инциденты</h2>
        <RouterLink
          :to="'/history?check_id=' + check.id + '&tab=incidents'"
          class="green"
          >Все →</RouterLink
        >
      </div>
      <IncidentTable :rows="incidents" />
    </section>
    <EditModal
      v-if="modal"
      kind="check"
      :initial="check"
      :node-id="check.node"
      @close="modal = false"
      @saved="
        modal = false;
        refresh();
      "
  /></template>
</template>
