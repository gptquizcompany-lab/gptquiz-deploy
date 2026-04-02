async function loadRoomStats(roomId) {
	try {
		const response = await fetch(`/reports/room_stats/${roomId}`);
		const data = await response.json();

		const categories = data.map((item) => item.question);
		const textQuestions = data.map(
			(item, index) => `№${index + 1}. ${item.text}`,
		);

		const correctValues = data.map((item) => item.correctCount);
		const wrongValues = data.map(
			(item) => item.totalCount - item.correctCount,
		);
		const correctPercents = data.map((item) => item.succesfull);
		const wrongPercents = data.map((item) => 100 - item.succesfull);

		renderChart(
			categories,
			correctValues,
			wrongValues,
			correctPercents,
			wrongPercents,
			textQuestions,
		);
	} catch (error) {
		console.error("Помилка завантаження статистики:", error);
	}
}

function renderChart(
	categories,
	correctValues,
	wrongValues,
	correctPercents,
	wrongPercents,
	textQuestions,
) {
    const container = document.querySelector("#questionsChart");
    const containerWidth = container.parentElement.getBoundingClientRect().width || 400;
    const minBarWidth = 80;
    const naturalBarWidth = containerWidth / categories.length; 

    if (naturalBarWidth < minBarWidth) {
        container.style.width = (categories.length * minBarWidth) + "px";
    } else {
        container.style.width = "100%";
    }
	const options = {
		series: [
			{
				name: "Правильні",
				data: correctPercents,
			},
			{
				name: "Неправильні",
				data: wrongPercents,
			},
		],
		chart: {
			type: "bar",
			height: 350,
			width: "100%",
			background: "transparent",
			toolbar: { show: false },
			stacked: false,
		},
		plotOptions: {
			bar: {
				borderRadius: 4,
				columnWidth: "45%",
				distributed: false,
			},
		},
		colors: ["#22c55e", "#ef4444"],

		dataLabels: {
			enabled: true,
			formatter: function (val, opts) {
				const idx = opts.dataPointIndex;
				const seriesIdx = opts.seriesIndex;
				const percent =
					seriesIdx === 0 ? correctPercents[idx] : wrongPercents[idx];
				return percent > 0 ? percent + "%" : "";
			},
			style: {
				colors: ["#fff"],
				fontSize: "11px",
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
			min: 0,
			max: 100,
			tickAmount: 5,
			labels: {
				style: { colors: "#a1a1a1" },
				formatter: function (val) {
					return val + "%";
				},
			},
		},
		grid: {
			borderColor: "#333",
			yaxis: { lines: { show: true } },
		},
		legend: {
			show: true,
			labels: { colors: "#a1a1a1" },
		},
		tooltip: {
			theme: "dark",
			shared: true,
			intersect: false,
			x: {
				formatter: function (val, { dataPointIndex }) {
					return textQuestions[dataPointIndex];
				},
			},
			y: {
				formatter: function (val, opts) {
					const idx = opts.dataPointIndex;
					const seriesIdx = opts.seriesIndex;
					const count =
						seriesIdx === 0 ? correctValues[idx] : wrongValues[idx];
					const label =
						seriesIdx === 0 ? "правильних" : "неправильних";
					return `${count} відповідей (${val}% ${label})`;
				},
			},
		},
		noData: {
			text: "Дані відсутні",
			style: { color: "#a1a1a1", fontSize: "16px" },
		},
	};

	const chart = new ApexCharts(
		document.querySelector("#questionsChart"),
		options,
	);
	chart.render();
}
