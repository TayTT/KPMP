function plot_data(ctx, data, title="", x_label="", y_label="") {
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            scales: {
                y: {
                    title: {
                        display: true,
                        text: y_label,
                        color: '#ffffff'
                    },
                    beginAtZero: false,
                    grid: {
                        color: '#aaaaaa'
                    },
                    ticks: {
                        color: '#ffffff'
                    },
                    border: {
                        color: '#aaaaaa'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: x_label,
                        color: '#ffffff'
                    },
                    grid: {
                        color: '#aaaaaa'
                    },
                    ticks: {
                        color: '#ffffff'
                    },
                    border: {
                        color: '#aaaaaa'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: "right",
                    align: "center",
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: title,
                    color: '#ffffff'
                }
            }
        }
    })
}

function plot_weatherData(ctx, x_data, y_data, legend, title="", x_label="", y_label="") {

    let dates = []
    x_data.forEach(date=> dates.push(new Date(date).toUTCString()))

    let data = {
        labels: dates,
        datasets: [{
            label: legend,
            data: y_data,
            borderWidth: 1
        }]
    }

    plot_data(ctx, data, title, x_label, y_label)
}

function plot_multipleData(ctx, x_data, y_data, legend, title="", x_label="", y_label="") {

    let dates = []
    x_data.forEach(date=> dates.push(new Date(date).toUTCString()))

    let y_datasets = []
    for(let i = 0; i < y_data.length; i++) {
        y_datasets.push({
            label: legend[i],
            data: y_data[i],
            borderWidth: 1
        })
    }

    let data = {
        labels: dates,
        datasets: y_datasets
    }

    plot_data(ctx, data, title, x_label, y_label)

}