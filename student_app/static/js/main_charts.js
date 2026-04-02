let lineChart, pieChart;

const themeColors = {
    line: '#008FFB',      
    labels: '#a1a1a1',
    grid: '#333333',
    marker: '#ffffff',   
    background: '#1b1b1b'
};

window.onload = function() {

    lineChart = new ApexCharts(document.querySelector("#lineChart"), {
        chart: {
            type: 'line',
            height: 350,
            background: 'transparent',
            foreColor: themeColors.labels,
            toolbar: { show: true },
            events: {
                markerClick: function(event, chartContext, { dataPointIndex }) {
                    const hashes = chartContext.w.config.userData.hashes;
                    if (hashes && hashes[dataPointIndex]) {
                        window.location.href = "/student/report/" + hashes[dataPointIndex];
                    }
                }
            }
        },
        colors: [themeColors.line], 
        stroke: {
            curve: 'smooth',
            width: 4
        },
        markers: {
            size: 6,
            colors: [themeColors.line],
            strokeColors: themeColors.marker,
            strokeWidth: 2,
            hover: { size: 9 }
        },
        grid: {
            borderColor: themeColors.grid,
            xaxis: { lines: { show: false } } 
        },
        yaxis: {
            min: 0,
            max: 12,
            tickAmount: 12,
            labels: {
                style: { colors: themeColors.labels }
            }
        },
        xaxis: {
            type: 'category',
            labels: {
                style: { colors: themeColors.labels }
            }
        },
        userData: { hashes: [] },
        series: [],
        noData: {
            text: "Немає даних на цей період",
            align: 'center',
            verticalAlign: 'middle',
            style: {
                color: themeColors.labels,
                fontSize: '18px',
                fontFamily: 'Inter, sans-serif',                
            }
        },
    });

    pieChart = new ApexCharts(document.querySelector("#pieChart"), {
        chart: {
            type: 'pie',
            height: 350,
            background: 'transparent',
            foreColor: themeColors.labels
        },
        dataLabels: {
            enabled: true,
            formatter: function (val, opts) {
                const label = opts.w.config.labels[opts.seriesIndex];
                return label && typeof label === 'string' ? label.split(" ")[1] : '';
            },
            style: {
                fontSize: '14px',
                fontWeight: 'bold',
                colors: ['#fff'] 
            },
            dropShadow: {
                enabled: true,
                opacity: 0.5
            }
        },
        legend: {
            position: 'right',
            labels: { colors: themeColors.labels }
        },
        
        series: [], 
        labels: [], 
        noData: {
            text: "Немає даних на цей період",
            align: 'center',
            verticalAlign: 'middle',
            style: {
                color: themeColors.labels,
                fontSize: '18px',
                fontFamily: 'Inter, sans-serif'
        }}
    });

    lineChart.render();
    pieChart.render();
    updateCharts();
};

async function updateCharts() {
    const sID = document.getElementById('student_id').value;
    const start = document.getElementById('start_date').value;
    const end = document.getElementById('end_date').value;

    const url = `/student/api/student_stats/${sID}?start_date=${start}&end_date=${end}`;
    
    try {
        const response = await fetch(url);
        const resData = await response.json();

        lineChart.updateOptions({
            xaxis: { categories: resData.dates },
            userData: { hashes: resData.hashes } 
        });
        
        lineChart.updateSeries([{
            name: 'Оцінка',
            data: resData.grades
        }]);

        pieChart.updateOptions({ 
            labels: Object.keys(resData.pie_data) 
        });
        pieChart.updateSeries(Object.values(resData.pie_data));

    } catch (err) {
        console.error("Ошибка:", err);
    }
}