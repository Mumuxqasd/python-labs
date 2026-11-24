const { chromium } = require(
  require.resolve("playwright", {
    paths: [require("path").join(__dirname, "../frontend")],
  }),
);
const fs = require("fs");
const path = require("path");
const baseUrl = process.env.NETSCOPE_URL || "http://localhost:8080";
const username = process.env.NETSCOPE_USERNAME || "admin";
const password = process.env.NETSCOPE_PASSWORD;
if (!password)
  throw Error("Set NETSCOPE_PASSWORD to an existing administrator password");
const nodeName =
  process.env.NETSCOPE_NODE_NAME || "UI acceptance " + Date.now();
const targetHost = process.env.NETSCOPE_TARGET_HOST || "backend";
(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1050 },
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const dir = path.join(__dirname, "../docs/screenshots");
  fs.mkdirSync(dir, { recursive: true });
  await page.goto(baseUrl);
  await page.getByRole("button", { name: "Войти в систему →" }).waitFor();
  await page.screenshot({ path: dir + "/01-login.png" });
  await page.getByLabel("Логин", { exact: true }).fill(username);
  await page.getByLabel("Пароль", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Войти в систему →" }).click();
  await page.getByRole("heading", { name: "Обзор сети" }).waitFor();
  await page.getByRole("link", { name: "▦ Узлы сети" }).click();
  await page.getByRole("button", { name: "＋ Добавить узел" }).click();
  await page.getByLabel("Название", { exact: true }).fill(nodeName);
  await page.getByLabel("Адрес узла").fill(targetHost);
  await page.getByLabel("Описание").fill("Контрольная демонстрация NetScope");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page.getByRole("link", { name: nodeName + " ↗" }).click();
  await page.getByRole("button", { name: "＋ Проверка" }).click();
  await page.getByLabel("Название", { exact: true }).fill("Django TCP");
  await page.getByLabel("Порт", { exact: true }).fill("8000");
  await page.getByLabel("Интервал, с").fill("5");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page
    .getByText("Доступен", { exact: true })
    .first()
    .waitFor({ timeout: 25000 });
  await page.screenshot({ path: dir + "/03-node.png" });
  await page.getByRole("link", { name: "Django TCP ↗" }).click();
  await page
    .getByRole("heading", { name: "Django TCP", exact: true })
    .waitFor();
  await page.getByRole("button", { name: "Изменить", exact: true }).click();
  await page.getByLabel("Порт", { exact: true }).fill("59999");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page
    .getByText("Недоступен", { exact: true })
    .first()
    .waitFor({ timeout: 25000 });
  await page.getByText("Открыт", { exact: true }).waitFor();
  await page.screenshot({ path: dir + "/05-incident.png", fullPage: true });
  await page.getByRole("button", { name: "Изменить", exact: true }).click();
  await page.getByLabel("Порт", { exact: true }).fill("8000");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page
    .getByText("Восстановлено", { exact: true })
    .first()
    .waitFor({ timeout: 25000 });
  await page.screenshot({ path: dir + "/04-check.png", fullPage: true });
  const checkId = page.url().split("/").pop();
  const apiUrl = new URL(`/api/checks/${checkId}/`, page.url()).href;
  const before = (await (await page.request.get(apiUrl)).json())
    .last_checked_at;
  let queued = false;
  for (let attempt = 0; attempt < 5; attempt++) {
    const responsePromise = page.waitForResponse(
      (r) =>
        r.url().endsWith(`/api/checks/${checkId}/run/`) &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("button", { name: "Проверить сейчас", exact: true })
      .click();
    const response = await responsePromise;
    if (response.status() === 202) {
      queued = true;
      break;
    }
    await page.waitForTimeout(1000);
  }
  if (!queued) throw Error("Manual check was never queued");
  await page
    .getByText(/Проверка запрошена/)
    .first()
    .waitFor();
  let finished = false;
  for (let attempt = 0; attempt < 20; attempt++) {
    const current = await (await page.request.get(apiUrl)).json();
    if (current.last_checked_at !== before && !current.manual_requested_at) {
      finished = true;
      break;
    }
    await page.waitForTimeout(500);
  }
  if (!finished) throw Error("Manual result did not finish");
  // A form stays open and keeps its draft while polling continues.
  await page.getByRole("button", { name: "Изменить", exact: true }).click();
  await page.getByLabel("Название", { exact: true }).fill("Несохранённый ввод");
  await page.waitForTimeout(5500);
  if (
    (await page.getByLabel("Название", { exact: true }).inputValue()) !==
    "Несохранённый ввод"
  )
    throw Error("Draft reset by polling");
  await page.getByRole("button", { name: "Отмена", exact: true }).click();
  await page.getByRole("link", { name: "◫ Обзор" }).click();
  await page.getByRole("heading", { name: "Обзор сети" }).waitFor();
  await page.getByText("Доступен", { exact: true }).first().waitFor();
  await page.screenshot({ path: dir + "/02-dashboard.png", fullPage: true });
  await page.getByRole("link", { name: "▦ Узлы сети" }).click();
  await page.getByRole("link", { name: nodeName + " ↗" }).waitFor();
  await page.screenshot({ path: dir + "/06-nodes.png", fullPage: true });
  await page.getByRole("link", { name: "◷ История" }).click();
  await page.getByRole("heading", { name: "История мониторинга" }).waitFor();
  await page
    .getByRole("cell", { name: "Доступен", exact: true })
    .first()
    .waitFor();
  await page.screenshot({ path: dir + "/07-history.png", fullPage: true });
  await page.getByRole("button", { name: "Инциденты", exact: true }).click();
  await page.getByText("Восстановлено", { exact: true }).first().waitFor();
  await page.route("**/api/**", (r) => r.abort());
  await page
    .getByText("Нет связи с сервером", { exact: true })
    .first()
    .waitFor({ timeout: 15000 });
  await page.unroute("**/api/**");
  await page
    .getByText("Автообновление · 5 секунд", { exact: true })
    .waitFor({ timeout: 15000 });
  await page.getByRole("link", { name: "ⓘ О проекте" }).click();
  await page.getByRole("heading", { name: "Четыре метода" }).waitFor();
  await page.setViewportSize({ width: 1024, height: 850 });
  await page.getByRole("link", { name: "◫ Обзор" }).click();
  await page.getByRole("heading", { name: "Обзор сети" }).waitFor();
  await page.screenshot({
    path: dir + "/08-dashboard-1024.png",
    fullPage: true,
  });
  // Remove only the node created by this run. Screenshot files remain.
  await page.getByRole("link", { name: "▦ Узлы сети" }).click();
  await page.getByRole("link", { name: nodeName + " ↗" }).waitFor();
  page.once("dialog", (d) => d.accept());
  await page
    .getByRole("row")
    .filter({ hasText: nodeName })
    .getByRole("button", { name: "Удалить", exact: true })
    .click();
  await page
    .getByRole("link", { name: nodeName + " ↗" })
    .waitFor({ state: "hidden" });
  await page.getByRole("button", { name: username + " · Выйти ↗" }).click();
  await page.getByRole("button", { name: "Войти в систему →" }).waitFor();
  if (errors.length) throw Error(errors.join("\n"));
  console.log(
    "PASS: login, CRUD node/check, real TCP UP → DOWN → UP, incident recovery, manual queue, polling draft, all screens, 1024px layout, logout; no browser errors",
  );
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
