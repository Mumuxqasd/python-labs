<script setup>
defineProps(["page", "count", "size"]);
defineEmits(["change"]);
</script>
<template>
  <div class="pager">
    <span class="muted"
      >{{ count }} записей · Страница {{ page }} из
      {{ Math.max(1, Math.ceil(count / size)) }}</span
    >
    <div>
      <button
        class="ghost"
        :disabled="page <= 1"
        @click="$emit('change', page - 1)"
      >
        ← Назад</button
      ><button
        class="ghost"
        :disabled="page * size >= count"
        @click="$emit('change', page + 1)"
      >
        Вперёд →
      </button>
    </div>
  </div>
</template>
