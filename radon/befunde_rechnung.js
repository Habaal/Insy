/* Abschnitt "Nachgerechnet": Aufladekurve, Radon-Zufluss, Druck (Kamineffekt). Daten: BEF.modell aus analyse/20_aufladekurve.py */
(function () {
  const M = BEF.modell, $ = id => document.getElementById(id);
  const C = {blue: '#2a78d6', orange: '#eb6834', ink: '#212529', ink2: '#52514e', grid: '#e1e0d9'};
  const CFG = {responsive: true, displaylogo: false, displayModeBar: false};
  const L = e => Object.assign({paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: {family: 'system-ui, -apple-system, "Segoe UI", sans-serif', color: C.ink2, size: 12}, margin: {l: 58, r: 12, t: 14, b: 48}, hoverlabel: {bgcolor: '#fff', font: {color: C.ink}}}, e);
  const AX = e => Object.assign({gridcolor: C.grid, linecolor: '#c3c2b7', zerolinecolor: '#c3c2b7', tickfont: {color: '#6c6a66', size: 11}, automargin: true}, e);
  const YT = t => ({text: t, font: {size: 11, color: '#6c6a66'}, standoff: 6});
  const de = (x, d) => (Math.round(x * 10 ** d) / 10 ** d).toString().replace('.', ',');
  const big = x => Math.round(x).toLocaleString('de-AT');

  /* Kennzahlen der Aufladekurve */
  $('m-fit').innerHTML = `<table class="table table-sm"><thead><tr><th>Raum</th><th class="text-end">Endwert (Sättigung)</th><th class="text-end">Zeitkonstante τ</th><th class="text-end">Passgenauigkeit R²</th></tr></thead><tbody>` +
    Object.entries(M.zimmer).map(([k, v]) => `<tr><td>${k}</td><td class="text-end">${v.css} Bq/m³</td><td class="text-end">${de(v.tau, 1)} h</td><td class="text-end">${de(v.r2, 3)}</td></tr>`).join('') + '</tbody></table>';

  /* Rechner: wie viel kommt ins Haus */
  $('m-calc').innerHTML = `<div class="row g-3"><div class="col-lg-6">
      <label class="form-label mb-0">Luftvolumen des Hauses: <b id="m-vv"></b> m³</label><input type="range" class="form-range" id="m-v" min="100" max="1000" step="10" value="400">
      <label class="form-label mb-0">Radon in der Bodenluft: <b id="m-bv"></b> kBq/m³</label><input type="range" class="form-range" id="m-b" min="5" max="150" step="1" value="40">
      <label class="form-label mb-0">Quellstärke</label><select id="m-s" class="form-select form-select-sm"><option value="fit">aus der Aufladekurve: ${de(M.S_fit, 1)} Bq/m³ pro Stunde</option><option value="co2">mit CO₂-Luftwechsel: ${de(M.S_co2, 1)} Bq/m³ pro Stunde</option></select>
    </div><div class="col-lg-6"><div class="border rounded p-2 h-100" id="m-out"></div></div></div>`;
  function calc() {
    const V = +$('m-v').value, Cb = +$('m-b').value * 1000, S = $('m-s').value === 'fit' ? M.S_fit : M.S_co2;
    $('m-vv').textContent = V; $('m-bv').textContent = $('m-b').value;
    const Bqh = S * V, Lh = Bqh / Cb * 1000;
    $('m-out').innerHTML = `<div>Radon-Zufluss ins ganze Haus: <b>${big(Bqh)} Bq pro Stunde</b> (${big(Bqh * 24 / 1000)} kBq pro Tag)</div>
      <div class="mt-1">Das entspricht etwa <b>${de(Lh, 0)} Liter Bodenluft pro Stunde</b> (${de(Lh * 24 / 1000, 1)} m³ pro Tag), wenn das Radon nur mit der Bodenluft hereinkommt.</div>
      <div class="mt-1">Zum Vergleich: Der Luftwechsel im geschlossenen Haus tauscht etwa <b>${de(M.ach_co2 * V, 0)} m³ pro Stunde</b> aus. Die Bodenluft ist also ein winziger Teil der Luft, bringt aber das ganze Radon.</div>
      <div class="small text-muted mt-2">Volumen und Bodenluft-Radon sind <b>nicht gemessen</b>, sondern Annahmen zum Ausprobieren. Ergebnis = Quellstärke × Volumen.</div>`;
  }
  ['m-v', 'm-b', 'm-s'].forEach(i => $(i).oninput = calc); calc();

  /* Druck: Radon nachts gegen Kamineffekt-Druck, vor/nach Anlage */
  function ols(x, y) { const n = x.length, mx = x.reduce((a, b) => a + b) / n, my = y.reduce((a, b) => a + b) / n; let sxy = 0, sxx = 0; x.forEach((v, i) => { sxy += (v - mx) * (y[i] - my); sxx += (v - mx) ** 2; }); const b = sxy / sxx; return [my - b * mx, b]; }
  function druck() {
    const h = +$('m-h').value, k = h / 3; $('m-hv').textContent = de(h, 1);
    const tr = [];
    [[0, 'vor der Anlage', C.orange], [1, 'nach der Anlage', C.blue]].forEach(([p, nm, col]) => {
      const s = M.nacht.filter(r => r.post === p), x = s.map(r => r.dp * k), y = s.map(r => r.og);
      tr.push({x, y, text: s.map(r => r.d), mode: 'markers', name: nm, marker: {size: 7, color: col, opacity: .7}, hovertemplate: '%{text}<br>Druck %{x:.2f} Pa<br>Radon nachts %{y:.0f} Bq/m³<extra></extra>'});
      const [a, b] = ols(x, y), xs = [Math.min(...x), Math.max(...x)];
      tr.push({x: xs, y: xs.map(v => a + b * v), mode: 'lines', line: {color: col, width: 2}, hoverinfo: 'skip', showlegend: false});
    });
    Plotly.react('m-dp', tr, L({legend: {orientation: 'h', y: -0.22}, xaxis: AX({title: YT('Unterdruck im Haus durch Kamineffekt, nachts [Pa]'), zeroline: true}), yaxis: AX({title: YT('Radon Wohnräume, nachts 2–6 Uhr [Bq/m³]'), rangemode: 'tozero'})}), CFG);
    const A = M.anlage, dp = M.dp;
    $('m-dptxt').innerHTML = `<b>Was sieht man?</b> Jeder Punkt ist eine Nacht. Nach rechts wird der Unterdruck stärker, mit dem das warme Haus Bodenluft ansaugt (berechnet aus Innen- und Außentemperatur, Höhe ${de(h, 1)} m über der neutralen Zone). Mehr Unterdruck heißt mehr Radon. Die blaue Linie (nach der Anlage) liegt tiefer: Bei gleichem Druck ist weniger Radon da.<br>
      <b>Typischer Unterdruck:</b> im Mittel ${de(dp.h3_med * k, 1)} Pa, in den kältesten Stunden bis ${de(dp.h3_p95 * k, 1)} Pa (95-%-Wert). Im Urlaub (heiße Tage) etwa <b>${de(dp.urlaub * k, 2)} Pa</b>, also praktisch null, und trotzdem stieg Radon auf ${M.css} Bq/m³.<br>
      <b>Was leistet die Anlage?</b> Ihr Effekt (${de(A.anlage_bq, 0)} Bq/m³ nachts bei gleichem Wetter) entspricht einer Verschiebung um ${de(A.shift_K, 1)} K Temperaturunterschied, also einem <b>Gegendruck von etwa ${de(A.dp_aeq * k, 1)} Pa</b> (95-%-Bereich ${de(A.dp_ci[0] * k, 1)} bis ${de(A.dp_ci[1] * k, 1)} Pa). Das ist eine grobe Modellrechnung, keine Druckmessung.`;
  }
  $('m-h').oninput = druck; druck();
})();
