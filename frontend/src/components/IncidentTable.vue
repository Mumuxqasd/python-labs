<script setup>
import { formatTime } from "../api";
defineProps({ rows: { type: Array, default: () => [] } });
function duration(s) {
  return s >= 3600
    ? `${Math.floor(s / 3600)} ч ${Math.floor((s % 3600) / 60)} мин`
    : s >= 60
      ? `${Math.floor(s / 60)} мин ${s % 60} с`
      : `${s} с`;
}
</script>
<template>
  <div class="table-scroll">
    <table>
      <thead>
        <tr>
          <th>Проверка</th>
          <th>Начало / конец</th>
          <th>Длительность</th>
          <th>Состояние</th>
          <th>Последняя ошибка</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>
            <RouterLink :to="'/checks/' + r.check">{{ r.node_name }}</RouterLink
            ><small class="muted block">{{ r.check_name }}</small>
          </td>
          <td>
            {{ formatTime(r.started_at)
            }}<small class="muted block">{{ formatTime(r.ended_at) }}</small>
          </td>
          <td>{{ duration(r.duration_seconds) }}</td>
          <td>
            <span class="badge" :class="r.ended_at ? 'UNKNOWN' : 'DOWN'">{{
              r.ended_at ? "Закрыт" : "Открыт"
            }}</span
            ><small class="muted block">{{
              r.close_reason === "RECOVERED"
                ? "Восстановлено"
                : r.close_reason === "STOPPED"
                  ? "Мониторинг остановлен"
                  : ""
            }}</small>
          </td>
          <td class="detail-cell muted">{{ r.last_error }}</td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="5" class="empty">Инцидентов нет</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
