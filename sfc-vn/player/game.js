const WIDTH = 16;
const ROWS = 4;
const SAVE_KEY = "city11_saves_v1";

const $ = (id) => document.getElementById(id);
const state = {
  data: null,
  nodeId: null,
  pages: [],
  page: 0,
  choice: 0,
  menu: null,
  menuIndex: 0,
  menuKind: "root",
};

function paginate(text, width, rows) {
  const lines = [];
  for (const para of String(text).split("\n")) {
    if (para === "") {
      lines.push("");
      continue;
    }
    let buf = "";
    for (const ch of para) {
      if (buf.length >= width) {
        lines.push(buf);
        buf = ch;
      } else buf += ch;
    }
    if (buf) lines.push(buf);
  }
  const pages = [];
  for (let i = 0; i < lines.length; i += rows) pages.push(lines.slice(i, i + rows));
  return pages.length ? pages : [[""]];
}

function loadSaves() {
  try {
    const raw = JSON.parse(localStorage.getItem(SAVE_KEY) || "[]");
    return [0, 1, 2].map((i) => raw[i] || null);
  } catch {
    return [null, null, null];
  }
}

function writeSaves(saves) {
  localStorage.setItem(SAVE_KEY, JSON.stringify(saves));
}

function node() {
  return state.data.nodes[state.nodeId];
}

function setBg(scene) {
  $("bg").src = `assets/scene_${scene || "title"}.jpg`;
}

function setPortrait(id) {
  const img = $("portrait");
  if (!id) {
    img.style.display = "none";
    img.removeAttribute("src");
    return;
  }
  img.src = `assets/portrait_${id}.png`;
  img.style.display = "block";
}

function renderText() {
  const n = node();
  $("place").textContent = n.place || "";
  $("who").textContent = n.portrait ? state.data.portraits[n.portrait] || "" : "";
  if (n.type === "choice") {
    const lines = [n.prompt, ...n.options.map((o, i) => `${i === state.choice ? "▶ " : "　"}${o.text}`)];
    $("text").textContent = lines.join("\n");
    $("hint").textContent = "上下选择　Z确定　Esc菜单";
    return;
  }
  if (n.type === "ending") {
    const pages = [[n.title], ...paginate(n.text, WIDTH, ROWS)];
    $("text").textContent = (pages[state.page] || []).join("\n");
    $("hint").textContent = state.page + 1 >= pages.length ? "Z 回到标题" : "Z 继续　Esc菜单";
    return;
  }
  $("text").textContent = (state.pages[state.page] || []).join("\n");
  $("hint").textContent = "Z 继续　Esc 随时存读档";
}

function endingPages(n) {
  return 1 + paginate(n.text, WIDTH, ROWS).length;
}

function endingPageList(n) {
  return [[n.title], ...paginate(n.text, WIDTH, ROWS)];
}

function enterNode(id) {
  state.nodeId = id;
  state.choice = 0;
  state.page = 0;
  const n = node();
  setBg(n.scene);
  setPortrait(n.portrait);
  if (n.type === "text") state.pages = paginate(n.text, WIDTH, ROWS);
  else state.pages = [];
  renderText();
}

function advance() {
  if (state.menu) return activateMenu();
  const n = node();
  if (n.type === "choice") {
    enterNode(n.options[state.choice].next);
    return;
  }
  if (n.type === "ending") {
    if (state.page + 1 < endingPages(n)) {
      state.page += 1;
      renderText();
    } else showTitle();
    return;
  }
  if (state.page + 1 < state.pages.length) {
    state.page += 1;
    renderText();
  } else enterNode(n.next);
}

function showTitle() {
  state.nodeId = "__title";
  state.menu = ["开始游戏", "读取档案"];
  state.menuKind = "title";
  state.menuIndex = 0;
  setBg("title");
  setPortrait("");
  $("place").textContent = "";
  $("who").textContent = "";
  $("text").textContent = `${state.data.title}\n${state.data.subtitle}\n\n${state.data.hint}`;
  $("hint").textContent = "";
  drawOverlay();
}

function openMenu() {
  if (state.nodeId === "__title") return;
  state.menu = ["继续", "保存", "读取", "回标题"];
  state.menuKind = "root";
  state.menuIndex = 0;
  drawOverlay();
}

