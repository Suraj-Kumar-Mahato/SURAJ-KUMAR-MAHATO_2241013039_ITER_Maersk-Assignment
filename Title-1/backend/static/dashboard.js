async function fetchJSON(url) {
  const headers = API_KEY ? {'X-API-KEY': API_KEY} : {};
  const res = await fetch(url, {headers});
  return res.json();
}

async function initMap() {
  const map = L.map('map').setView([19.0760, 72.8777], 4); // India zoom
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  const gj = await fetchJSON('/api/v1/geojson');
  const layer = L.geoJSON(gj, {
    pointToLayer: function (feature, latlng) {
      const rsrp = feature.properties.rsrp ?? -120;
      // green (good) to red (poor)
      let color = '#2ecc71';
      if (rsrp < -80) color = '#f1c40f';
      if (rsrp < -95) color = '#e67e22';
      if (rsrp < -110) color = '#e74c3c';
      return L.circleMarker(latlng, {radius: 5, color, fillColor: color, fillOpacity: 0.8});
    },
    onEachFeature: function (f, layer) {
      const p = f.properties;
      const html = Object.entries(p).map(([k,v])=>`<b>${k}</b>: ${v}`).join('<br>');
      layer.bindPopup(html);
    }
  }).addTo(map);

  map.fitBounds(layer.getBounds(), {maxZoom: 15, padding: [20,20]});
}

async function initChart() {
  const data = await fetchJSON('/api/v1/measurements?limit=200');
  const labels = data.map(d => d.ts).reverse();
  const rsrp = data.map(d => d.rsrp).reverse();
  const rsrq = data.map(d => d.rsrq).reverse();
  const sinr = data.map(d => d.sinr).reverse();

  const ctx = document.getElementById('kpiChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {label: 'RSRP (dBm)', data: rsrp},
        {label: 'RSRQ (dB)', data: rsrq},
        {label: 'SINR (dB)', data: sinr}
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { display: true } },
      scales: {
        x: { ticks: { display: false } },
        y: { beginAtZero: false }
      }
    }
  });
}

(async () => {
  await initMap();
  await initChart();
  // Simple auto-refresh
  setInterval(async ()=>{
    document.location.reload();
  }, 60000);
})();
