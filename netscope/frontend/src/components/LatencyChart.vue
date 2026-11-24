<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import Chart from "chart.js/auto";
import { formatTime } from "../api";
const props = defineProps({ series: { type: Array, default: () => [] } }),
  canvas = ref(null);
let chart;
function render() {
  if (!chart) return;
  chart.data.labels = props.series.map((r) => formatTime(r.finished_at));
  chart.data.datasets[0].data = props.series.map((r) =>
    r.status === "UP" ? r.latency_ms : null,
  );
  chart.data.datasets[1].data = props.series.map((r) =>
    r.status === "DOWN" ? 0 : null,
  );
  chart.update("none");
}
onMounted(() => {
  chart = new Chart(canvas.value, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Задержка, мс",
          data: [],
          borderColor: "#5cdda0",
          backgroundColor: "#5cdda010",
          fill: true,
          tension: 0.25,
          spanGaps: false,
          pointRadius: 3,
        },
        {
          label: "Ошибка (не задержка)",
          data: [],
          type: "scatter",
          borderColor: "#ff7e87",
          backgroundColor: "#ff7e87",
          pointStyle: "crossRot",
          pointRadius: 7,
          showLine: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { labels: { color: "#9aacaa", usePointStyle: true } },
        tooltip: {
          callbacks: {
            label: (ctx) =>
              ctx.datasetIndex === 1
                ? "DOWN · ошибка проверки"
                : `${ctx.parsed.y.toFixed(2)} мс`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: "#849a96", maxTicksLimit: 5 },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: "мс", color: "#849a96" },
          ticks: { color: "#849a96" },
          grid: { color: "#ffffff08" },
        },
      },
    },
  });
  render();
});
watch(() => props.series, render, { deep: true });
onBeforeUnmount(() => chart?.destroy());
</script>
<template>
  <div class="chart-wrap">
    <div v-if="!series.length" class="chart-empty muted">
      Пока нет измерений
    </div>
    <canvas
      ref="canvas"
      role="img"
      aria-label="История задержки. Ошибки отмечены крестиками и разрывами линии."
    ></canvas>
  </div>
</template>
