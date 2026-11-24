<script setup>
import { reactive, ref, onMounted, onBeforeUnmount } from "vue";
import { api } from "../api";
const props = defineProps({
  kind: String,
  initial: Object,
  nodeId: [Number, String],
});
const emit = defineEmits(["close", "saved"]);
const isNode = props.kind === "node";
const defaults = isNode
  ? { name: "", host: "", description: "", enabled: true }
  : {
      name: "",
      check_type: "TCP",
      port: 80,
      scheme: "http",
      path: "/",
      expected_http_status: 200,
      interval_seconds: 10,
      timeout_seconds: 3,
      enabled: true,
      node: Number(props.nodeId),
    };
const form = reactive({ ...defaults, ...props.initial }),
  error = ref(""),
  busy = ref(false),
  dialog = ref(null);
function escape(e) {
  if (e.key === "Escape" && !busy.value) emit("close");
}
onMounted(() => {
  document.addEventListener("keydown", escape);
  dialog.value?.focus();
});
onBeforeUnmount(() => document.removeEventListener("keydown", escape));
async function save() {
  busy.value = true;
  error.value = "";
  let fields = isNode
    ? ["name", "host", "description", "enabled"]
    : [
        "name",
        "node",
        "check_type",
        "port",
        "scheme",
        "path",
        "expected_http_status",
        "interval_seconds",
        "timeout_seconds",
        "enabled",
      ];
  const body = Object.fromEntries(fields.map((k) => [k, form[k]]));
  if (!isNode) {
    if (!["TCP", "HTTP"].includes(form.check_type)) body.port = null;
    if (form.check_type !== "HTTP") {
      body.scheme = "";
      body.path = "";
      body.expected_http_status = null;
    } else if (body.port === "") body.port = null;
  }
  try {
    await api(
      `${isNode ? "nodes" : "checks"}/${props.initial?.id ? props.initial.id + "/" : ""}`,
      { method: props.initial?.id ? "PATCH" : "POST", body },
    );
    emit("saved");
  } catch (e) {
    error.value = e.message;
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <div class="modal-backdrop" @click.self="!busy && $emit('close')">
    <section
      ref="dialog"
      class="modal card"
      role="dialog"
      aria-modal="true"
      tabindex="-1"
      aria-labelledby="modal-title"
    >
      <div class="section-head">
        <h2 id="modal-title">
          {{ initial?.id ? "Редактирование" : "Добавление" }}
          {{ isNode ? "узла" : "проверки" }}
        </h2>
        <button
          type="button"
          class="ghost"
          :disabled="busy"
          @click="$emit('close')"
          aria-label="Закрыть"
        >
          ✕
        </button>
      </div>
      <form @submit.prevent="save">
        <label
          >Название<input
            v-model.trim="form.name"
            required
            maxlength="100"
            placeholder="Например, Основной сервер" /></label
        ><template v-if="isNode"
          ><label
            >Адрес узла<input
              v-model.trim="form.host"
              required
              maxlength="253"
              placeholder="backend, 192.168.1.1 или ::1" /></label
          ><small class="muted">Без http:// и номера порта</small
          ><label
            >Описание<textarea
              v-model="form.description"
              maxlength="500"
              rows="3"
            ></textarea></label></template
        ><template v-else
          ><label
            >Метод<select v-model="form.check_type">
              <option>ICMP</option>
              <option>TCP</option>
              <option>DNS</option>
              <option>HTTP</option>
            </select></label
          >
          <div v-if="form.check_type === 'HTTP'" class="form-grid">
            <label
              >Схема<select v-model="form.scheme">
                <option>http</option>
                <option>https</option>
              </select></label
            ><label
              >Ожидаемый HTTP-код<input
                type="number"
                min="100"
                max="599"
                required
                v-model.number="form.expected_http_status" /></label
            ><label class="span2"
              >Путь<input
                v-model="form.path"
                required
                maxlength="255"
                pattern="/.*"
                placeholder="/api/health/"
            /></label>
          </div>
          <label v-if="['TCP', 'HTTP'].includes(form.check_type)"
            >Порт {{ form.check_type === "HTTP" ? "(необязательно)" : ""
            }}<input
              type="number"
              min="1"
              max="65535"
              :required="form.check_type === 'TCP'"
              v-model.number="form.port"
              placeholder="80"
          /></label>
          <div class="form-grid">
            <label
              >Интервал, с<input
                type="number"
                min="5"
                max="300"
                required
                v-model.number="form.interval_seconds" /></label
            ><label
              >Тайм-аут, с<input
                type="number"
                min="1"
                :max="Math.min(10, form.interval_seconds - 1)"
                required
                v-model.number="form.timeout_seconds"
            /></label>
          </div>
          <small class="muted"
            >Тайм-аут должен быть меньше интервала. DNS требует доменное
            имя.</small
          ></template
        ><label class="checkbox"
          ><input type="checkbox" v-model="form.enabled" />Мониторинг
          включён</label
        >
        <div v-if="error" class="error" role="alert">{{ error }}</div>
        <div class="form-actions">
          <button
            type="button"
            class="ghost"
            :disabled="busy"
            @click="$emit('close')"
          >
            Отмена</button
          ><button class="primary" :disabled="busy">
            {{ busy ? "Сохранение…" : "Сохранить" }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
