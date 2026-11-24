<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { api, all, usePolling, latency, formatTime } from "../api";
import StatusBadge from "../components/StatusBadge.vue";
import EditModal from "../components/EditModal.vue";
const route = useRoute(),
  node = ref(null),
  checks = ref([]),
  modal = ref(false),
  kind = ref("check"),
  initial = ref(null),
  notice = ref("");
const { error, refresh } = usePolling(async () => {
  [node.value, checks.value] = await Promise.all([
    api(`nodes/${route.params.id}/`),
    all(`checks/?node_id=${route.params.id}`),
  ]);
});
watch(() => route.params.id, refresh);
function edit(c, k = "check") {
  kind.value = k;
  initial.value = c;
  modal.value = true;
}
async function run(c) {
  try {
    let d = await api(`checks/${c.id}/run/`, { method: "POST" });
    notice.value = d.detail;
    refresh();
  } catch (e) {
    notice.value = e.message;
  }
}
async function toggle(c) {
  try {
    await api(`checks/${c.id}/`, {
      method: "PATCH",
      body: { enabled: !c.enabled },
    });
    refresh();
  } catch (e) {
    notice.value = e.message;
  }
}
async function remove(c) {
  if (
    !confirm(`Удалить проверку «${c.name}» вместе с её историей и инцидентами?`)
  )
    return;
  try {
    await api(`checks/${c.id}/`, { method: "DELETE" });
    refresh();
  } catch (e) {
    notice.value = e.message;
  }
}
</script>
<template>
  <RouterLink to="/nodes" class="back muted">← Узлы сети</RouterLink>
  <p v-if="error" class="error">{{ error }}</p>
  <template v-if="node"
    ><div class="page-heading">
      <div>
        <div class="eyebrow">КАРТОЧКА УЗЛА</div>
        <h1>{{ node.name }}</h1>
        <p class="mono muted">
          {{ node.host }}
          <span v-if="node.description">· {{ node.description }}</span>
        </p>
      </div>
      <div class="actions">
        <StatusBadge :status="node.status" /><button
          class="ghost"
          @click="edit(node, 'node')"
        >
          Изменить узел</button
        ><button class="primary" @click="edit(null)">＋ Проверка</button>
      </div>
    </div>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
    <div class="check-grid">
      <article v-for="c in checks" :key="c.id" class="card check-card">
        <div class="section-head">
          <span class="type-label">{{ c.check_type }}</span
          ><StatusBadge :status="c.status" />
        </div>
        <RouterLink :to="'/checks/' + c.id"
          ><h2>{{ c.name }} ↗</h2></RouterLink
        >
        <p class="muted mono">
          {{ c.check_type === "HTTP" ? c.scheme + "://" : "" }}{{ node.host
          }}{{ c.port ? ":" + c.port : ""
          }}{{ c.check_type === "HTTP" ? c.path : "" }}
        </p>
        <div class="check-metrics">
          <div>
            <small class="muted">Задержка</small
            ><strong>{{ latency(c.last_latency_ms) }}</strong>
          </div>
          <div>
            <small class="muted">Интервал / тайм-аут</small
            ><strong
              >{{ c.interval_seconds }} / {{ c.timeout_seconds }} с</strong
            >
          </div>
        </div>
        <p class="muted">Проверено: {{ formatTime(c.last_checked_at) }}</p>
        <p v-if="c.last_error" class="error">{{ c.last_error }}</p>
        <p v-if="c.manual_requested_at" class="green">Проверка запрошена…</p>
        <div class="actions">
          <button
            class="primary"
            :disabled="
              !c.enabled ||
              !node.enabled ||
              !!c.manual_requested_at ||
              c.running
            "
            @click="run(c)"
          >
            Проверить сейчас</button
          ><button class="ghost" @click="edit(c)">Изменить</button
          ><button class="ghost" @click="toggle(c)">
            {{ c.enabled ? "Пауза" : "Включить" }}</button
          ><button class="ghost danger" @click="remove(c)">Удалить</button>
        </div>
      </article>
    </div>
    <section v-if="!checks.length" class="card empty">
      У узла пока нет проверок. Добавьте ICMP, TCP, DNS или HTTP.
    </section></template
  >
  <EditModal
    v-if="modal && node"
    :kind="kind"
    :initial="initial"
    :node-id="node.id"
    @close="modal = false"
    @saved="
      modal = false;
      notice = 'Сохранено';
      refresh();
    "
  />
</template>
