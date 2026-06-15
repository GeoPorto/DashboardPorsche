import json
from pathlib import Path

import pandas as pd


INPUT_XLSX = Path(r"data\dadosPorsche.xlsx")
OUTPUT_DIR = Path(r"outputs")
OUTPUT_HTML = OUTPUT_DIR / "porsche_sales_dashboard.html"


def clean_record(row):
    raw_date = row.get("SaleDateSanitized")
    parsed_date = pd.to_datetime(raw_date, errors="coerce")
    has_date = not pd.isna(parsed_date)
    return {
        "sale_id": int(row["sale_id"]) if not pd.isna(row["sale_id"]) else None,
        "sale_date": parsed_date.strftime("%Y-%m-%d") if has_date else None,
        "sale_date_raw": "" if pd.isna(raw_date) else str(raw_date),
        "year": int(parsed_date.year) if has_date else None,
        "month": int(parsed_date.month) if has_date else None,
        "customer_name": "" if pd.isna(row.get("customer_name")) else str(row.get("customer_name")),
        "model": "" if pd.isna(row.get("PorscheModelSanitized")) else str(row.get("PorscheModelSanitized")),
        "model_year": int(row["ModelYearSanitized"]) if not pd.isna(row["ModelYearSanitized"]) else None,
        "price": float(row["SalesPriceSanitized"]) if not pd.isna(row["SalesPriceSanitized"]) else 0.0,
        "mileage": int(row["VehicleMileageSanitized"]) if not pd.isna(row["VehicleMileageSanitized"]) else 0,
        "pay_method": "" if pd.isna(row.get("PayMethodSanitized")) else str(row.get("PayMethodSanitized")),
        "city": "" if pd.isna(row.get("CitySanitized")) else str(row.get("CitySanitized")),
        "state": "" if pd.isna(row.get("StateSanitized")) else str(row.get("StateSanitized")),
        "salesperson": "" if pd.isna(row.get("salesperson")) else str(row.get("salesperson")),
        "status": "" if pd.isna(row.get("DeliveryStatusSanitized")) else str(row.get("DeliveryStatusSanitized")),
    }


