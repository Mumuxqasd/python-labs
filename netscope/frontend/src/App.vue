<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { api, connection } from "./api";
const router = useRouter(),
  user = ref(null),
  ready = ref(false),
  username = ref(""),
  password = ref(""),
  error = ref(""),
  busy = ref(false);
onMounted(async () => {
  try {
    await api("auth/csrf/");
    user.value = await api("auth/me/");
  } catch (e) {
    if (e.status !== 403 && e.status !== 401) error.value = e.message;
  } finally {
    ready.value = true;
  }
});
async function signIn() {
  busy.value = true;
  error.value = "";
  try {
    await api("auth/csrf/");
    user.value = await api("auth/login/", {
      method: "POST",
      body: { username: username.value, password: password.value },
    });
    password.value = "";
    router.push("/");
  } catch (e) {
    error.value = e.message;
  } finally {
    busy.value = false;
  }
}
async function signOut() {
  try {
    await api("auth/logout/", { method: "POST" });
    user.value = null;
  } catch (e) {
    error.value = e.message;
  }
}
</script>
<template>
  <div v-if="!ready" class="loading full">Подключение к NetScope…</div>
  <div v-else-if="!user" class="login-shell">
    <form class="login card" @submit.prevent="signIn">
      <div class="brand-mark">N<span>↗</span></div>
      <div class="eyebrow">NETWORK OBSERVABILITY</div>
      <h1>NetScope<span class="green">.</span></h1>
      <p class="muted">Ваша сеть под наблюдением</p>
      <label
        >Логин<input
          v-model="username"
          required
          autocomplete="username"
          placeholder="admin" /></label
      ><label
        >Пароль<input
          v-model="password"
          required
          type="password"
          autocomplete="current-password"
          placeholder="Введите пароль"
      /></label>
      <div v-if="error" class="error" role="alert">{{ error }}</div>
      <button class="primary" :disabled="busy">
        {{ busy ? "Входим…" : "Войти в систему →" }}</button
      ><small class="muted">Локальный мониторинг · Версия 1.0</small>
    </form>
  </div>
  <div v-else class="shell">
    <aside>
      <RouterLink to="/" class="brand"
        >◈ NetScope<span class="green">.</span></RouterLink
      >
      <div class="eyebrow nav-label">РАБОЧЕЕ ПРОСТРАНСТВО</div>
      <nav>
        <RouterLink to="/">◫ <span>Обзор</span></RouterLink
        ><RouterLink to="/nodes">▦ <span>Узлы сети</span></RouterLink
        ><RouterLink to="/history">◷ <span>История</span></RouterLink
        ><RouterLink to="/about">ⓘ <span>О проекте</span></RouterLink>
      </nav>
      <div class="sidebar-bottom">
        <div class="local"><i class="dot UP"></i> Локальная среда</div>
        <p>Один администратор.<br />Полный контроль сети.</p>
        <button class="ghost" @click="signOut">
          {{ user.username }} · Выйти ↗
        </button>
      </div>
    </aside>
    <main>
      <header class="topbar">
        <span>Рабочая область <span class="muted">/ NetScope</span></span
        ><span class="live"
          ><i class="dot" :class="connection.online ? 'UP' : 'DOWN'"></i
          >{{
            connection.online
              ? "Автообновление · 5 секунд"
              : "Нет связи с сервером"
          }}</span
        >
      </header>
      <div v-if="!connection.online" class="error banner" role="alert">
        Нет связи с сервером. Данные могут быть устаревшими; подключение
        повторяется автоматически.
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <div class="content"><RouterView /></div>
    </main>
  </div>
</template>
