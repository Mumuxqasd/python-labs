<script setup>
import StatusBadge from "./StatusBadge.vue";
import { formatTime, latency } from "../api";
defineProps({ rows: { type: Array, default: () => [] } });
</script>
<template>
  <div class="table-scroll">
    <table>
      <thead>
        <tr>
          <th>Время</th>
          <th>Узел / проверка</th>
          <th>Статус</th>
          <th>Задержка</th>
          <th>Подробности</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td class="mono">{{ formatTime(r.finished_at) }}</td>
          <td>
            <RouterLink :to="'/checks/' + r.check">{{ r.node_name }}</RouterLink
            ><small class="muted block"
              >{{ r.check_name }} · {{ r.check_type }}</small
            >
          </td>
          <td><StatusBadge :status="r.status" /></td>
          <td class="mono">{{ latency(r.latency_ms) }}</td>
          <td class="detail-cell muted">
            {{
              r.error_message ||
              (r.http_status ? "HTTP " + r.http_status : "Успешно")
            }}
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="5" class="empty">Пока нет измерений</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
