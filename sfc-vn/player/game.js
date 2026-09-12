const WIDTH = 18;
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

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderText() {
  const n = node();
  $("place").textContent = n.place || "";
  $("who").textContent = n.portrait ? state.data.portraits[n.portrait] || "" : "";
  if (n.type === "choice") {
    const prompt = `<div class="prompt">${escapeHtml(n.prompt)}</div>`;
    const opts = n.options
      .map((o, i) => {
        const mark = i === state.choice ? "▶ " : "　";
        const on = i === state.choice ? " on" : "";
        return `<div class="choice${on}" data-i="${i}">${mark}${escapeHtml(o.text)}</div>`;
      })
      .join("");
    $("text").innerHTML = prompt + opts;
    $("hint").textContent = "上下选择　点选项或A确定";
    [...$("text").querySelectorAll(".choice")].forEach((el) => {
      el.onclick = (ev) => {
        ev.stopPropagation();
        const i = Number(el.dataset.i);
        if (state.choice === i) advance();
        else {
          state.choice = i;
          renderText();
        }
      };
    });
    return;
  }
  if (n.type === "ending") {
    const pages = [[n.title], ...paginate(n.text, WIDTH, ROWS)];
    $("text").textContent = (pages[state.page] || []).join("\n");
    $("hint").textContent = state.page + 1 >= pages.length ? "点屏幕回到标题" : "点屏幕继续　Start菜单";
    return;
  }
  $("text").textContent = (state.pages[state.page] || []).join("\n");
  $("hint").textContent = "点屏幕继续　Start／Esc 菜单";
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
  state.menu = ["开始游戏", "读取档案", "退出游戏"];
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
  if (state.nodeId === "__title" || state.nodeId === "__quit") return;
  state.menu = ["继续", "保存", "读取", "回标题", "退出游戏"];
  state.menuKind = "root";
  state.menuIndex = 0;
  drawOverlay();
}

function askQuit() {
  state.menu = ["再想想", "确定退出"];
  state.menuKind = "quitask";
  state.menuIndex = 0;
  drawOverlay();
}

function quitGame() {
  if (document.fullscreenElement) document.exitFullscreen?.().catch(() => {});
  state.nodeId = "__quit";
  state.menu = ["重新开始"];
  state.menuKind = "quit";
  state.menuIndex = 0;
  setBg("title");
  setPortrait("");
  $("place").textContent = "";
  $("who").textContent = "";
  $("text").textContent = `${state.data.title}\n\n已经退出。`;
  $("hint").textContent = "";
  drawOverlay();
  try {
    window.close();
  } catch {
    /* browsers only close windows they opened */
  }
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
    quitask: "要退出游戏吗",
    quit: "已经退出",
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
    } else if (i === 1) {
      state.menuKind = "load";
      const saves = loadSaves();
      state.menu = saves.map((s, idx) => `${slotLabel(s, idx)}${s ? `<span class="slotmeta">${s.when}　${s.preview}</span>` : ""}`);
      state.menuIndex = 0;
      drawOverlay();
    } else {
      askQuit();
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
    } else if (i === 3) {
      closeMenu();
      showTitle();
    } else {
      askQuit();
    }
    return;
  }
  if (kind === "quitask") {
    if (i === 0) {
      if (state.nodeId === "__title") showTitle();
      else openMenu();
    } else {
      quitGame();
    }
    return;
  }
  if (kind === "quit") {
    showTitle();
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

function menuBack() {
  if (state.menuKind === "quitask") {
    if (state.nodeId === "__title") showTitle();
    else openMenu();
    return;
  }
  if (state.menu && state.menuKind !== "title" && state.menuKind !== "quit") {
    closeMenu();
    return;
  }
  if (state.menuKind !== "quit") openMenu();
}

function onKey(ev) {
  const k = ev.key;
  const code = ev.keyCode || ev.which;
  const up = k === "ArrowUp" || k === "w" || k === "W" || code === 19;
  const down = k === "ArrowDown" || k === "s" || k === "S" || code === 20;
  const ok =
    k === "Enter" ||
    k === " " ||
    k === "z" ||
    k === "Z" ||
    k === "x" ||
    k === "X" ||
    code === 23 ||
    code === 96 ||
    code === 99 ||
    code === 100;
  const menu =
    k === "Escape" ||
    k === "Backspace" ||
    k === "ContextMenu" ||
    code === 4 ||
    code === 82 ||
    code === 97 ||
    code === 108 ||
    code === 109;
  if (up || down || ok || menu) ev.preventDefault();
  if (up) move(-1);
  else if (down) move(1);
  else if (ok) advance();
  else if (menu) menuBack();
}

function tryFullscreen() {
  if (document.fullscreenElement) return;
  const landscape = window.innerWidth > window.innerHeight;
  if (window.innerHeight <= 720 && landscape) {
    document.documentElement.requestFullscreen?.().catch(() => {});
  }
}

const padPrev = {};
const padHold = {};
function padPressed(gp, i) {
  const b = gp.buttons[i];
  return !!(b && (b.pressed || b.value > 0.5));
}
function padAxis(gp, i) {
  return gp.axes && Number.isFinite(gp.axes[i]) ? gp.axes[i] : 0;
}
function padEdge(id, down) {
  const now = performance.now();
  const was = !!padPrev[id];
  padPrev[id] = down;
  if (down && !was) {
    padHold[id] = now;
    return true;
  }
  if (down && was && now - (padHold[id] || 0) > 380) {
    padHold[id] = now - 260;
    return id === "up" || id === "down";
  }
  return false;
}
function padDpad(gp) {
  const y = padAxis(gp, 1) || padAxis(gp, 3);
  const hatY = padAxis(gp, 7) || padAxis(gp, 5);
  const up = padPressed(gp, 12) || y < -0.5 || hatY < -0.5;
  const down = padPressed(gp, 13) || y > 0.5 || hatY > 0.5;
  return { up, down };
}
function firstGamepad() {
  const pads = navigator.getGamepads?.() || [];
  for (const gp of pads) {
    if (gp && gp.buttons && gp.buttons.length) return gp;
  }
  return null;
}

function pollGamepad() {
  const gp = firstGamepad();
  if (gp) {
    const d = padDpad(gp);
    if (padEdge("up", d.up)) move(-1);
    if (padEdge("down", d.down)) move(1);
    const faceA = padPressed(gp, 0) || padPressed(gp, 2);
    const faceB = padPressed(gp, 1) || padPressed(gp, 3);
    const start = padPressed(gp, 8) || padPressed(gp, 9) || padPressed(gp, 11);
    if (state.menu) {
      if (padEdge("a", faceA || (state.menuKind === "title" && faceB))) advance();
      else if (padEdge("menu", start || (faceB && state.menuKind !== "title"))) menuBack();
    } else {
      if (padEdge("a", faceA || faceB)) advance();
      else if (padEdge("menu", start)) menuBack();
    }
  }
  requestAnimationFrame(pollGamepad);
}

async function main() {
  state.data = await (await fetch("story.json")).json();
  document.addEventListener("keydown", onKey);
  $("screen").addEventListener("click", () => {
    tryFullscreen();
    advance();
  });
  window.addEventListener("gamepadconnected", () => {
    $("hint").textContent = "已识别手柄　A确定　上下选　Start菜单";
  });
  pollGamepad();
  showTitle();
}

main();
