import { reactive, onMounted, onUnmounted, ref } from "vue";
export const connection = reactive({ online: true, error: "" });
function cookie(name) {
  return (
    document.cookie
      .split("; ")
      .find((s) => s.startsWith(name + "="))
      ?.split("=")
      .slice(1)
      .join("=") || ""
  );
}
export function errorText(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(errorText).join("; ");
  return Object.entries(value || {})
    .map(([k, v]) => `${k}: ${errorText(v)}`)
    .join(" · ");
}
export async function api(path, options = {}) {
  let response;
  try {
    response = await fetch("/api/" + path, {
      credentials: "same-origin",
      signal: AbortSignal.timeout(8000),
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": decodeURIComponent(cookie("csrftoken")),
        ...options.headers,
      },
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    connection.online = false;
    throw new Error("Нет связи с сервером");
  }
  if (response.status >= 500) {
    connection.online = false;
    throw new Error("Нет связи с сервером. Повторяем подключение…");
  }
  connection.online = true;
  const data =
    response.status === 204
      ? null
      : await response
          .json()
          .catch(() => ({ detail: "Не удалось обработать ответ сервера" }));
  if (!response.ok) {
    const error = new Error(errorText(data));
    error.status = response.status;
    throw error;
  }
  return data;
}
export async function all(path) {
  let result = [],
    next = path + (path.includes("?") ? "&" : "?") + "page_size=200";
  while (next) {
    let data = await api(next);
    result.push(...data.results);
    next = data.next ? data.next.split("/api/")[1] : null;
  }
  return result;
}
export function usePolling(load) {
  const loading = ref(true),
    error = ref("");
  let timer,
    busy = false,
    disposed = false;
  const refresh = async () => {
    if (busy || disposed) return;
    busy = true;
    try {
      await load();
      if (!disposed) error.value = "";
    } catch (e) {
      if (!disposed) error.value = e.message;
    } finally {
      busy = false;
      loading.value = false;
    }
  };
  onMounted(() => {
    refresh();
    timer = setInterval(refresh, 5000);
  });
  onUnmounted(() => {
    disposed = true;
    clearInterval(timer);
  });
  return { loading, error, refresh };
}
export const formatTime = (value) =>
  value ? new Date(value).toLocaleString("ru-RU") : "—";
export const latency = (value) =>
  value == null ? "—" : `${Number(value).toFixed(1)} мс`;
export const statusText = {
  UP: "Доступен",
  DOWN: "Недоступен",
  UNKNOWN: "Нет данных",
  PAUSED: "Приостановлен",
};
export function query(values) {
  return new URLSearchParams(
    Object.fromEntries(
      Object.entries(values).filter(([, v]) => v !== "" && v != null),
    ),
  ).toString();
}