function slotLabel(slot, i) {
  if (!slot) return `空槽 ${i + 1}`;
  return `槽 ${i + 1}　${slot.place || "旅途中"}`;
}

function drawOverlay() {
  const ov = $("overlay");
  if (!state.menu) {
    ov.classList.add("hidden");
    return;
  }
  ov.classList.remove("hidden");
  const title = {
    title: state.data.title,
    root: "菜单　随时可存读",
    save: "保存到哪一格",
    load: "读取哪一格",
  }[state.menuKind];
  const items = state.menu
    .map((label, i) => `<div class="item${i === state.menuIndex ? " active" : ""}" data-i="${i}">${label}</div>`)
    .join("");
  $("panel").innerHTML = `<h2>${title}</h2>${items}`;
  [...$("panel").querySelectorAll(".item")].forEach((el) => {
    el.onmouseenter = () => {
      state.menuIndex = Number(el.dataset.i);
      drawOverlay();
    };
    el.onclick = (ev) => {
      ev.stopPropagation();
      state.menuIndex = Number(el.dataset.i);
      activateMenu();
    };
  });
}

function activateMenu() {
  const kind = state.menuKind;
  const i = state.menuIndex;
  if (kind === "title") {
    if (i === 0) {
      closeMenu();
      enterNode(state.data.start);
    } else {
      state.menuKind = "load";
      const saves = loadSaves();
      state.menu = saves.map((s, idx) => `${slotLabel(s, idx)}${s ? `<span class="slotmeta">${s.when}　${s.preview}</span>` : ""}`);
      state.menuIndex = 0;
      drawOverlay();
    }
    return;
  }
  if (kind === "root") {
    if (i === 0) closeMenu();
    else if (i === 1) {
      state.menuKind = "save";
      const saves = loadSaves();
      state.menu = saves.map((s, idx) => slotLabel(s, idx));
      state.menuIndex = 0;
      drawOverlay();
    } else if (i === 2) {
      state.menuKind = "load";
      const saves = loadSaves();
      state.menu = saves.map((s, idx) => `${slotLabel(s, idx)}${s ? `<span class="slotmeta">${s.when}　${s.preview}</span>` : ""}`);
      state.menuIndex = 0;
      drawOverlay();
    } else {
      closeMenu();
      showTitle();
    }
    return;
  }
  if (kind === "save") {
    const n = node();
    const saves = loadSaves();
    saves[i] = {
      nodeId: state.nodeId,
      page: state.page,
      choice: state.choice,
      place: n.place || "",
      preview: (n.text || n.prompt || n.title || "").slice(0, 16),
      when: new Date().toLocaleString("zh-CN", { hour12: false }),
    };
    writeSaves(saves);
    closeMenu();
    $("hint").textContent = `已保存到槽 ${i + 1}`;
    return;
  }
  if (kind === "load") {
    const saves = loadSaves();
    const slot = saves[i];
    if (!slot) return;
    closeMenu();
    enterNode(slot.nodeId);
    state.page = slot.page || 0;
    state.choice = slot.choice || 0;
    if (node().type === "text") {
      state.pages = paginate(node().text, WIDTH, ROWS);
      if (state.page >= state.pages.length) state.page = 0;
    }
    renderText();
  }
}

function closeMenu() {
  state.menu = null;
  drawOverlay();
}

function move(dir) {
  if (state.menu) {
    state.menuIndex = (state.menuIndex + dir + state.menu.length) % state.menu.length;
    drawOverlay();
    return;
  }
  const n = node();
  if (n && n.type === "choice") {
    state.choice = (state.choice + dir + n.options.length) % n.options.length;
    renderText();
  }
}

function onKey(ev) {
  const k = ev.key;
  if (k === "ArrowDown" || k === "s") move(1);
  else if (k === "ArrowUp" || k === "w") move(-1);
  else if (k === "Enter" || k === " " || k === "z" || k === "Z") advance();
  else if (k === "Escape") {
    if (state.menu && state.menuKind !== "title") closeMenu();
    else openMenu();
  }
}

async function main() {
  state.data = await (await fetch("story.json")).json();
  document.addEventListener("keydown", onKey);
  $("screen").addEventListener("click", () => advance());
  showTitle();
}

main();
