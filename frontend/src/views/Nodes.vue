<script setup>
import { ref, watch } from "vue";
import { api, usePolling, query, formatTime } from "../api";
import StatusBadge from "../components/StatusBadge.vue";
import EditModal from "../components/EditModal.vue";
import Pager from "../components/Pager.vue";
const rows = ref([]),
  count = ref(0),
  page = ref(1),
  search = ref(""),
  status = ref(""),
  modal = ref(false),
  initial = ref(null),
  notice = ref("");
const { loading, error, refresh } = usePolling(async () => {
  let d = await api(
    "nodes/?" +
      query({ search: search.value, status: status.value, page: page.value }),
  );
  rows.value = d.results;
  count.value = d.count;
});
watch([search, status], () => {
  page.value = 1;
  refresh();
});
watch(page, refresh);
function edit(n) {
  initial.value = n;
  modal.value = true;
}
async function toggle(n) {
  try {
    await api(`nodes/${n.id}/`, {
      method: "PATCH",
      body: { enabled: !n.enabled },
    });
    await refresh();
  } catch (e) {
    notice.value = e.message;
  }
}
async function remove(n) {
  if (
    !confirm(
      `Удалить узел «${n.name}»? Все его проверки, история и инциденты будут удалены.`,
    )
  )
    return;
  try {
    await api(`nodes/${n.id}/`, { method: "DELETE" });
    page.value = 1;
    await refresh();
  } catch (e) {
    notice.value = e.message;
  }
}
function saved() {
  modal.value = false;
  notice.value = "Сохранено";
  refresh();
}
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">ВАША ИНФРАСТРУКТУРА</div>
      <h1>Узлы сети</h1>
      <p class="muted">Управляйте хостами и их проверками.</p>
    </div>
    <button class="primary" @click="edit(null)">＋ Добавить узел</button>
  </div>
  <div class="toolbar">
    <input
      v-model="search"
      placeholder="Поиск по имени или адресу"
      aria-label="Поиск узлов"
    /><select v-model="status" aria-label="Статус узла">
      <option value="">Все состояния</option>
      <option value="UP">Доступен</option>
      <option value="DOWN">Недоступен</option>
      <option value="UNKNOWN">Нет данных</option>
      <option value="PAUSED">Приостановлен</option>
    </select>
  </div>
  <p v-if="error" class="error">{{ error }}</p>
  <p v-if="notice" class="notice" role="status">{{ notice }}</p>
  <section class="card">
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Узел</th>
            <th>Адрес</th>
            <th>Статус</th>
            <th>Проверки</th>
            <th>Последняя активность</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="n in rows" :key="n.id">
            <td>
              <RouterLink class="strong" :to="'/nodes/' + n.id"
                >{{ n.name }} ↗</RouterLink
              ><small class="muted block">{{ n.description }}</small>
            </td>
            <td class="mono">{{ n.host }}</td>
            <td><StatusBadge :status="n.status" /></td>
            <td>{{ n.checks_count }}</td>
            <td class="muted">{{ formatTime(n.last_checked_at) }}</td>
            <td>
              <div class="actions">
                <button class="ghost" @click="edit(n)">Изменить</button
                ><button class="ghost" @click="toggle(n)">
                  {{ n.enabled ? "Пауза" : "Включить" }}</button
                ><button class="ghost danger" @click="remove(n)">
                  Удалить
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="6" class="empty">
              {{
                loading
                  ? "Загрузка…"
                  : "Узлы не найдены. Добавьте узел или измените фильтры."
              }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :page="page" :count="count" :size="50" @change="page = $event" />
  </section>
  <EditModal
    v-if="modal"
    kind="node"
    :initial="initial"
    @close="modal = false"
    @saved="saved"
  />
</template>
