const chartData = {
    cpu: Array(10).fill(null), // Initialize with 10 null values for CPU data
    ram: Array(10).fill(null) // Initialize with 10 null values for RAM data
};

const timeLabels = Array(10).fill(''); // Initialize with empty time labels
const colors = {
    cpu: '#E60000', // Red for CPU
    ram: '#32CD32'  // Green for RAM
};

// Function to fetch server data
function fetchServerData() {
    fetch('/admin_panel/full_server_status')
        .then(response => response.json())
        .then(data => {
            updateChart(data);
        })
        .catch(error => console.error('Error fetching server data:', error));
}

// Function to update the chart with fetched data
function updateChart(data) {
    const currentTime = new Date().toLocaleTimeString('en-GB', { hour12: false });

    // Update time labels
    if (timeLabels.length >= 10) {
        timeLabels.shift(); // Remove the oldest timestamp
    }
    timeLabels.push(currentTime);

    // Update CPU and RAM data
    chartData.cpu.push(data.cpu);
    chartData.ram.push(data.ram);

    // Limit to 10 data points
    if (chartData.cpu.length > 10) chartData.cpu.shift();
    if (chartData.ram.length > 10) chartData.ram.shift();

    // Redraw the chart with new data
    drawChart();
}

// Function to draw the chart
function drawChart() {
    const datasets = [
        {
            label: 'CPU Load (%)',
            data: chartData.cpu,
            borderColor: colors.cpu,
            backgroundColor: colors.cpu,
            fill: false
        },
        {
            label: 'RAM Usage (%)',
            data: chartData.ram,
            borderColor: colors.ram,
            backgroundColor: colors.ram,
            fill: false
        }
    ];

    serverChart.data.labels = timeLabels;
    serverChart.data.datasets = datasets;
    serverChart.update();
}

// Create the chart
const serverChart = new Chart(document.getElementById('basechart').getContext('2d'), {
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
                display: false
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

// Fetch server data every 5 seconds
setInterval(fetchServerData, 5000);

// Initial fetch
fetchServerData();
