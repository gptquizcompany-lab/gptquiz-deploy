async function loadTimeStats(roomId) {
    if (document.querySelector("#timeQuestionsChart")) {
        document.querySelector("#timeQuestionsChart").remove();
    }

    try {
        const response = await fetch(`/reports/room_time_stats/${roomId}`);
        const data = await response.json();

        const categories = data.map(item => item.question);
        const textQuestions = data.map((item, index) => `№${index + 1}. ${item.text}`);
        const avgTimes = data.map(item => item.avg_time); 

        renderTimeChart(categories, avgTimes, textQuestions);

    } catch (error) {
        console.error("Помилка завантаження часу:", error);
    }
}

function renderTimeChart(categories, avgTimes, textQuestions) {
    const container = document.querySelector("#questionsChart");
    container.innerHTML = '<div id="timeQuestionsChart"></div>';

    const options = {
        series: [{
            name: 'Середній час',
            data: avgTimes
        }],
        chart: {
            type: 'line',
            height: 350,
            width: "100%",
            background: 'transparent',
            toolbar: { show: false }
        },
        stroke: {
            curve: 'straight',
            width: 3
        },
        colors: ['#775DD0'],
        markers: {
            size: 5,
            colors: ['#775DD0'],
            strokeColors: '#fff',
            strokeWidth: 2,
            hover: { size: 7 }
        },
        dataLabels: {
            enabled: false
        },
        xaxis: {
            categories: categories,
            labels: {
                style: {
                    colors: '#a1a1a1',
                    fontSize: '14px'
                }
            },
            axisBorder: { show: false },
            axisTicks: { show: false }
        },
        yaxis: {
            min: 0,
            labels: {
                style: { colors: '#a1a1a1' },
                formatter: function(val) {
                    return val + "с";
                }
            }
        },
        grid: {
            borderColor: '#333',
            yaxis: { lines: { show: true } }
        },
        legend: { show: false },
        tooltip: {
            theme: 'dark',
            x: {
                formatter: function(val, { dataPointIndex }) {
                    return textQuestions[dataPointIndex];
                }
            },
            y: {
                formatter: function(val) {
                    return val + " сек.";
                }
            }
        },
        noData: {
            text: "Дані відсутні",
            style: { color: '#a1a1a1', fontSize: '16px' }
        }
    };

    const chart = new ApexCharts(document.querySelector("#timeQuestionsChart"), options);
    chart.render();
}