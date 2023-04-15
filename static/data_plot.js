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
                    },
                    
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
                },
                zoom: {
                    zoom:{
                        wheel:{
                            enabled: true
                        }
                    }
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

function plot_magnData(ctx, x_data, y_data, legend, title="", x_label="", y_label="") {
    let dates_all = []
    x_data[0].forEach(date=> dates_all.push(new Date(date).toUTCString()))

    let dates_scat = []
    x_data[1].forEach(date=> dates_scat.push(new Date(date).toUTCString()))

    let line_dataset = {
        label: legend[0],
        data: y_data[0],
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
        fill: false,
        yAxisID: 'y-axis-1'
    }

    let scatter_dataset = {
        label: legend[1],
        data: [],
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        pointRadius: 5,
        pointHoverRadius: 7,
        showLine: false,
        yAxisID: 'y-axis-1'
    }

    for (let i = 0; i < y_data[1].length; i++) {
        scatter_dataset.data.push({
            x: dates_scat[i],
            y: y_data[1][i]
        })
    }

    let data = {
        labels: dates_all,
        datasets: [line_dataset, scatter_dataset]
    }

    plot_data(ctx, data, title, x_label, y_label)
}
