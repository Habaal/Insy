/* Interaktive Befunde-Seite. Daten: befunde_daten.js (const BEF), erzeugt von analyse/18_mehr_analysen.py */
(function () {
  const B = BEF;
  const C = {blue: '#2a78d6', orange: '#eb6834', aqua: '#1baf7a', gelb: '#eda100', rot: '#d03b3b', gruen: '#0ca30c', grau: '#898781', ink: '#212529', ink2: '#52514e', grid: '#e1e0d9', viol: '#4a3aa7'};
  const FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif';
  const $ = id => document.getElementById(id);
  const CFG = {responsive: true, displaylogo: false, displayModeBar: false};
  const L = e => Object.assign({paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: {family: FONT, color: C.ink2, size: 12}, margin: {l: 58, r: 12, t: 14, b: 44},
    hoverlabel: {bgcolor: '#fff', bordercolor: '#c3c2b7', font: {color: C.ink, size: 12}}}, e);
  const AX = e => Object.assign({gridcolor: C.grid, linecolor: '#c3c2b7', zerolinecolor: '#c3c2b7', tickfont: {color: '#6c6a66', size: 11}, automargin: true}, e);
  const YT = t => ({text: t, font: {size: 11, color: '#6c6a66'}, standoff: 6});
  const f0 = x => Math.round(x).toLocaleString('de-AT'), f1 = x => (Math.round(x * 10) / 10).toString().replace('.', ','), f2 = x => (Math.round(x * 100) / 100).toString().replace('.', ',');
  const ampel = v => v > 300 ? ['hoch (über 300)', C.rot] : v >= 100 ? ['erhöht (100 bis 300)', C.gelb] : ['unbedenklich (unter 100)', C.gruen];
  const badge = v => { const [t, c] = ampel(v); return `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c};margin-right:6px"></span>${t}`; };
  const mkBtns = (el, items, cb, active) => { el.innerHTML = ''; items.forEach((it, i) => { const b = document.createElement('button'); b.className = 'btn btn-sm btn-outline-secondary me-1 mb-1'; b.textContent = it[0]; b.onclick = () => { [...el.children].forEach(x => x.classList.remove('active')); b.classList.add('active'); cb(it, i); }; el.appendChild(b); if (i === (active ?? -1)) b.classList.add('active'); }); };
  const bands = (ymax) => [[0, 100, '12,163,12', .07], [100, 300, '250,178,25', .11], [300, ymax, '208,59,59', .09]].map(([a, b, c, al]) => ({type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: a, y1: b, layer: 'below', line: {width: 0}, fillcolor: `rgba(${c},${al})`}));

  /* ---------- 1. Kennzahlen */
  (function () {
    const w = B.wetter.match, lw = B.luftwechsel, g = B.grenz[0];
    const card = (l, v, n) => `<div class="col-6 col-lg-3 mb-3"><div class="border rounded p-2 h-100"><div class="text-muted small">${l}</div><div style="font-size:1.5rem;font-weight:600;line-height:1.2">${v}</div><div class="small text-muted">${n}</div></div></div>`;
    $('b-kpi').innerHTML = '<div class="row">' +
      card('Ø Wohnräume vor → nach der Anlage', `${f0(B.mittel.vor)} → ${f0(B.mittel.nach)} <small>Bq/m³</small>`, 'ohne Urlaub, Referenz 100 / 300') +
      card('Urlaub, Haus 6 Tage zu', `${f0(B.mittel.urlaub)} <small>Bq/m³</small>`, 'niemand zuhause, nach Lüften in 2 h normal') +
      card('Kühle Nächte (6–15 °C): Median', `${f0(w.vor)} → ${f0(w.nach)} <small>Bq/m³</small>`, `bei gleichem Wetter ${f0(100 * (w.nach / w.vor - 1))} %, Nächte über 60: ${f0(w.gt60_vor)} % → ${f0(w.gt60_nach)} %`) +
      card('Luftwechsel: zu → gelüftet', `${f1(lw.ach_urlaub)} → ${f1(lw.ach_lueften)} <small>pro Stunde</small>`, `Lüften wirkt etwa ${f0(lw.ach_lueften / lw.ach_urlaub)}-mal stärker`) + '</div>';
  })();

  /* ---------- 2. Zeitstrahl */
  (function () {
    const T = B.tage, el = $('b-zeit');
    const chk = {max: true, sock: true, tech: false};
    $('b-zeit-ctl').innerHTML = '<div id="zb" class="mb-2"></div><div class="mb-2"><label class="me-3"><input type="checkbox" id="z-max" checked> höchster Stundenwert des Tages</label><label class="me-3"><input type="checkbox" id="z-sock" checked> Küche Sockel (Wand)</label><label><input type="checkbox" id="z-tech"> Technikraum (Keller)</label></div>';
    const PRE = [['Gesamt', null, '<b>Was sieht man?</b> Die Wohnräume (blau) liegen fast immer im grünen Bereich. Zwei Ausreißer: der Anfang im März (damals wurde das Problem entdeckt) und der Urlaub, als das Haus geschlossen war. Rechts der gestrichelten Linie (Anlage, 24.08.) gibt es keine hohen Spitzen mehr.'],
      ['Urlaub', ['2026-07-25', '2026-08-12'], '<b>Was sieht man?</b> Grau = Urlaub (31.07. abends bis 06.08. gegen 19–20 Uhr). Alle Räume steigen auf über 300, weil nichts gelüftet wird. Nach der Rückkehr fällt es sofort.'],
      ['Anlage eingebaut', ['2026-08-05', '2026-09-20'], '<b>Was sieht man?</b> Links der gestrichelten Linie noch Spitzen, rechts verläuft alles flach. Der Sockel-Sensor (orange) fällt schon ab Mitte August.'],
      ['Überwiegend gelüftet', ['2026-03-30', '2026-06-25'], '<b>Was sieht man?</b> Unregelmäßig, aber überwiegend gelüftet (laut Hr. Grimmer). Wohnräume meist 20–40, kurze Nachtspitzen. Der Keller (grün) ist sehr niedrig, weil viel Luft ausgetauscht wurde.']];
    let range = null, txt = PRE[0][2];
    function draw() {
      const tr = [{x: T.d, y: T.og, name: 'Wohnräume (typischer Wert)', mode: 'lines', line: {color: C.blue, width: 2.2}, hovertemplate: '%{y:.0f} Bq/m³<extra>Wohnräume</extra>'}];
      if ($('z-max').checked) tr.push({x: T.d, y: T.ogmax, name: 'höchster Stundenwert', mode: 'lines', line: {color: C.blue, width: .8, dash: 'dot'}, hovertemplate: '%{y:.0f} Bq/m³<extra>höchster Stundenwert</extra>'});
      if ($('z-sock').checked) tr.push({x: T.d, y: T.sock, name: 'Küche Sockel', mode: 'lines', line: {color: C.orange, width: 1.6}, hovertemplate: '%{y:.0f} Bq/m³<extra>Küche Sockel</extra>'});
      if ($('z-tech').checked) tr.push({x: T.d, y: T.tech, name: 'Technikraum', mode: 'lines', line: {color: C.aqua, width: 1.6}, hovertemplate: '%{y:.0f} Bq/m³<extra>Technikraum</extra>'});
      const ymax = 450;
      const sh = [...bands(1000), {type: 'rect', xref: 'x', yref: 'paper', x0: '2026-07-31', x1: '2026-08-07', y0: 0, y1: 1, line: {width: 0}, fillcolor: 'rgba(137,135,129,.25)', layer: 'below'},
        {type: 'line', xref: 'x', yref: 'paper', x0: '2026-08-24', x1: '2026-08-24', y0: 0, y1: 1, line: {color: C.ink, width: 1.2, dash: 'dash'}}];
      const an = [{xref: 'x', yref: 'paper', x: '2026-08-03', y: 1, yanchor: 'bottom', text: 'Urlaub', showarrow: false, font: {size: 11}}, {xref: 'x', yref: 'paper', x: '2026-08-24', y: 1, yanchor: 'bottom', xanchor: 'left', text: 'Anlage eingebaut', showarrow: false, font: {size: 11}}];
      Plotly.react(el, tr, L({margin: {l: 58, r: 12, t: 24, b: 40}, hovermode: 'x unified', showlegend: true, legend: {orientation: 'h', y: -0.16}, shapes: sh, annotations: an,
        xaxis: AX({range: range || ['2026-03-24', '2026-10-13']}), yaxis: AX({title: YT('Radon [Bq/m³]'), range: [0, ymax], rangemode: 'tozero'})}), CFG);
      $('b-zeit-txt').innerHTML = txt;
    }
    mkBtns($('zb'), PRE, it => { range = it[1]; txt = it[2]; draw(); }, 0);
    ['z-max', 'z-sock', 'z-tech'].forEach(i => $(i).onchange = draw);
    draw();
  })();

  /* ---------- 3. Risiko-Rechner */
  (function () {
    const COEF = {icrp: 6.9e-6, unscear: 3.7e-6};
    const el = $('b-risiko');
    el.innerHTML = `
      <div class="row g-3">
        <div class="col-lg-5">
          <div id="r-pre" class="mb-2"></div>
          <label class="form-label mb-0">Radon im Haus: <b id="r-cv"></b> Bq/m³</label><input type="range" class="form-range" id="r-c" min="0" max="600" step="1" value="36">
          <label class="form-label mb-0">Aufenthalt im Haus pro Jahr: <b id="r-hv"></b> Stunden</label><input type="range" class="form-range" id="r-h" min="1000" max="8760" step="100" value="7000">
          <label class="form-label mb-0">Dosiskoeffizient</label>
          <select id="r-k" class="form-select form-select-sm mb-2"><option value="icrp">ICRP 137 (6,9 nSv je Bq·h/m³)</option><option value="unscear">UNSCEAR umgerechnet (ca. 3,7 nSv je Bq·h/m³)</option></select>
          <div class="border rounded p-2" id="r-out"></div>
        </div>
        <div class="col-lg-7"><div id="r-chart" style="height:340px"></div></div>
      </div>
      <h4 class="mt-4 h6">Jahresmittel-Schätzung mit Winterfaktor</h4>
      <p class="small text-muted mb-1">Die Messung deckt nur März bis Oktober ab. Im Winter ist Radon meist höher (Allgemeinwissen). Der Faktor ist eine Annahme, kein Messwert.</p>
      <label class="form-label mb-0">Winterfaktor: <b id="w-fv"></b> × (1 = Winter wie Sommer)</label><input type="range" class="form-range" id="w-f" min="1" max="4" step="0.1" value="1">
      <div id="w-out" class="border rounded p-2 mt-1"></div>`;
    const pts = [['Vor der Anlage', B.mittel.vor, C.orange], ['Nach der Anlage', B.mittel.nach, C.blue]];
    function calc() {
      const c = +$('r-c').value, h = +$('r-h').value, k = COEF[$('r-k').value];
      $('r-cv').textContent = c; $('r-hv').textContent = f0(h);
      const rr = 0.16 * c, dose = c * h * k;
      $('r-out').innerHTML = `<div>${badge(c)}</div><div class="mt-1">Zusätzliches Lungenkrebs-Risiko (relativ): <b>+${f1(rr)} %</b></div><div>Strahlendosis: <b>${f1(dose)} mSv pro Jahr</b></div><div class="small text-muted mt-1">Risiko: WHO, 16 % je 100 Bq/m³, langfristiger Mittelwert, linear. Dosis = Radon × Stunden × Koeffizient (ICRP, F = 0,4).</div>`;
      const x = Array.from({length: 61}, (_, i) => i * 10), tr = [{x, y: x.map(v => .16 * v), mode: 'lines', line: {color: C.ink2, width: 2}, hovertemplate: '%{x} Bq/m³: +%{y:.0f} %<extra></extra>', showlegend: false},
        {x: [c], y: [rr], mode: 'markers', marker: {size: 14, color: C.ink, symbol: 'diamond'}, hovertemplate: 'Auswahl: +%{y:.1f} %<extra></extra>', showlegend: false},
        ...pts.map((p, i) => ({x: [p[1]], y: [.16 * p[1]], mode: 'markers+text', text: [p[0]], textposition: i ? 'bottom right' : 'top left', marker: {size: 10, color: p[2]}, hovertemplate: p[0] + ': %{x:.0f} Bq/m³, +%{y:.1f} %<extra></extra>', showlegend: false}))];
      Plotly.react('r-chart', tr, L({margin: {l: 58, r: 12, t: 12, b: 48}, xaxis: AX({title: YT('Radon im Haus [Bq/m³]'), range: [0, 600]}), yaxis: AX({title: YT('zusätzliches relatives Lungenkrebs-Risiko [%]'), range: [0, 100]}),
        shapes: [{type: 'rect', xref: 'x', yref: 'paper', x0: 0, x1: 100, y0: 0, y1: 1, fillcolor: 'rgba(12,163,12,.07)', line: {width: 0}, layer: 'below'}, {type: 'rect', xref: 'x', yref: 'paper', x0: 100, x1: 300, y0: 0, y1: 1, fillcolor: 'rgba(250,178,25,.11)', line: {width: 0}, layer: 'below'}, {type: 'rect', xref: 'x', yref: 'paper', x0: 300, x1: 600, y0: 0, y1: 1, fillcolor: 'rgba(208,59,59,.09)', line: {width: 0}, layer: 'below'}],
        annotations: [{x: 100, y: 1, xref: 'x', yref: 'paper', text: 'WHO 100', showarrow: false, yanchor: 'bottom', font: {size: 10}}, {x: 300, y: 1, xref: 'x', yref: 'paper', text: 'Österreich 300', showarrow: false, yanchor: 'bottom', font: {size: 10}}]}), CFG);
    }
    mkBtns($('r-pre'), [['Vor der Anlage', B.mittel.vor], ['Nach der Anlage', B.mittel.nach], ['Urlaub (leeres Haus)', B.mittel.urlaub], ['WHO-Wert', 100], ['Österreich-Referenzwert', 300]], it => { $('r-c').value = Math.round(it[1]); calc(); });
    ['r-c', 'r-h', 'r-k'].forEach(i => $(i).oninput = calc); calc();
    function winter() {
      const f = +$('w-f').value; $('w-fv').textContent = f1(f);
      const a = B.mittel.vor * f, b = B.mittel.nach * f;
      $('w-out').innerHTML = `Vor der Anlage: <b>${f0(a)}</b> Bq/m³ (${badge(a)}) · Nach der Anlage: <b>${f0(b)}</b> Bq/m³ (${badge(b)}).<div class="small text-muted mt-1">Ab Faktor ${f1(100 / B.mittel.vor)} läge das Haus vor der Anlage über 100, nach der Anlage ab ${f1(100 / B.mittel.nach)}. Über 300 erst ab Faktor ${f1(300 / B.mittel.nach)} (nach der Anlage).</div>`;
    }
    $('w-f').oninput = winter; winter();
  })();

  /* ---------- 4. Lüften: Urlaub als Experiment + Simulator */
  (function () {
    const lw = B.luftwechsel, n = lw.rn.length, t0 = Date.parse(lw.t0.replace(' ', 'T') + 'Z');
    const X = Array.from({length: n}, (_, i) => new Date(t0 + i * 36e5).toISOString().slice(0, 16).replace('T', ' '));
    const i0 = Math.round((Date.parse('2026-07-31T18:00Z') - t0) / 36e5), c0 = lw.rn[i0];
    const fit = X.map((_, i) => (i < i0 || i > i0 + 120) ? null : Math.round(lw.sat - (lw.sat - c0) * Math.exp(-lw.Lges * (i - i0))));
    Plotly.react($('b-urlaub'), [
      {x: X, y: lw.rn, name: 'Radon Wohnräume', mode: 'lines', line: {color: C.blue, width: 2}, xaxis: 'x', yaxis: 'y', hovertemplate: '%{y:.0f} Bq/m³<extra>Radon</extra>'},
      {x: X, y: fit, name: 'Modell (Sättigung ' + lw.sat + ' Bq/m³)', mode: 'lines', line: {color: C.orange, width: 2, dash: 'dash'}, xaxis: 'x', yaxis: 'y', hovertemplate: '%{y:.0f} Bq/m³<extra>Modell</extra>'},
      {x: X, y: lw.co2k, name: 'CO₂ Küche', mode: 'lines', line: {color: C.aqua, width: 1.6}, xaxis: 'x2', yaxis: 'y2', hovertemplate: '%{y:.0f} ppm<extra>CO₂ Küche</extra>'},
      {x: X, y: lw.co2s, name: 'CO₂ Schlafzimmer', mode: 'lines', line: {color: C.viol, width: 1.6}, xaxis: 'x2', yaxis: 'y2', hovertemplate: '%{y:.0f} ppm<extra>CO₂ Schlafzimmer</extra>'}],
      L({margin: {l: 58, r: 12, t: 20, b: 40}, hovermode: 'x unified', legend: {orientation: 'h', y: -0.12}, xaxis: AX({anchor: 'y', showticklabels: false}), xaxis2: AX({anchor: 'y2', matches: 'x', tickformat: '%d.%m.'}),
        yaxis: AX({domain: [0.38, 1], title: YT('Radon [Bq/m³]'), rangemode: 'tozero'}), yaxis2: AX({domain: [0, 0.3], title: YT('CO₂ [ppm]')}),
        shapes: [{type: 'rect', xref: 'x', yref: 'paper', x0: '2026-07-31 18:00', x1: '2026-08-06 19:30', y0: 0, y1: 1, fillcolor: 'rgba(137,135,129,.22)', line: {width: 0}, layer: 'below'}],
        annotations: [{xref: 'x', yref: 'paper', x: '2026-08-03 06:00', y: 1, yanchor: 'bottom', text: 'Urlaub', showarrow: false, font: {size: 11}}]}), CFG);
    $('b-urlaub-txt').innerHTML = `<b>Was sieht man?</b> Während des Urlaubs (grau) ist das Haus zu und leer. Das CO₂ fällt langsam auf Außenluft-Niveau (etwa 405 ppm), Radon steigt in fünf Tagen auf etwa ${lw.sat} Bq/m³ und bleibt dort. Aus dem CO₂-Abfall ergibt sich ein Luftwechsel von nur <b>${f2(lw.ach_urlaub)} pro Stunde</b> (ca. 3 % der Raumluft pro Stunde). Als Radon-Aufbau passt dazu eine Quellstärke von etwa <b>${f0(lw.S)} Bq/m³ pro Stunde</b>. Nach der Rückkehr lüftet jemand: der Luftwechsel steigt auf etwa <b>${f1(lw.ach_lueften)} pro Stunde</b> (Halbwertszeit ca. 26 Minuten), Radon fällt in zwei Stunden auf etwa ${lw.basis_nach} Bq/m³. <span class="text-muted">Einzonen-Näherung, grobe Schätzung.</span>`;

    /* Simulator */
    $('b-sim').innerHTML = `<div class="row g-3"><div class="col-lg-5">
      <label class="form-label mb-0">Luftwechsel: <b id="s-av"></b> pro Stunde</label><input type="range" class="form-range" id="s-a" min="0" max="100" step="1" value="40">
      <label class="form-label mb-0">Quellstärke: <b id="s-sv"></b> Bq/m³ pro Stunde</label><input type="range" class="form-range" id="s-s" min="2" max="30" step="0.5" value="${lw.S}">
      <label><input type="checkbox" id="s-anl"> Anlage: Quelle um 23 % reduziert (Annahme aus dem Vergleich bei gleichem Wetter)</label>
      <div class="border rounded p-2 mt-2" id="s-out"></div></div><div class="col-lg-7"><div id="s-chart" style="height:320px"></div></div></div>`;
    const ach = v => Math.pow(10, -2 + 2.4 * v / 100); /* 0,01 bis ca. 2,5 pro Stunde (log) */
    const LR = 0.00755;
    function sim() {
      const a = ach(+$('s-a').value), S0 = +$('s-s').value, S = S0 * ($('s-anl').checked ? 0.77 : 1), ss = S / (a + LR);
      $('s-av').textContent = f2(a); $('s-sv').textContent = f1(S);
      const alltag = S / B.mittel.vor - LR;
      $('s-out').innerHTML = `<div>Gleichgewicht: <b>${f0(ss)} Bq/m³</b></div><div>${badge(ss)}</div><div class="small text-muted mt-1">Gleichgewicht = Quellstärke / (Luftwechsel + Zerfall 0,0076 pro Stunde). Der gemessene Alltagswert (Ø ${f0(B.mittel.vor)}) entspräche bei dieser Quelle einem Luftwechsel von etwa <b>${f2(alltag)} pro Stunde</b>: im Alltag wird also viel gelüftet.</div>`;
      const x = Array.from({length: 121}, (_, i) => Math.pow(10, -2 + 2.4 * i / 120)), y = x.map(v => S / (v + LR));
      Plotly.react('s-chart', [{x, y, mode: 'lines', line: {color: C.ink2, width: 2}, hovertemplate: 'Luftwechsel %{x:.2f}/h: %{y:.0f} Bq/m³<extra></extra>', showlegend: false},
        {x: [a], y: [ss], mode: 'markers', marker: {size: 13, color: C.ink, symbol: 'diamond'}, hovertemplate: 'Auswahl: %{y:.0f} Bq/m³<extra></extra>', showlegend: false},
        {x: [lw.ach_urlaub, alltag, lw.ach_lueften], y: [S / (lw.ach_urlaub + LR), B.mittel.vor, S / (lw.ach_lueften + LR)], mode: 'markers+text', text: ['Haus zu', 'Alltag', 'Fenster auf'], textposition: ['top right', 'top right', 'top left'], marker: {size: 9, color: C.orange}, hoverinfo: 'skip', showlegend: false}],
        L({margin: {l: 58, r: 12, t: 12, b: 48}, xaxis: AX({type: 'log', title: YT('Luftwechsel [1/h], logarithmisch'), range: [-2, 0.4]}), yaxis: AX({title: YT('Radon im Gleichgewicht [Bq/m³]'), range: [0, 600]}), shapes: bands(600)}), CFG);
    }
    ['s-a', 's-s', 's-anl'].forEach(i => $(i).oninput = sim); sim();
  })();

  /* ---------- 5. Wetter */
  (function () {
    const W = B.wetter, V = {tout: ['Außentemperatur [°C]', 'Je kälter es draußen ist, desto mehr Radon im Haus. Gründe (übliche Erklärung, nicht aus den Quellen geprüft): Der Kamineffekt des beheizten Hauses saugt Bodenluft an, und es wird weniger gelüftet.'],
      dT: ['Temperaturunterschied innen minus außen [°C]', 'Je größer der Unterschied, desto stärker saugt das warme Haus Luft aus dem Boden nach (Kamineffekt, übliche Erklärung). Hier der stärkste Einzelfaktor.'],
      wind: ['Wind in 10 m Höhe [km/h]', 'Wind tauscht Luft aus und verdünnt Radon. Vor der Anlage kaum erkennbar, danach deutlicher (nur 50 Nächte, daher unsicher).'],
      dp12: ['Luftdruckänderung der letzten 12 h [hPa]', 'Fallender Druck kann Bodenluft herausziehen (übliche Erklärung). Der Zusammenhang ist hier schwach.'],
      soil: ['Bodentemperatur in 54 cm Tiefe [°C]', 'Folgt der Jahreszeit. Warmer Boden und viel Radon schließen sich hier aus: im Sommer ist es niedriger.']};
    const sel = $('w-var'); Object.entries(V).forEach(([k, v]) => { const o = document.createElement('option'); o.value = k; o.textContent = v[0]; sel.appendChild(o); });
    function scatter() {
      const k = sel.value, d = W.tage.filter(r => r[k] != null);
      const mk = (post, name, col) => { const s = d.filter(r => r.post === post); return {x: s.map(r => r[k]), y: s.map(r => r.og), text: s.map(r => r.d), mode: 'markers', name, marker: {size: 7, color: col, opacity: .75}, hovertemplate: '%{text}<br>' + V[k][0] + ': %{x:.1f}<br>Radon nachts: %{y:.0f} Bq/m³<extra></extra>'}; };
      Plotly.react('w-sc', [mk(0, 'vor der Anlage', C.orange), mk(1, 'nach der Anlage', C.blue)], L({margin: {l: 58, r: 12, t: 12, b: 48}, legend: {orientation: 'h', y: -0.22}, xaxis: AX({title: YT(V[k][0])}), yaxis: AX({title: YT('Radon in den Wohnräumen, nachts 2–6 Uhr [Bq/m³]'), range: [0, Math.max(...d.map(r => r.og)) * 1.15]}), shapes: bands(1000)}), CFG);
      const c = W.cor;
      $('w-txt').innerHTML = `<b>Was sieht man?</b> Jeder Punkt ist eine Nacht (2–6 Uhr). ${V[k][1]} <br><b>Zusammenhang (Spearman-Korrelation, −1 bis +1):</b> vor der Anlage <b>${c.vor[k] ?? '–'}</b>, nach der Anlage <b>${c.nach[k] ?? '–'}</b>. Je näher an ±1, desto klarer der Zusammenhang; 0 = keiner.`;
    }
    sel.onchange = scatter; scatter();
    const bn = W.bins.filter(b => b.m0 != null && b.m1 != null);
    Plotly.react('w-bins', [{type: 'bar', x: bn.map(b => b.bin), y: bn.map(b => b.m0), name: 'vor der Anlage', marker: {color: C.orange}, text: bn.map(b => 'n=' + b.n0), hovertemplate: '%{x} °C<br>Median %{y:.0f} Bq/m³ (%{text})<extra>vor</extra>'},
      {type: 'bar', x: bn.map(b => b.bin), y: bn.map(b => b.m1), name: 'nach der Anlage', marker: {color: C.blue}, text: bn.map(b => 'n=' + b.n1), hovertemplate: '%{x} °C<br>Median %{y:.0f} Bq/m³ (%{text})<extra>nach</extra>'}],
      L({barmode: 'group', margin: {l: 58, r: 12, t: 12, b: 60}, legend: {orientation: 'h', y: -0.3}, xaxis: AX({title: YT('Außentemperatur in der Nacht [°C]')}), yaxis: AX({title: YT('Radon nachts, Median [Bq/m³]'), rangemode: 'tozero'})}), CFG);
    const rg = W.reg, pc = v => 100 * (Math.exp(v) - 1);
    Plotly.react('w-reg', [{type: 'bar', orientation: 'h', y: rg.map(r => r.name), x: rg.map(r => pc(r.b)), marker: {color: rg.map(r => r.name === 'nach Anlage' ? C.blue : C.grau)},
      error_x: {type: 'data', symmetric: false, array: rg.map(r => pc(r.hi) - pc(r.b)), arrayminus: rg.map(r => pc(r.b) - pc(r.lo)), color: C.ink2}, hovertemplate: '%{y}: %{x:+.0f} %<extra></extra>'}],
      L({margin: {l: 150, r: 20, t: 10, b: 44}, xaxis: AX({title: YT('Änderung des Radons nachts [%] bei sonst gleichen Bedingungen'), zeroline: true}), yaxis: AX({autorange: 'reversed'})}), CFG);
    $('w-regtxt').innerHTML = `Mehrfach-Regression (log Radon nachts, ${W.n} Nächte, R² = ${f2(W.r2)}). Balken = geschätzte Wirkung, Strich = 95-%-Bereich (Bootstrap). Wind, Temperaturunterschied und Druckänderung sind je pro eine Standardabweichung angegeben. <b>Nach der Anlage ${f0(pc(rg[3].b))} % (${f0(pc(rg[3].lo))} bis ${f0(pc(rg[3].hi))} %)</b>. Der Bereich ist eher zu eng, weil aufeinanderfolgende Nächte ähnlich sind und das Lüften nicht im Modell steckt.`;
  })();

  /* ---------- 6. Tagesrhythmus */
  (function () {
    const P = B.wochentag, hr = Array.from({length: 24}, (_, i) => i + ':00');
    mkBtns($('t-btn'), [['Werktag', 'werktag'], ['Wochenende', 'wochenende'], ['beide']], it => draw(it[1]), 2);
    function draw(w) {
      const ks = w ? [w] : ['werktag', 'wochenende'], col = {werktag: C.blue, wochenende: C.orange}, nm = {werktag: 'Montag–Freitag', wochenende: 'Samstag/Sonntag'};
      Plotly.react('t-rn', ks.map(k => ({x: hr, y: P[k].rn, name: nm[k], mode: 'lines', line: {color: col[k], width: 2.4}, hovertemplate: '%{y:.0f} Bq/m³<extra>' + nm[k] + '</extra>'})), L({margin: {l: 58, r: 12, t: 12, b: 36}, hovermode: 'x unified', xaxis: AX({tickvals: [0, 3, 6, 9, 12, 15, 18, 21].map(h => h + ':00')}), yaxis: AX({title: YT('Radon Wohnräume [Bq/m³]'), rangemode: 'tozero'})}), CFG);
      Plotly.react('t-co2', ks.map(k => ({x: hr, y: P[k].co2, name: nm[k], mode: 'lines', line: {color: col[k], width: 2.4}, hovertemplate: '%{y:.0f} ppm<extra>' + nm[k] + '</extra>'})), L({margin: {l: 58, r: 12, t: 12, b: 36}, hovermode: 'x unified', xaxis: AX({tickvals: [0, 3, 6, 9, 12, 15, 18, 21].map(h => h + ':00')}), yaxis: AX({title: YT('CO₂ Küche [ppm]')})}), CFG);
    }
    draw(null);
    const n = B.nacht;
    $('t-txt').innerHTML = `<b>Was sieht man?</b> Oben der übliche Radonwert je Uhrzeit, unten das CO₂ in der Küche (zeigt, wann jemand im Raum ist). Radon steigt nachts und fällt tagsüber. Werktag und Wochenende unterscheiden sich kaum (Median über den ganzen Tag 29,5 gegen 30,8 Bq/m³). <b>Nachtanstieg</b> (22 → 5 Uhr): vor der Anlage im Mittel <b>${f1(n.vor[0])} Bq/m³ pro Stunde</b> (obere 25 % der Nächte über ${f1(n.vor[1])}), nach der Anlage <b>${f1(n.nach[0])}</b> (über ${f1(n.nach[1])}).`;
  })();

  /* ---------- 7. Raumluft */
  (function () {
    const M = B.luft.monate;
    const IND = {co2: ['CO₂ über 1000 ppm (Anteil der Stunden, %)', 'co2_{}_gt1000', 'UBA-Leitwert: unter 1000 ppm hygienisch unbedenklich, 1000–2000 auffällig, über 2000 inakzeptabel (laut Suchergebnis zu den UBA-Leitwerten, nicht direkt gelesen). Höchster Stundenwert hier: 1618 ppm (Küche, Oktober). Über 2000 ppm kam nie vor.'],
      t26: ['Temperatur über 26 °C (Anteil der Stunden, %)', 't_{}_gt26', 'Eigene Schwelle als Komfortgrenze (nicht aus einer Quelle). Das Schlafzimmer ist im Sommer oft warm: im August in knapp der Hälfte der Stunden über 26 °C.'],
      rh60: ['Luftfeuchte über 60 % (Anteil der Stunden, %)', 'rh_{}_gt60', 'UBA: 40–60 % relative Feuchte halten das Schimmelrisiko gering, über 60 % steigt es (laut Suchergebnis). Feuchte wird erst ab 10.07. gemessen.'],
      rh70: ['Luftfeuchte über 70 % (Anteil der Stunden, %)', 'rh_{}_gt70', 'Über 70 % über längere Zeit kann Schimmel entstehen (Wiesbadener Lüftungs-Faltblatt laut Suchergebnis). Das kam kaum vor.']};
    const sel = $('l-ind'); Object.entries(IND).forEach(([k, v]) => { const o = document.createElement('option'); o.value = k; o.textContent = v[0]; sel.appendChild(o); });
    function draw() {
      const k = sel.value, key = IND[k][1];
      Plotly.react('l-chart', [['K', 'Küche', C.aqua], ['S', 'Schlafzimmer', C.viol]].map(([c, n, col]) => ({type: 'bar', x: M.map(m => m.monat), y: M.map(m => m[key.replace('{}', c)]), name: n, marker: {color: col}, hovertemplate: '%{x}: %{y:.1f} %<extra>' + n + '</extra>'})),
        L({barmode: 'group', margin: {l: 58, r: 12, t: 12, b: 50}, legend: {orientation: 'h', y: -0.2}, yaxis: AX({title: YT(IND[k][0]), rangemode: 'tozero'})}), CFG);
      $('l-txt').innerHTML = `<b>Was sieht man?</b> ${IND[k][2]}`;
    }
    sel.onchange = draw; draw();
    const nc = B.luft.nacht;
    $('l-nacht').innerHTML = `<b>Schlafzimmer nachts</b> (23–6 Uhr, ${nc.n} Nächte ohne Urlaub): CO₂ im Mittel <b>${nc.med} ppm</b> (Median), nur <b>${f0(nc.gt1000)} %</b> der Nächte im Mittel über 1000 ppm, keine über 1400 ppm. Die Luft im Schlafzimmer ist also meist gut (vermutlich wird nachts gelüftet).`;
  })();

  /* ---------- 8. Räume und Phasen */
  (function () {
    const G = B.grenz, PH = [['Vor der Anlage (ab 01.04., ohne Urlaub)', 'vor'], ['Urlaub (01.–06.08.)', 'urlaub'], ['Nach der Anlage (ab 24.08.)', 'nach']];
    const MT = [['Mittelwert [Bq/m³]', 'mean'], ['Stunden über 100 [%]', 'gt100'], ['Stunden über 300 [%]', 'gt300'], ['95 %-Wert [Bq/m³]', 'p95'], ['Höchster Stundenwert [Bq/m³]', 'max']];
    let ph = 'vor', mt = 'mean';
    mkBtns($('g-ph'), PH, it => { ph = it[1]; draw(); }, 0); mkBtns($('g-mt'), MT, it => { mt = it[1]; draw(); }, 0);
    function draw() {
      const v = G.map(r => r[ph][mt]), isRn = mt === 'mean' || mt === 'p95' || mt === 'max';
      Plotly.react('g-chart', [{type: 'bar', x: G.map(r => r.raum), y: v, marker: {color: v.map(x => isRn ? (x > 300 ? C.rot : x >= 100 ? C.gelb : C.gruen) : C.blue)}, hovertemplate: '%{x}: %{y:.1f}<extra></extra>'}],
        L({margin: {l: 58, r: 12, t: 12, b: 60}, xaxis: AX({}), yaxis: AX({title: YT(MT.find(m => m[1] === mt)[0]), rangemode: 'tozero'}), shapes: isRn ? [] : []}), CFG);
      $('g-txt').innerHTML = `<b>Was sieht man?</b> ${isRn ? 'Balkenfarbe = Ampel (grün unter 100, gelb 100–300, rot über 300).' : 'Anteil der Stunden, in denen der Raum über dem Wert lag.'} Küche Sockel, Technikraum und Werkstatt (Wand und Keller) lagen vor der Anlage häufiger über 100 als die Wohnräume. Nach der Anlage fast nirgends mehr. Stunden: ${f0(G[0][ph].n)} je Wohnraum-Sensor.`;
    }
    draw();
  })();

  /* ---------- 9. Ereignisse */
  (function () {
    const E = B.ereignisse.map((e, i) => ({...e, nr: i + 1})), flt = {'Phase': true, 'Wendepunkt': true, 'Radon-Ereignis': true, 'Sensor-Reset': true};
    const dmy = s => s.slice(8, 10) + '.' + s.slice(5, 7) + '. ' + s.slice(11, 16);
    $('e-flt').innerHTML = Object.keys(flt).map(k => `<label class="me-3"><input type="checkbox" checked data-k="${k}"> ${k}</label>`).join('');
    [...$('e-flt').querySelectorAll('input')].forEach(i => i.onchange = () => { flt[i.dataset.k] = i.checked; tab(); });
    const ein = e => e.art === 'Radon-Ereignis' ? (e.peak >= 300 ? 'hoch' : e.peak >= 200 ? 'erhöht' : 'leicht erhöht') : e.art === 'Sensor-Reset' ? 'technisch' : '';
    function tab() {
      $('e-tab').innerHTML = '<thead><tr><th>#</th><th>Art</th><th>Von</th><th>Bis</th><th>Räume</th><th class="text-end">Höchster Wert</th><th>Einordnung</th><th>Notiz</th></tr></thead><tbody>' +
        E.filter(e => flt[e.art]).map(e => `<tr style="cursor:pointer" data-i="${e.nr - 1}"><td>${e.nr}</td><td>${e.art}</td><td style="white-space:nowrap">${dmy(e.von)}</td><td style="white-space:nowrap">${e.bis === e.von ? '–' : dmy(e.bis)}</td><td>${e.raeume}</td><td class="text-end">${e.peak ?? ''}</td><td>${ein(e)}</td><td>${e.notiz || ''}</td></tr>`).join('') + '</tbody>';
      [...$('e-tab').querySelectorAll('tbody tr')].forEach(tr => tr.onclick = () => zoom(E[+tr.dataset.i]));
    }
    function zoom(e) {
      const a = Date.parse(e.von.replace(' ', 'T') + 'Z'), b = Date.parse(e.bis.replace(' ', 'T') + 'Z'), pad = Math.max(36 * 36e5, (b - a) / 2 + 24 * 36e5), mid = (a + b) / 2;
      const f = t => new Date(t).toISOString().slice(0, 16).replace('T', ' ');
      $('e-sel').innerHTML = `<b>#${e.nr} ${e.art}</b>, ${dmy(e.von)}${e.bis === e.von ? '' : ' bis ' + dmy(e.bis)}${e.notiz ? ': ' + e.notiz : ''}`;
      Plotly.relayout('e-chart', {'xaxis.range': [f(mid - pad), f(mid + pad)]});
    }
    tab();
    const T = B.tage, ex = E.filter(e => e.art === 'Radon-Ereignis');
    Plotly.react('e-chart', [{x: T.d, y: T.ogmax, name: 'höchster Stundenwert (Wohnräume)', mode: 'lines', line: {color: C.blue, width: 1.2}, hovertemplate: '%{y:.0f} Bq/m³<extra></extra>'},
      {x: ex.map(e => e.von.slice(0, 10)), y: ex.map(e => e.peak), text: ex.map(e => '#' + e.nr + ' ' + e.raeume), mode: 'markers', name: 'erkanntes Ereignis', marker: {size: 8, color: C.orange, symbol: 'triangle-down'}, hovertemplate: '%{text}<br>Höchster Wert %{y} Bq/m³<extra></extra>'}],
      L({margin: {l: 58, r: 12, t: 12, b: 40}, legend: {orientation: 'h', y: -0.18}, xaxis: AX({range: ['2026-03-24', '2026-10-13']}), yaxis: AX({title: YT('Radon [Bq/m³]'), range: [0, 520]}), shapes: bands(1000)}), CFG);
  })();

  /* ---------- 10. Messgenauigkeit */
  (function () {
    const r = B.rauschen;
    Plotly.react('n-chart', [{type: 'bar', x: ['Wert unter 50', 'Wert 50 bis 150', 'Wert über 150'], y: [r['unter 50'], r['50-150'], r['ueber 150']], marker: {color: C.blue}, hovertemplate: '%{x}: ±%{y:.0f} Bq/m³<extra></extra>'}],
      L({margin: {l: 58, r: 12, t: 12, b: 44}, yaxis: AX({title: YT('Streuung zwischen zwei Sensoren (1 σ) [Bq/m³]'), rangemode: 'tozero'}), xaxis: AX({title: YT('Radonwert im Raum [Bq/m³]')})}), CFG);
    const H = B.herbst;
    Plotly.react('n-herbst', [{x: H.map(h => h.tout), y: H.map(h => h.og), text: H.map(h => 'Woche bis ' + h.w), mode: 'markers+text', textposition: 'top center', marker: {size: 10, color: C.orange}, hovertemplate: '%{text}<br>Außentemp. %{x:.1f} °C<br>Radon %{y:.0f} Bq/m³<extra></extra>'}],
      L({margin: {l: 58, r: 12, t: 12, b: 48}, xaxis: AX({title: YT('Außentemperatur, Wochenmittel [°C]')}), yaxis: AX({title: YT('Radon Wohnräume, Wochenmedian [Bq/m³]'), rangemode: 'tozero'})}), CFG);
    $('n-txt').innerHTML = `<b>Was sieht man?</b> Links: Zwei gleiche Sensoren im selben Zustand weichen bei niedrigen Werten um etwa ±${f0(r['unter 50'])} Bq/m³ voneinander ab, bei hohen um ±${f0(r['ueber 150'])} (Streuung 1 σ der Stundenwerte). Hr. Grimmers Angabe von ±30 passt als Obergrenze für einzelne Stundenwerte. Über viele Stunden gemittelt ist die Streuung viel kleiner. Rechts: Im Herbst (Wochen bis 11.10.) steigt das Radon mit sinkender Außentemperatur (Spearman ${f2(-0.75)}), alle Sensoren gemeinsam. Das spricht dafür, dass der Anstieg von etwa 22 auf 35–42 Bq/m³ eher jahreszeitlich als Zufall ist, aber weiter weit unter 100 liegt.`;
  })();
})();
