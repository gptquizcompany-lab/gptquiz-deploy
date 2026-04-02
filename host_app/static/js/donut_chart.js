function renderDonut(data1) {
    const options = {
        series: [data1.correct, data1.wrong, data1.skipped],
            chart: {
            type: 'donut',
            height: 300,
            animations: { enabled: true }
        },
        colors: ['#22CE00', '#F03C39', '#585858'],
        labels: ['Правильно', 'Не правильно', 'Пропущено'],
        
        legend: {
            show: false
        },
        
        dataLabels: {
            enabled: false
        },
        
        plotOptions: {
            pie: {
                expandOnClick: false,
                donut: {
                    size: '70%',
                    labels: {
                        show: false
                    }
                },
                customScale: 1,
                dataLabels: { minAngleToShowLabel: 10 }
            }
        },
        stroke: {
            show: true,
            width: 5,
            colors: ['#2B2B2B'] 
        }
    };

    const chart = new ApexCharts(document.querySelector("#chart"), options);
    chart.render();
}