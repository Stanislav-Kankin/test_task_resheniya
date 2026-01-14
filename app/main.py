from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.db import init_db
from app.api.prices import router as prices_router

app = FastAPI(title="Deribit Prices API", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(prices_router)


@app.get("/", response_class=HTMLResponse)
async def ui() -> str:
    return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Deribit Prices UI</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
    .row { display:flex; gap: 16px; flex-wrap: wrap; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; min-width: 260px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: 1px solid #eee; padding: 8px; text-align: left; }
    code { background: #f6f6f6; padding: 2px 6px; border-radius: 6px; }
    .muted { color: #666; font-size: 14px; }
    button, select { padding: 8px 10px; border-radius: 10px; border: 1px solid #ccc; background: white; }
  </style>
</head>
<body>
  <h2>Deribit Prices UI</h2>
  <div class="muted">
    API: <code>/prices</code>, <code>/prices/latest</code>, <code>/prices/range</code> • Swagger: <code>/docs</code>
  </div>

  <div style="margin: 16px 0" class="row">
    <div class="card">
      <div><b>BTC (latest)</b></div>
      <div id="btc">—</div>
      <div class="muted" id="btc_ts"></div>
    </div>
    <div class="card">
      <div><b>ETH (latest)</b></div>
      <div id="eth">—</div>
      <div class="muted" id="eth_ts"></div>
    </div>
    <div class="card">
      <div><b>Последние записи</b></div>
      <div style="display:flex; gap:10px; align-items:center; margin-top:8px;">
        <select id="ticker">
          <option value="btc_usd">btc_usd</option>
          <option value="eth_usd">eth_usd</option>
        </select>
        <button id="btnRefresh" type="button">Обновить</button>
      </div>
      <div class="muted" style="margin-top:8px;">Авто-обновление раз в 10 секунд</div>
    </div>
  </div>

  <div class="card">
    <table>
      <thead>
        <tr>
          <th>ts_unix</th>
          <th>datetime</th>
          <th>ticker</th>
          <th>price</th>
        </tr>
      </thead>
      <tbody id="rows">
        <tr><td colspan="4">—</td></tr>
      </tbody>
    </table>
  </div>

<script>
function fmtTs(ts) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  return d.toLocaleString();
}

async function loadLatest(ticker, valueEl, tsEl) {
  const r = await fetch(`/prices/latest?ticker=${ticker}`);
  if (!r.ok) { valueEl.textContent = `error ${r.status}`; tsEl.textContent = ""; return; }
  const data = await r.json();
  valueEl.textContent = data.price;
  tsEl.textContent = `ts_unix: ${data.ts_unix} • ${fmtTs(data.ts_unix)}`;
}

async function loadTable(ticker) {
  const r = await fetch(`/prices?ticker=${ticker}&limit=20&offset=0`);
  const tbody = document.getElementById("rows");
  if (!r.ok) { tbody.innerHTML = `<tr><td colspan="4">error ${r.status}</td></tr>`; return; }
  const data = await r.json();
  if (!data.length) { tbody.innerHTML = `<tr><td colspan="4">пока пусто</td></tr>`; return; }
  tbody.innerHTML = data.slice(-20).reverse().map(x => `
    <tr>
      <td>${x.ts_unix}</td>
      <td>${fmtTs(x.ts_unix)}</td>
      <td>${x.ticker}</td>
      <td>${x.price}</td>
    </tr>
  `).join("");
}

async function refreshAll() {
  await loadLatest("btc_usd", document.getElementById("btc"), document.getElementById("btc_ts"));
  await loadLatest("eth_usd", document.getElementById("eth"), document.getElementById("eth_ts"));
  const t = document.getElementById("ticker").value;
  await loadTable(t);
}

document.getElementById("ticker").addEventListener("change", refreshAll);

refreshAll();
setInterval(refreshAll, 10000);
</script>
</body>
</html>"""
