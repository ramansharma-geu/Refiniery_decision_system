// Dashboard Chart Initialization for RDIS

document.addEventListener("DOMContentLoaded", function() {
    // Fetch analytics data
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            renderCharts(data);
        })
        .catch(error => {
            console.error("Error loading analytics data: ", error);
        });
});

function renderCharts(data) {
    if (!data || !data.trends || Object.keys(data.trends).length === 0) {
        console.warn("No trend data available for charts.");
        return;
    }

    const trends = data.trends;
    const scenarioDist = data.scenario_distribution || {};

    // Unit Color Mapping (Carbon palette)
    const colors = {
        "CDU": { border: "#0f62fe", bg: "rgba(15, 98, 254, 0.05)" },         // Blue
        "VDU": { border: "#6f7070", bg: "rgba(111, 112, 112, 0.05)" },       // Slate Gray
        "FCC": { border: "#8a3ffc", bg: "rgba(138, 63, 252, 0.05)" },        // Magenta/Purple
        "Hydrotreater": { border: "#009d9a", bg: "rgba(0, 157, 154, 0.05)" }, // Teal
        "Storage Terminal": { border: "#da1e28", bg: "rgba(218, 30, 40, 0.05)" } // Red
    };

    // Extract timestamps from the first available unit (not hard-coded to CDU)
    const unitCodes = Object.keys(trends);
    if (unitCodes.length === 0) return;
    const labels = trends[unitCodes[0]].timestamps || [];

    // 1. Throughput Chart (Line Chart)
    const ctxThroughput = document.getElementById('throughputChart').getContext('2d');
    new Chart(ctxThroughput, {
        type: 'line',
        data: {
            labels: labels,
            datasets: unitCodes.map(unitCode => ({
                label: unitCode,
                data: trends[unitCode].throughput || [],
                borderColor: (colors[unitCode] || { border: "#161616" }).border,
                backgroundColor: (colors[unitCode] || { bg: "rgba(22, 22, 22, 0.05)" }).bg,
                borderWidth: 2,
                pointRadius: 2,
                tension: 0.1,
                fill: false
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'IBM Plex Sans' } } }
            },
            scales: {
                x: { grid: { color: "#f4f4f4" }, ticks: { font: { family: 'IBM Plex Sans', size: 10 } } },
                y: { grid: { color: "#e0e0e0" }, ticks: { font: { family: 'IBM Plex Sans', size: 10 } }, title: { display: true, text: 'bbl / day' } }
            }
        }
    });

    // 2. Yield Chart (Line Chart)
    const ctxYield = document.getElementById('yieldChart').getContext('2d');
    new Chart(ctxYield, {
        type: 'line',
        data: {
            labels: labels,
            datasets: unitCodes.map(unitCode => ({
                label: unitCode,
                data: trends[unitCode].yield || [],
                borderColor: (colors[unitCode] || { border: "#161616" }).border,
                borderWidth: 1.5,
                pointRadius: 1,
                tension: 0.1,
                fill: false
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false } // Hide to save space in small cards
            },
            scales: {
                x: { grid: { color: "#f4f4f4" }, ticks: { font: { family: 'IBM Plex Sans', size: 9 } } },
                y: { grid: { color: "#e0e0e0" }, ticks: { font: { family: 'IBM Plex Sans', size: 9 } }, title: { display: true, text: 'Yield %' } }
            }
        }
    });

    // 3. Energy Consumption Chart (Bar Chart)
    const ctxEnergy = document.getElementById('energyChart').getContext('2d');
    new Chart(ctxEnergy, {
        type: 'bar',
        data: {
            labels: unitCodes,
            datasets: [{
                label: 'Average Energy Consumption',
                data: unitCodes.map(unitCode => {
                    const vals = trends[unitCode].energy_consumption || [];
                    if (vals.length === 0) return 0;
                    const sum = vals.reduce((a, b) => a + b, 0);
                    return roundVal(sum / vals.length);
                }),
                backgroundColor: unitCodes.map(unitCode => (colors[unitCode] || { border: "#161616" }).border),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { font: { family: 'IBM Plex Sans', size: 9 } } },
                y: { grid: { color: "#e0e0e0" }, ticks: { font: { family: 'IBM Plex Sans', size: 9 } }, title: { display: true, text: 'MMBtu / hr' } }
            }
        }
    });

    // 4. Downtime Chart (Bar Chart)
    const ctxDowntime = document.getElementById('downtimeChart').getContext('2d');
    new Chart(ctxDowntime, {
        type: 'bar',
        data: {
            labels: unitCodes,
            datasets: [{
                label: 'Cumulative Downtime (hrs)',
                data: unitCodes.map(unitCode => {
                    const vals = trends[unitCode].downtime || [];
                    return roundVal(vals.reduce((a, b) => a + b, 0));
                }),
                backgroundColor: "#161616", // Charcoal base
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { font: { family: 'IBM Plex Sans', size: 9 } } },
                y: { grid: { color: "#e0e0e0" }, ticks: { font: { family: 'IBM Plex Sans', size: 9 } }, title: { display: true, text: 'Hours' } }
            }
        }
    });

    // 5. Scenario Distribution Chart (Pie/Doughnut Chart)
    const ctxDist = document.getElementById('scenarioDistChart').getContext('2d');
    const distLabels = Object.keys(scenarioDist);
    const distData = Object.values(scenarioDist);
    
    const fallbackColors = ["#0f62fe", "#8a3ffc", "#009d9a", "#da1e28", "#f1c21b", "#6f7070", "#198038"];
    
    new Chart(ctxDist, {
        type: 'doughnut',
        data: {
            labels: distLabels.length > 0 ? distLabels : ['No Scenarios'],
            datasets: [{
                data: distData.length > 0 ? distData : [1],
                backgroundColor: fallbackColors.slice(0, distLabels.length || 1),
                borderWidth: 1,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 10, font: { family: 'IBM Plex Sans', size: 9 } } }
            },
            cutout: '60%'
        }
    });
}

function roundVal(v) {
    return Math.round(v * 100) / 100;
}
