async function loadStudentTimeStats(data) {
	if (document.querySelector("#timeChart").innerHTML.trim()) {
		document.querySelector("#timeChart").innerHTML = "";
	}
	if (!data || data.length === 0) return;

	try {
		const categories = data.map((item, index) => `Q${index + 1}`);
		const textQuestions = data.map(
			(item, index) => `№${index + 1}. ${item.question_text}`,
		);
		const values = data.map((item) => item.time_spent);

		renderChartTime(categories, values, textQuestions);
	} catch (error) {
		console.error("Помилка завантаження статистики:", error);
	}
}

function renderChartTime(categories, values, textQuestions) {
    const minBarWidth = 60;
    const minChartWidth = 400;
    const calculatedWidth = Math.max(minChartWidth, categories.length * minBarWidth);

    document.querySelector("#timeChart").style.width = calculatedWidth + "px";
	
	const options = {
		series: [
			{
				name: "Час",
				data: values,
			},
		],
		chart: {
			type: "bar",
			height: "100%",
			width: "100%",
			background: "transparent",
			toolbar: { show: false },
		},
		plotOptions: {
			bar: {
				borderRadius: 4,
				columnWidth: "45%",
				distributed: true,
			},
		},
		colors: ["#775DD0"],

		dataLabels: {
			enabled: true,
			formatter: function (val) {
				return val + " с";
			},
			style: {
				colors: ["#fff"],
				fontSize: "12px",
			},
		},
		xaxis: {
			categories: categories,
			labels: {
				style: {
					colors: "#a1a1a1",
					fontSize: "14px",
				},
			},
			axisBorder: { show: false },
			axisTicks: { show: false },
		},
		yaxis: {
			labels: {
				style: { colors: "#a1a1a1" },
				formatter: function (val) {
					return val + " с";
				},
			},
		},
		grid: {
			borderColor: "#333",
			yaxis: { lines: { show: true } },
		},
		legend: { show: false },
		tooltip: {
			theme: "dark",
			x: {
				formatter: function (val, { dataPointIndex }) {
					return textQuestions[dataPointIndex];
				},
			},
			y: {
				formatter: function (val) {
					return val + " Секунд було витрачено";
				},
			},
		},
		noData: {
			text: "Дані відсутні",
			style: { color: "#a1a1a1", fontSize: "16px" },
		},
	};

	const chart = new ApexCharts(document.querySelector("#timeChart"), options);
	chart.render();
}
