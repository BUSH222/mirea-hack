const masterData = {};

const colors = ['#E60000', '#32CD32', '#0000FF']

const timeLabels = Array(10).fill('');

// Function to fetch server data
function fetchServerData() {
    fetch('/admin_panel/full_server_status')
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
        })
        .catch(error => console.error('Error fetching server data:', error));
}

// Function to update charts with fetched data
function updateCharts(data) {
    // Update server names
    const currentTime = new Date().toLocaleTimeString('en-GB', { hour12: false });

    if (timeLabels.length >= 10) {
        timeLabels.shift();
    }
    timeLabels.push(currentTime);

    for (const server in data) {
        if (!masterData[server]) {
            masterData[server] = Array(10).fill(null); // Initialize with 10 null values
        }
        masterData[server].push(data[server].cpu);
        masterData[server].push(data[server].ram);

        // Limit to 10 data points
        if (masterData[server].length > 10) masterData[server].shift();
    }

    // Redraw the charts with new data
    drawChart(cpuLoadChart, masterData, 'Нагрузка на основной сервер');
}

// Function to draw the chart
function drawChart(chart, data, label) {
    const datasets = serverNames.map((server, index) => ({
        label: server,
        data: data[server],
        borderColor: colors[index % colors.length],
        fill: false
    }));

    chart.data.labels = timeLabels;
    chart.data.datasets = datasets;
    chart.update();
}

// Create the charts
const cpuLoadChart = new Chart(document.getElementById('cpuLoadChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            },
            x: {
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        },
        animation: false
    }
});

const ramUsageChart = new Chart(document.getElementById('ramUsageChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            },
            x: {
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        },
        animation: false
    }
});

const rpmChart = new Chart(document.getElementById('rpmChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 1000,
                type: 'logarithmic'
            },
            x: {
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        },
        animation: false
    }
});

// Fetch server data every 5 seconds
setInterval(fetchServerData, 5000);

// Initial fetch
fetchServerData();
