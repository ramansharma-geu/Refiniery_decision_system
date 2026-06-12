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
    const trends = data.trends;
    const scenarioDist = data.scenario_distribution;

    // Unit Color Mapping (IBM Carbon palette)
    const colors = {
        "CDU": { border: "#0f62fe", bg: "rgba(15, 98, 254, 0.05)" },         // IBM Blue
        "VDU": { border: "#6f7070", bg: "rgba(111, 112, 112, 0.05)" },       // Slate Gray
        "FCC": { border: "#8a3ffc", bg: "rgba(138, 63, 252, 0.05)" },        // Magenta/Purple
        "Hydrotreater": { border: "#009d9a", bg: "rgba(0, 157, 154, 0.05)" }, // Teal
        "Storage Terminal": { border: "#da1e28", bg: "rgba(218, 30, 40, 0.05)" } // Red
    };

    // Extract timestamps (using CDU as reference timeline)
    const labels = trends["CDU"].timestamps;

    // 1. Throughput Chart (Line Chart)
    const ctxThroughput = document.getElementById('throughputChart').getContext('2d');
    new Chart(ctxThroughput, {
        type: 'line',
        data: {
            labels: labels,
            datasets: Object.keys(trends).map(unitCode => ({
                label: unitCode,
                data: trends[unitCode].throughput,
                borderColor: colors[unitCode].border,
                backgroundColor: colors[unitCode].bg,
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
            datasets: Object.keys(trends).map(unitCode => ({
                label: unitCode,
                data: trends[unitCode].yield,
                borderColor: colors[unitCode].border,
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
            labels: Object.keys(trends),
            datasets: [{
                label: 'Average Energy Consumption',
                data: Object.keys(trends).map(unitCode => {
                    const vals = trends[unitCode].energy_consumption;
                    const sum = vals.reduce((a, b) => a + b, 0);
                    return roundVal(sum / vals.length);
                }),
                backgroundColor: Object.keys(trends).map(unitCode => colors[unitCode].border),
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
            labels: Object.keys(trends),
            datasets: [{
                label: 'Cumulative Downtime (hrs)',
                data: Object.keys(trends).map(unitCode => {
                    const vals = trends[unitCode].downtime;
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
    
    new Chart(ctxDist, {
        type: 'doughnut',
        data: {
            labels: distLabels,
            datasets: [{
                data: distData,
                backgroundColor: [
                    "#0f62fe", // Blue
                    "#8a3ffc", // Purple
                    "#009d9a", // Teal
                    "#da1e28", // Red
                    "#f1c21b"  // Yellow
                ],
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