def main():
    df = pd.read_excel(INPUT_XLSX, sheet_name="Sanitized")
    records = [clean_record(row) for _, row in df.iterrows()]
    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))

    html = f"""<!doctype html>
<html lang="pt">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Porsche Sales BI Dashboard</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --panel: #ffffff;
      --panel-2: #fbfcfd;
      --ink: #17202a;
      --muted: #6d7785;
      --line: #dfe4ea;
      --line-2: #ebeff3;
      --accent: #b42318;
      --accent-2: #1f7a8c;
      --accent-3: #d4a017;
      --good: #16805b;
      --warn: #b7791f;
      --danger: #b42318;
      --shadow: 0 14px 32px rgba(28, 36, 46, 0.09);
      --radius: 8px;
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      min-height: 100vh;
    }}

    .app {{
      display: grid;
      grid-template-columns: 292px minmax(0, 1fr);
      min-height: 100vh;
    }}

    aside {{
      background: #101820;
      color: #f7fafc;
      padding: 22px 18px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      border-right: 1px solid #0d141b;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }}

    .crest {{
      width: 42px;
      height: 42px;
      border: 1px solid rgba(255,255,255,.25);
      background: linear-gradient(135deg, #f4c542 0 45%, #b42318 45% 72%, #101820 72%);
      box-shadow: inset 0 0 0 4px rgba(255,255,255,.08);
      border-radius: 8px;
      flex: 0 0 auto;
    }}

    .brand h1 {{
      font-size: 18px;
      line-height: 1.08;
      margin: 0;
      font-weight: 700;
      letter-spacing: 0;
    }}

    .brand p {{
      margin: 4px 0 0;
      color: #a9b4c0;
      font-size: 12px;
    }}

    .filter-block {{
      margin-bottom: 16px;
    }}

    label {{
      display: block;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: #a9b4c0;
      margin-bottom: 7px;
      font-weight: 700;
    }}

    select, .multi-button {{
      width: 100%;
      background: #17232e;
      border: 1px solid #2d3b47;
      color: #f7fafc;
      min-height: 38px;
      border-radius: 6px;
      padding: 8px 10px;
      outline: none;
      font-size: 13px;
    }}

    select:focus, .multi-filter.open .multi-button {{
      border-color: #d4a017;
      box-shadow: 0 0 0 3px rgba(212, 160, 23, .16);
    }}

    .multi-filter {{
      position: relative;
    }}

    .multi-button {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      text-align: left;
      font-weight: 600;
    }}

    .multi-button span {{
      display: block;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .multi-button svg {{
      flex: 0 0 auto;
      color: #a9b4c0;
    }}

    .multi-menu {{
      display: none;
      position: absolute;
      top: calc(100% + 6px);
      left: 0;
      right: 0;
      z-index: 15;
      max-height: 250px;
      overflow: auto;
      background: #17232e;
      border: 1px solid #2d3b47;
      border-radius: 6px;
      box-shadow: 0 18px 32px rgba(0, 0, 0, .28);
      padding: 6px;
    }}

    .multi-filter.open .multi-menu {{
      display: block;
    }}

    .multi-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 7px 8px;
      border-radius: 5px;
      color: #eef2f7;
      font-size: 13px;
      cursor: pointer;
    }}

    .multi-row:hover {{
      background: rgba(255, 255, 255, .07);
    }}

    .multi-row input {{
      width: 14px;
      height: 14px;
      accent-color: #d4a017;
      flex: 0 0 auto;
    }}

    .multi-clear {{
      width: 100%;
      min-height: 30px;
      margin-bottom: 4px;
      background: #22313f;
      color: #d8dee5;
      border: 1px solid #334455;
      font-size: 12px;
    }}

    .multi-empty {{
      color: #9aa7b5;
      padding: 8px;
      font-size: 12px;
    }}

    .filter-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}

    .sidebar-actions {{
      display: grid;
      gap: 9px;
      margin-top: 20px;
    }}

    button {{
      border: 0;
      cursor: pointer;
      border-radius: 6px;
      font-weight: 700;
      min-height: 39px;
      font-size: 13px;
    }}

    .reset {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: #f7fafc;
      color: #111827;
    }}

    .ghost {{
      background: transparent;
      color: #d8dee5;
      border: 1px solid #2d3b47;
    }}

    .side-note {{
      margin: 16px 0 0;
      color: #9aa7b5;
      font-size: 12px;
      line-height: 1.45;
    }}

    main {{
      padding: 24px;
      min-width: 0;
    }}

    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 18px;
      margin-bottom: 18px;
    }}

    .title h2 {{
      margin: 0;
      font-size: 26px;
      letter-spacing: 0;
    }}

    .title p {{
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 13px;
    }}

    .summary-badge {{
      min-width: 220px;
      text-align: right;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
      padding-top: 4px;
    }}

    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(160px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }}

    .kpi {{
      background: var(--panel);
      border: 1px solid var(--line-2);
      border-radius: var(--radius);
      padding: 16px 16px 14px;
      box-shadow: var(--shadow);
      min-height: 108px;
      position: relative;
      overflow: hidden;
    }}

    .kpi::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      height: 4px;
      width: 100%;
      background: var(--accent);
    }}

    .kpi:nth-child(2)::before {{ background: var(--accent-2); }}
    .kpi:nth-child(3)::before {{ background: var(--accent-3); }}
    .kpi:nth-child(4)::before {{ background: var(--good); }}

    .kpi span {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-weight: 800;
    }}

    .kpi strong {{
      display: block;
      font-size: 25px;
      margin-top: 12px;
      letter-spacing: 0;
      white-space: nowrap;
    }}

    .kpi small {{
      color: var(--muted);
      display: block;
      margin-top: 7px;
      font-size: 12px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(0, .9fr);
      gap: 16px;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line-2);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      min-width: 0;
      overflow: hidden;
    }}

    .panel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 14px 16px 8px;
      border-bottom: 1px solid var(--line-2);
    }}

    .panel-title h3 {{
      margin: 0;
      font-size: 15px;
      letter-spacing: 0;
    }}

    .panel-title p {{
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 12px;
    }}

    .chart-wrap {{
      padding: 12px 14px 14px;
      position: relative;
    }}

    canvas {{
      display: block;
      width: 100%;
      height: 330px;
    }}

    .tall canvas {{
      height: 450px;
    }}

    .scroll-chart {{
      max-height: 460px;
      overflow-y: auto;
      padding-right: 4px;
    }}

    .scroll-chart canvas {{
      height: auto;
      min-height: 430px;
    }}

    .segment {{
      display: inline-flex;
      background: #eef2f5;
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      flex: 0 0 auto;
    }}

    .segment button {{
      min-height: 30px;
      padding: 0 10px;
      border-radius: 0;
      color: var(--muted);
      background: transparent;
      font-size: 12px;
    }}

    .segment button.active {{
      background: #101820;
      color: #ffffff;
    }}

    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      padding: 0 16px 12px;
      color: var(--muted);
      font-size: 12px;
    }}

    .legend span {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .swatch {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      display: inline-block;
      flex: 0 0 auto;
    }}

    .tooltip {{
      position: fixed;
      pointer-events: none;
      background: rgba(16, 24, 32, .94);
      color: #fff;
      padding: 9px 10px;
      border-radius: 6px;
      box-shadow: 0 12px 24px rgba(0,0,0,.18);
      font-size: 12px;
      line-height: 1.4;
      z-index: 20;
      max-width: 260px;
      opacity: 0;
      transform: translate(10px, 10px);
      transition: opacity .12s ease;
    }}

    .empty {{
      height: 230px;
      display: none;
      align-items: center;
      justify-content: center;
      text-align: center;
      color: var(--muted);
      font-size: 13px;
      border: 1px dashed var(--line);
      border-radius: var(--radius);
      background: var(--panel-2);
    }}

    .panel.is-empty canvas,
    .panel.is-empty .legend {{
      display: none;
    }}

    .panel.is-empty .empty {{
      display: flex;
    }}

    @media (max-width: 1180px) {{
      .kpis {{ grid-template-columns: repeat(2, minmax(160px, 1fr)); }}
      .grid {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 860px) {{
      .app {{ grid-template-columns: 1fr; }}
      aside {{
        position: static;
        height: auto;
      }}
      main {{ padding: 18px; }}
      .topbar {{
        display: block;
      }}
      .summary-badge {{
        text-align: left;
        margin-top: 10px;
      }}
      .kpis {{ grid-template-columns: 1fr; }}
      canvas {{ height: 300px; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="brand">
        <div class="crest" aria-hidden="true"></div>
        <div>
          <h1>Porsche Sales BI</h1>
          <p>Dashboard executivo</p>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-block">
          <label for="yearFilter">Ano</label>
          <select id="yearFilter"></select>
        </div>
        <div class="filter-block">
          <label for="monthFilter">Mês</label>
          <select id="monthFilter"></select>
        </div>
      </div>

      <div class="filter-block">
        <label>Estado</label>
        <div class="multi-filter" data-filter="state">
          <button class="multi-button" id="stateButton" type="button"><span>Todos</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
          <div class="multi-menu" id="stateMenu"></div>
        </div>
      </div>

      <div class="filter-block">
        <label>Cidade</label>
        <div class="multi-filter" data-filter="city">
          <button class="multi-button" id="cityButton" type="button"><span>Todas</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
          <div class="multi-menu" id="cityMenu"></div>
        </div>
      </div>

      <div class="filter-block">
        <label>Modelo</label>
        <div class="multi-filter" data-filter="model">
          <button class="multi-button" id="modelButton" type="button"><span>Todos</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
          <div class="multi-menu" id="modelMenu"></div>
        </div>
      </div>

      <div class="filter-block">
        <label>Entrega</label>
        <div class="multi-filter" data-filter="status">
          <button class="multi-button" id="statusButton" type="button"><span>Todos</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
          <div class="multi-menu" id="statusMenu"></div>
        </div>
      </div>

      <div class="sidebar-actions">
        <button class="reset" id="resetFilters" title="Limpar filtros">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7M3 4v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Limpar filtros
        </button>
        <button class="ghost" id="selectDelivered">Ver entregues</button>
      </div>

      <p class="side-note">Datas inválidas permanecem nos totais quando o período está em "Todos". Ao filtrar ano ou mês, apenas vendas com data válida entram na análise.</p>
    </aside>

    <main>
      <section class="topbar">
        <div class="title">
          <h2>Análise de Vendas Porsche</h2>
          <p>KPIs comerciais, eficiência da entrega, performance da equipa e comportamento de preço.</p>
        </div>
        <div class="summary-badge" id="filterSummary"></div>
      </section>

      <section class="kpis">
        <article class="kpi">
          <span>Receita Total</span>
          <strong id="kpiRevenue">$0</strong>
          <small>Exclui vendas canceladas</small>
        </article>
        <article class="kpi">
          <span>Volume de Vendas</span>
          <strong id="kpiVolume">0</strong>
          <small>Contagem de sale_id</small>
        </article>
        <article class="kpi">
          <span>Ticket Médio</span>
          <strong id="kpiAverage">$0</strong>
          <small>Preço médio da seleção</small>
        </article>
        <article class="kpi">
          <span>Sucesso na Entrega</span>
          <strong id="kpiDelivery">0%</strong>
          <small>Delivered / volume filtrado</small>
        </article>
      </section>

      <section class="grid">
        <article class="panel" id="panelModelScatter">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Receita por Modelo</h3>
              <p>Volume no eixo X e receita no eixo Y</p>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas id="modelScatter"></canvas>
            <div class="empty">Sem dados para esta seleção.</div>
          </div>
          <div class="legend" id="familyLegend"></div>
        </article>

        <article class="panel" id="panelDonut">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Status de Entrega</h3>
              <p>Distribuição por categoria</p>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas id="donutChart"></canvas>
            <div class="empty">Sem dados para esta seleção.</div>
          </div>
          <div class="legend" id="statusLegend"></div>
        </article>

        <article class="panel tall" id="panelSalesperson">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Performance da Equipa</h3>
              <p>Total de vendas por salesperson em ordem decrescente</p>
            </div>
          </div>
          <div class="chart-wrap scroll-chart">
            <canvas id="salespersonBar"></canvas>
            <div class="empty">Sem dados para esta seleção.</div>
          </div>
        </article>

        <article class="panel" id="panelStacked">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Preferências por Estado</h3>
              <p id="stackedSubtitle">Métodos de pagamento nos estados com maior volume</p>
            </div>
            <div class="segment" role="group" aria-label="Tipo de empilhamento">
              <button id="stackPayment" class="active" type="button">Pagamento</button>
              <button id="stackFamily" type="button">Modelo</button>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas id="stackedBar"></canvas>
            <div class="empty">Sem dados para esta seleção.</div>
          </div>
          <div class="legend" id="stackLegend"></div>
        </article>

        <article class="panel" id="panelMileage" style="grid-column: 1 / -1;">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Quilometragem vs Preço</h3>
              <p>Dispersão com linha de tendência linear</p>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas id="mileageScatter"></canvas>
            <div class="empty">Sem dados suficientes para a tendência.</div>
          </div>
        </article>
      </section>
    </main>
  </div>

  <div class="tooltip" id="tooltip"></div>

  <script id="sales-data" type="application/json">{payload}</script>
  <script>
    const DATA = JSON.parse(document.getElementById('sales-data').textContent);
    const MONTHS = [
      ['1', 'Jan'], ['2', 'Fev'], ['3', 'Mar'], ['4', 'Abr'], ['5', 'Mai'], ['6', 'Jun'],
      ['7', 'Jul'], ['8', 'Ago'], ['9', 'Set'], ['10', 'Out'], ['11', 'Nov'], ['12', 'Dez']
    ];
    const FAMILY_COLORS = {{
      '911': '#b42318',
      'Cayenne': '#1f7a8c',
      'Macan': '#d4a017',
      'Panamera': '#4c6fff',
      'Taycan': '#16805b',
      '718': '#7c3aed',
      'Outro': '#64748b'
    }};
    const STATUS_COLORS = {{
      'Delivered': '#16805b',
      'In Transit': '#1f7a8c',
      'Shipped': '#4c6fff',
      'Pending': '#d4a017',
      'Pending Approval': '#b7791f',
      'Pending Review': '#a16207',
      'Awaiting Delivery': '#8b5cf6',
      'Awaiting Pickup': '#7c3aed',
      'Awaiting Review': '#64748b',
      'Cancelled': '#b42318'
    }};
    const SERIES_COLORS = ['#b42318', '#1f7a8c', '#d4a017', '#4c6fff', '#16805b', '#7c3aed', '#db2777', '#475569', '#ea580c', '#0f766e'];
    const tooltip = document.getElementById('tooltip');
    let stackMode = 'payment';
    let hoverLayers = {{}};

    const els = {{
      year: document.getElementById('yearFilter'),
      month: document.getElementById('monthFilter'),
      summary: document.getElementById('filterSummary'),
      kpiRevenue: document.getElementById('kpiRevenue'),
      kpiVolume: document.getElementById('kpiVolume'),
      kpiAverage: document.getElementById('kpiAverage'),
      kpiDelivery: document.getElementById('kpiDelivery')
    }};

    const filterState = {{
      state: new Set(),
      city: new Set(),
      model: new Set(),
      status: new Set()
    }};

    const multiFilters = {{
      state: {{
        field: 'state',
        allText: 'Todos os estados',
        button: document.getElementById('stateButton'),
        menu: document.getElementById('stateMenu')
      }},
      city: {{
        field: 'city',
        allText: 'Todas as cidades',
        button: document.getElementById('cityButton'),
        menu: document.getElementById('cityMenu')
      }},
      model: {{
        field: 'model',
        allText: 'Todos os modelos',
        button: document.getElementById('modelButton'),
        menu: document.getElementById('modelMenu')
      }},
      status: {{
        field: 'status',
        allText: 'Todos os status',
        button: document.getElementById('statusButton'),
        menu: document.getElementById('statusMenu')
      }}
    }};

    const formatUSD = new Intl.NumberFormat('en-US', {{
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }});
    const formatInt = new Intl.NumberFormat('pt-PT');

    function uniqueSorted(rows, key) {{
      return [...new Set(rows.map(d => d[key]).filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b)));
    }}

    function selectedValues(key) {{
      return [...filterState[key]];
    }}

    function setOptions(select, values, allLabel = 'Todos') {{
      select.innerHTML = '';
      const all = document.createElement('option');
      all.value = '__all';
      all.textContent = allLabel;
      select.appendChild(all);
      values.forEach(value => {{
        const opt = document.createElement('option');
        opt.value = String(value);
        opt.textContent = String(value);
        select.appendChild(opt);
      }});
    }}

    function updateMultiButton(key) {{
      const cfg = multiFilters[key];
      const values = selectedValues(key);
      const label = cfg.button.querySelector('span');
      if (!values.length) {{
        label.textContent = cfg.allText;
        cfg.button.title = cfg.allText;
      }} else if (values.length === 1) {{
        label.textContent = values[0];
        cfg.button.title = values[0];
      }} else {{
        label.textContent = values.length + ' selecionados';
        cfg.button.title = values.join(', ');
      }}
    }}

    function setMultiOptions(key, values) {{
      const cfg = multiFilters[key];
      const allowed = new Set(values.map(String));
      [...filterState[key]].forEach(value => {{
        if (!allowed.has(value)) filterState[key].delete(value);
      }});
      cfg.menu.innerHTML = '';

      const clear = document.createElement('button');
      clear.className = 'multi-clear';
      clear.type = 'button';
      clear.dataset.clear = key;
      clear.textContent = cfg.allText;
      cfg.menu.appendChild(clear);

      if (!values.length) {{
        const empty = document.createElement('div');
        empty.className = 'multi-empty';
        empty.textContent = 'Sem opções disponíveis';
        cfg.menu.appendChild(empty);
        updateMultiButton(key);
        return;
      }}

      values.forEach(value => {{
        const text = String(value);
        const row = document.createElement('label');
        row.className = 'multi-row';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.value = text;
        input.dataset.key = key;
        input.checked = filterState[key].has(text);

        const span = document.createElement('span');
        span.textContent = text;

        row.appendChild(input);
        row.appendChild(span);
        cfg.menu.appendChild(row);
      }});
      updateMultiButton(key);
    }}

    function family(model) {{
      if (model.startsWith('911')) return '911';
      if (model.startsWith('718')) return '718';
      if (model.startsWith('Cayenne')) return 'Cayenne';
      if (model.startsWith('Macan')) return 'Macan';
      if (model.startsWith('Panamera')) return 'Panamera';
      if (model.startsWith('Taycan')) return 'Taycan';
      return 'Outro';
    }}

    function initFilters() {{
      const years = uniqueSorted(DATA.filter(d => d.year), 'year').map(String);
      setOptions(els.year, years, 'Todos');
      setOptions(els.month, MONTHS.map(m => m[0]), 'Todos');
      [...els.month.options].forEach(opt => {{
        const match = MONTHS.find(m => m[0] === opt.value);
        if (match) opt.textContent = match[1];
      }});
      Object.values(filterState).forEach(set => set.clear());
      setMultiOptions('state', uniqueSorted(DATA, 'state'));
      setMultiOptions('city', uniqueSorted(DATA, 'city'));
      setMultiOptions('model', uniqueSorted(DATA, 'model'));
      setMultiOptions('status', uniqueSorted(DATA, 'status'));
    }}

    function refreshDependentFilters() {{
      const states = selectedValues('state');
      const rowsForCities = DATA.filter(d => !states.length || states.includes(d.state));
      const nextCities = uniqueSorted(rowsForCities, 'city');
      setMultiOptions('city', nextCities);
      setMultiOptions('model', uniqueSorted(DATA, 'model'));
      setMultiOptions('status', uniqueSorted(DATA, 'status'));
    }}

    function getFilteredRows() {{
      const year = els.year.value === '__all' ? null : Number(els.year.value);
      const month = els.month.value === '__all' ? null : Number(els.month.value);
      const states = selectedValues('state');
      const cities = selectedValues('city');
      const models = selectedValues('model');
      const statuses = selectedValues('status');
      return DATA.filter(d => {{
        if (year !== null && d.year !== year) return false;
        if (month !== null && d.month !== month) return false;
        if (states.length && !states.includes(d.state)) return false;
        if (cities.length && !cities.includes(d.city)) return false;
        if (models.length && !models.includes(d.model)) return false;
        if (statuses.length && !statuses.includes(d.status)) return false;
        return true;
      }});
    }}

    function aggregate(rows, key, valueFn = () => 1) {{
      const map = new Map();
      rows.forEach(row => {{
        const k = row[key] || 'N/D';
        map.set(k, (map.get(k) || 0) + valueFn(row));
      }});
      return [...map.entries()].map(([name, value]) => ({{ name, value }}));
    }}

    function updateKpis(rows) {{
      const revenueRows = rows.filter(d => d.status !== 'Cancelled');
      const revenue = revenueRows.reduce((sum, d) => sum + d.price, 0);
      const totalPrice = rows.reduce((sum, d) => sum + d.price, 0);
      const delivered = rows.filter(d => d.status === 'Delivered').length;
      const avg = rows.length ? totalPrice / rows.length : 0;
      const deliveryRate = rows.length ? delivered / rows.length : 0;
      els.kpiRevenue.textContent = formatUSD.format(revenue);
      els.kpiVolume.textContent = formatInt.format(rows.length);
      els.kpiAverage.textContent = formatUSD.format(avg);
      els.kpiDelivery.textContent = `${{Math.round(deliveryRate * 100)}}%`;
      const invalidDates = rows.filter(d => !d.sale_date).length;
      const yearText = els.year.value === '__all' ? 'todos os anos' : els.year.value;
      const monthText = els.month.value === '__all' ? 'todos os meses' : els.month.options[els.month.selectedIndex].textContent;
      els.summary.innerHTML = `${{formatInt.format(rows.length)}} vendas filtradas<br>${{monthText}} / ${{yearText}}${{invalidDates ? `<br>${{invalidDates}} registos sem data válida na seleção` : ''}}`;
    }}

    function setupCanvas(canvas, cssHeight = null) {{
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.max(1, window.devicePixelRatio || 1);
      if (cssHeight) canvas.style.height = `${{cssHeight}}px`;
      const width = Math.max(320, Math.floor(rect.width));
      const height = Math.max(220, Math.floor(cssHeight || rect.height));
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      const ctx = canvas.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      return {{ ctx, width, height }};
    }}

    function clear(ctx, width, height) {{
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, width, height);
    }}

    function drawAxes(ctx, plot, yLabel, xLabel) {{
      ctx.strokeStyle = '#dfe4ea';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(plot.x, plot.y);
      ctx.lineTo(plot.x, plot.y + plot.h);
      ctx.lineTo(plot.x + plot.w, plot.y + plot.h);
      ctx.stroke();
      ctx.fillStyle = '#6d7785';
      ctx.font = '12px Segoe UI, Arial';
      ctx.fillText(yLabel, plot.x, 14);
      ctx.textAlign = 'right';
      ctx.fillText(xLabel, plot.x + plot.w, plot.y + plot.h + 34);
      ctx.textAlign = 'left';
    }}

    function drawGrid(ctx, plot, yTicks, yScale, yFormat) {{
      ctx.font = '11px Segoe UI, Arial';
      ctx.fillStyle = '#6d7785';
      ctx.strokeStyle = '#edf1f4';
      ctx.lineWidth = 1;
      yTicks.forEach(tick => {{
        const y = plot.y + plot.h - yScale(tick);
        ctx.beginPath();
        ctx.moveTo(plot.x, y);
        ctx.lineTo(plot.x + plot.w, y);
        ctx.stroke();
        ctx.fillText(yFormat(tick), 8, y + 4);
      }});
    }}

    function niceMax(value) {{
      if (value <= 0) return 1;
      const exp = Math.pow(10, Math.floor(Math.log10(value)));
      const n = value / exp;
      const step = n <= 2 ? 2 : n <= 5 ? 5 : 10;
      return step * exp;
    }}

    function showPanel(panelId, hasData) {{
      document.getElementById(panelId).classList.toggle('is-empty', !hasData);
    }}

    function drawModelScatter(rows) {{
      const canvas = document.getElementById('modelScatter');
      const {{ ctx, width, height }} = setupCanvas(canvas);
      const plot = {{ x: 64, y: 28, w: width - 92, h: height - 78 }};
      clear(ctx, width, height);
      hoverLayers.modelScatter = [];
      const map = new Map();
      rows.filter(d => d.status !== 'Cancelled').forEach(d => {{
        const current = map.get(d.model) || {{ model: d.model, volume: 0, revenue: 0, family: family(d.model) }};
        current.volume += 1;
        current.revenue += d.price;
        map.set(d.model, current);
      }});
      const points = [...map.values()].filter(d => d.volume > 0);
      showPanel('panelModelScatter', points.length > 0);
      if (!points.length) return;
      const maxX = Math.max(1, ...points.map(d => d.volume));
      const maxY = niceMax(Math.max(...points.map(d => d.revenue)));
      const xScale = v => plot.x + (v / maxX) * plot.w;
      const yScale = v => plot.y + plot.h - (v / maxY) * plot.h;
      drawAxes(ctx, plot, 'Receita', 'Volume de vendas');
      drawGrid(ctx, plot, [0, maxY * .25, maxY * .5, maxY * .75, maxY], v => (v / maxY) * plot.h, v => formatUSD.format(v).replace('.00', ''));
      ctx.fillStyle = '#6d7785';
      ctx.font = '11px Segoe UI, Arial';
      for (let i = 0; i <= maxX; i += Math.max(1, Math.ceil(maxX / 5))) {{
        const x = xScale(i);
        ctx.fillText(String(i), x - 3, plot.y + plot.h + 18);
      }}
      points.forEach(point => {{
        const x = xScale(point.volume);
        const y = yScale(point.revenue);
        const color = FAMILY_COLORS[point.family] || FAMILY_COLORS.Outro;
        const r = 6 + Math.min(8, Math.sqrt(point.revenue) / 220);
        ctx.beginPath();
        ctx.fillStyle = color;
        ctx.globalAlpha = .84;
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
        hoverLayers.modelScatter.push({{ x, y, r: r + 4, html: `<strong>${{point.model}}</strong><br>Família: ${{point.family}}<br>Volume: ${{point.volume}}<br>Receita: ${{formatUSD.format(point.revenue)}}` }});
      }});
      const families = [...new Set(points.map(d => d.family))].sort();
      document.getElementById('familyLegend').innerHTML = families.map(f => `<span><i class="swatch" style="background:${{FAMILY_COLORS[f] || FAMILY_COLORS.Outro}}"></i>${{f}}</span>`).join('');
    }}

    function drawSalespersonBars(rows) {{
      const canvas = document.getElementById('salespersonBar');
      const data = aggregate(rows, 'salesperson').sort((a, b) => b.value - a.value || a.name.localeCompare(b.name));
      const rowHeight = 26;
      const canvasHeight = Math.max(430, data.length * rowHeight + 58);
      const {{ ctx, width, height }} = setupCanvas(canvas, canvasHeight);
      clear(ctx, width, height);
      hoverLayers.salespersonBar = [];
      showPanel('panelSalesperson', data.length > 0);
      if (!data.length) return;
      const plot = {{ x: 142, y: 20, w: width - 174, h: height - 44 }};
      const max = Math.max(...data.map(d => d.value), 1);
      ctx.font = '12px Segoe UI, Arial';
      data.forEach((d, idx) => {{
        const y = plot.y + idx * rowHeight;
        const barW = (d.value / max) * plot.w;
        ctx.fillStyle = '#5e6a75';
        ctx.textAlign = 'right';
        ctx.fillText(d.name, plot.x - 10, y + 16);
        ctx.textAlign = 'left';
        ctx.fillStyle = idx < 3 ? '#b42318' : '#1f7a8c';
        ctx.fillRect(plot.x, y + 4, barW, 14);
        ctx.fillStyle = '#17202a';
        ctx.fillText(String(d.value), plot.x + barW + 7, y + 16);
        hoverLayers.salespersonBar.push({{ x: plot.x, y: y + 4, w: barW, h: 14, html: `<strong>${{d.name}}</strong><br>Vendas: ${{d.value}}` }});
      }});
    }}

    function drawStackedBars(rows) {{
      const canvas = document.getElementById('stackedBar');
      const {{ ctx, width, height }} = setupCanvas(canvas);
      clear(ctx, width, height);
      hoverLayers.stackedBar = [];
      const categoryKey = stackMode === 'payment' ? 'pay_method' : 'family';
      const enriched = rows.map(d => ({{ ...d, family: family(d.model) }}));
      const stateVolume = aggregate(enriched, 'state').sort((a, b) => b.value - a.value).slice(0, 12);
      const states = stateVolume.map(d => d.name);
      const categories = aggregate(enriched.filter(d => states.includes(d.state)), categoryKey)
        .sort((a, b) => b.value - a.value)
        .slice(0, 7)
        .map(d => d.name);
      showPanel('panelStacked', states.length > 0 && categories.length > 0);
      if (!states.length || !categories.length) return;
      document.getElementById('stackedSubtitle').textContent = stackMode === 'payment'
        ? 'Métodos de pagamento nos estados com maior volume'
        : 'Famílias de modelo nos estados com maior volume';
      const plot = {{ x: 48, y: 24, w: width - 74, h: height - 78 }};
      const barGap = 10;
      const barW = Math.max(12, (plot.w - barGap * (states.length - 1)) / states.length);
      const maxTotal = Math.max(...states.map(s => enriched.filter(d => d.state === s).length), 1);
      ctx.strokeStyle = '#edf1f4';
      ctx.fillStyle = '#6d7785';
      ctx.font = '11px Segoe UI, Arial';
      [0, .25, .5, .75, 1].forEach(p => {{
        const y = plot.y + plot.h - p * plot.h;
        ctx.beginPath();
        ctx.moveTo(plot.x, y);
        ctx.lineTo(plot.x + plot.w, y);
        ctx.stroke();
        ctx.fillText(String(Math.round(maxTotal * p)), 8, y + 4);
      }});
      states.forEach((state, idx) => {{
        const x = plot.x + idx * (barW + barGap);
        let yBase = plot.y + plot.h;
        categories.forEach((cat, ci) => {{
          const count = enriched.filter(d => d.state === state && d[categoryKey] === cat).length;
          if (!count) return;
          const h = (count / maxTotal) * plot.h;
          yBase -= h;
          const color = stackMode === 'payment' ? SERIES_COLORS[ci % SERIES_COLORS.length] : (FAMILY_COLORS[cat] || SERIES_COLORS[ci % SERIES_COLORS.length]);
          ctx.fillStyle = color;
          ctx.fillRect(x, yBase, barW, h);
          hoverLayers.stackedBar.push({{ x, y: yBase, w: barW, h, html: `<strong>${{state}}</strong><br>${{cat}}: ${{count}} vendas` }});
        }});
        ctx.save();
        ctx.translate(x + barW / 2, plot.y + plot.h + 16);
        ctx.rotate(-Math.PI / 5);
        ctx.fillStyle = '#6d7785';
        ctx.textAlign = 'right';
        ctx.fillText(state, 0, 0);
        ctx.restore();
      }});
      document.getElementById('stackLegend').innerHTML = categories.map((cat, i) => {{
        const color = stackMode === 'payment' ? SERIES_COLORS[i % SERIES_COLORS.length] : (FAMILY_COLORS[cat] || SERIES_COLORS[i % SERIES_COLORS.length]);
        return `<span><i class="swatch" style="background:${{color}}"></i>${{cat}}</span>`;
      }}).join('');
    }}

    function drawMileageScatter(rows) {{
      const canvas = document.getElementById('mileageScatter');
      const {{ ctx, width, height }} = setupCanvas(canvas);
      clear(ctx, width, height);
      hoverLayers.mileageScatter = [];
      const points = rows.filter(d => d.status !== 'Cancelled' && Number.isFinite(d.mileage) && Number.isFinite(d.price));
      showPanel('panelMileage', points.length >= 2);
      if (points.length < 2) return;
      const plot = {{ x: 64, y: 28, w: width - 92, h: height - 76 }};
      const maxX = niceMax(Math.max(...points.map(d => d.mileage)));
      const maxY = niceMax(Math.max(...points.map(d => d.price)));
      const xScale = v => plot.x + (v / maxX) * plot.w;
      const yScale = v => plot.y + plot.h - (v / maxY) * plot.h;
      drawAxes(ctx, plot, 'Preço de venda', 'Quilometragem');
      drawGrid(ctx, plot, [0, maxY * .25, maxY * .5, maxY * .75, maxY], v => (v / maxY) * plot.h, v => formatUSD.format(v).replace('.00', ''));
      ctx.fillStyle = '#6d7785';
      ctx.font = '11px Segoe UI, Arial';
      [0, .25, .5, .75, 1].forEach(p => {{
        const v = maxX * p;
        ctx.fillText(formatInt.format(Math.round(v)), xScale(v) - 10, plot.y + plot.h + 18);
      }});
      points.forEach(p => {{
        const x = xScale(p.mileage);
        const y = yScale(p.price);
        const f = family(p.model);
        ctx.fillStyle = FAMILY_COLORS[f] || FAMILY_COLORS.Outro;
        ctx.globalAlpha = .72;
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
        hoverLayers.mileageScatter.push({{ x, y, r: 8, html: `<strong>${{p.model}}</strong><br>${{p.model_year || ''}} · ${{p.status}}<br>Preço: ${{formatUSD.format(p.price)}}<br>Milhas: ${{formatInt.format(p.mileage)}}` }});
      }});
      const n = points.length;
      const sx = points.reduce((s, p) => s + p.mileage, 0);
      const sy = points.reduce((s, p) => s + p.price, 0);
      const sxx = points.reduce((s, p) => s + p.mileage * p.mileage, 0);
      const sxy = points.reduce((s, p) => s + p.mileage * p.price, 0);
      const denom = n * sxx - sx * sx;
      if (denom !== 0) {{
        const slope = (n * sxy - sx * sy) / denom;
        const intercept = (sy - slope * sx) / n;
        const y0 = intercept;
        const y1 = slope * maxX + intercept;
        ctx.strokeStyle = '#101820';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 5]);
        ctx.beginPath();
        ctx.moveTo(xScale(0), yScale(Math.max(0, y0)));
        ctx.lineTo(xScale(maxX), yScale(Math.max(0, y1)));
        ctx.stroke();
        ctx.setLineDash([]);
      }}
    }}

    function drawDonut(rows) {{
      const canvas = document.getElementById('donutChart');
      const {{ ctx, width, height }} = setupCanvas(canvas);
      clear(ctx, width, height);
      hoverLayers.donutChart = [];
      const data = aggregate(rows, 'status').sort((a, b) => b.value - a.value);
      showPanel('panelDonut', data.length > 0);
      if (!data.length) return;
      const total = data.reduce((s, d) => s + d.value, 0);
      const cx = width / 2;
      const cy = height / 2 - 8;
      const r = Math.min(width, height) * .32;
      const inner = r * .62;
      let start = -Math.PI / 2;
      data.forEach((d, idx) => {{
        const angle = (d.value / total) * Math.PI * 2;
        const end = start + angle;
        ctx.beginPath();
        ctx.arc(cx, cy, r, start, end);
        ctx.arc(cx, cy, inner, end, start, true);
        ctx.closePath();
        ctx.fillStyle = STATUS_COLORS[d.name] || SERIES_COLORS[idx % SERIES_COLORS.length];
        ctx.fill();
        hoverLayers.donutChart.push({{ cx, cy, r, inner, start, end, html: `<strong>${{d.name}}</strong><br>${{d.value}} vendas<br>${{Math.round(d.value / total * 100)}}% da seleção` }});
        start = end;
      }});
      ctx.fillStyle = '#17202a';
      ctx.textAlign = 'center';
      ctx.font = '700 24px Segoe UI, Arial';
      ctx.fillText(String(total), cx, cy - 2);
      ctx.font = '12px Segoe UI, Arial';
      ctx.fillStyle = '#6d7785';
      ctx.fillText('vendas', cx, cy + 18);
      ctx.textAlign = 'left';
      document.getElementById('statusLegend').innerHTML = data.map((d, i) => `<span><i class="swatch" style="background:${{STATUS_COLORS[d.name] || SERIES_COLORS[i % SERIES_COLORS.length]}}"></i>${{d.name}}</span>`).join('');
    }}

    function pointerInArc(layer, x, y) {{
      const dx = x - layer.cx;
      const dy = y - layer.cy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      let angle = Math.atan2(dy, dx);
      if (angle < -Math.PI / 2) angle += Math.PI * 2;
      let start = layer.start;
      let end = layer.end;
      if (start < -Math.PI / 2) start += Math.PI * 2;
      if (end < -Math.PI / 2) end += Math.PI * 2;
      return dist <= layer.r && dist >= layer.inner && angle >= start && angle <= end;
    }}

    function attachTooltip(canvasId) {{
      const canvas = document.getElementById(canvasId);
      canvas.addEventListener('mousemove', event => {{
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const layers = hoverLayers[canvasId] || [];
        let hit = null;
        for (const layer of layers) {{
          if ('r' in layer && !('inner' in layer)) {{
            const dx = x - layer.x;
            const dy = y - layer.y;
            if (Math.sqrt(dx * dx + dy * dy) <= layer.r) hit = layer;
          }} else if ('w' in layer) {{
            if (x >= layer.x && x <= layer.x + layer.w && y >= layer.y && y <= layer.y + layer.h) hit = layer;
          }} else if ('inner' in layer) {{
            if (pointerInArc(layer, x, y)) hit = layer;
          }}
        }}
        if (hit) {{
          tooltip.innerHTML = hit.html;
          tooltip.style.left = `${{event.clientX}}px`;
          tooltip.style.top = `${{event.clientY}}px`;
          tooltip.style.opacity = '1';
        }} else {{
          tooltip.style.opacity = '0';
        }}
      }});
      canvas.addEventListener('mouseleave', () => tooltip.style.opacity = '0');
    }}

    function render() {{
      refreshDependentFilters();
      Object.keys(multiFilters).forEach(updateMultiButton);
      const rows = getFilteredRows();
      updateKpis(rows);
      drawModelScatter(rows);
      drawDonut(rows);
      drawSalespersonBars(rows);
      drawStackedBars(rows);
      drawMileageScatter(rows);
    }}

    initFilters();
    ['year', 'month'].forEach(key => {{
      els[key].addEventListener('change', render);
    }});

    function closeAllMulti(except = null) {{
      document.querySelectorAll('.multi-filter.open').forEach(node => {{
        if (node.dataset.filter !== except) node.classList.remove('open');
      }});
    }}

    Object.entries(multiFilters).forEach(([key, cfg]) => {{
      const wrapper = cfg.button.closest('.multi-filter');
      cfg.button.addEventListener('click', event => {{
        event.stopPropagation();
        const willOpen = !wrapper.classList.contains('open');
        closeAllMulti(key);
        wrapper.classList.toggle('open', willOpen);
      }});
      cfg.menu.addEventListener('click', event => {{
        event.stopPropagation();
        const clearKey = event.target.dataset.clear;
        if (clearKey) {{
          filterState[clearKey].clear();
          render();
        }}
      }});
      cfg.menu.addEventListener('change', event => {{
        const input = event.target;
        if (!input || input.type !== 'checkbox') return;
        if (input.checked) {{
          filterState[key].add(input.value);
        }} else {{
          filterState[key].delete(input.value);
        }}
        render();
      }});
    }});

    document.addEventListener('click', () => closeAllMulti());

    document.getElementById('resetFilters').addEventListener('click', () => {{
      initFilters();
      render();
    }});
    document.getElementById('selectDelivered').addEventListener('click', () => {{
      filterState.status.clear();
      filterState.status.add('Delivered');
      render();
    }});
    document.getElementById('stackPayment').addEventListener('click', () => {{
      stackMode = 'payment';
      document.getElementById('stackPayment').classList.add('active');
      document.getElementById('stackFamily').classList.remove('active');
      render();
    }});
    document.getElementById('stackFamily').addEventListener('click', () => {{
      stackMode = 'family';
      document.getElementById('stackFamily').classList.add('active');
      document.getElementById('stackPayment').classList.remove('active');
      render();
    }});
    ['modelScatter', 'donutChart', 'salespersonBar', 'stackedBar', 'mileageScatter'].forEach(attachTooltip);
    window.addEventListener('resize', () => requestAnimationFrame(render));
    render();
  </script>
</body>
</html>
"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
