<script setup>
import { statusText } from "../api";
defineProps({ status: { type: String, default: "UNKNOWN" } });
</script>
<template>
  <span class="badge" :class="status"
    ><i class="dot" :class="status"></i>{{ statusText[status] || status }}</span
  >
</template>
