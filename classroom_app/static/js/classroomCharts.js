let successfulRateChart;

const themeColors = {
	line: "#22CE00",
	labels: "#a1a1a1",
	grid: "#333333",
};

window.onload = function () {
	const now = new Date();
	const year = now.getFullYear();
	const month = now.getMonth();
	const firstDay = new Date(year, month, 2).toISOString().split("T")[0];
	const lastDay = new Date(year, month + 1, 0).toISOString().split("T")[0];

	document.getElementById("start_date").value = firstDay;
	document.getElementById("end_date").value = lastDay;

	successfulRateChart = new ApexCharts(
		document.querySelector("#successfulRate"),
		{
			chart: {
				type: "area",
				height: 350,
				background: "transparent",
				foreColor: themeColors.labels,
				toolbar: { show: true },
				events: {
					markerClick: function (
						event,
						chartContext,
						{ dataPointIndex },
					) {
						const roomIds = chartContext.w.config.userData.roomIds;
						if (roomIds && roomIds[dataPointIndex]) {
							window.location.href =
								"/report/" + roomIds[dataPointIndex];
						}
					},
				},
			},
			dataLabels: {
				enabled: true,
				formatter: function (val) {
					return val + "%";
				},
			},
			colors: [themeColors.line],
			stroke: { curve: "smooth", width: 3 },
			fill: {
				type: "gradient",
				gradient: {
					shadeIntensity: 1,
					opacityFrom: 0.4,
					opacityTo: 0.1,
				},
			},
			yaxis: {
				min: 0,
				max: 100,
				tickAmount: 5,
				labels: {
					formatter: (val) => Math.round(val) + "%",
					style: { colors: themeColors.labels },
				},
			},
			xaxis: {
				type: "category",
				labels: { style: { colors: themeColors.labels } },
			},
			series: [],
			noData: {
				text: "Дані про успішність відсутні",
				style: { color: themeColors.labels, fontSize: "18px" },
			},
			tooltip: {
				theme: "dark",
				y: { formatter: (val) => val + "% успішності" },
			},
			legend: {
				show: false,
			},
		},
	);

	successfulRateChart.render();
	updateCharts();
};

async function updateCharts() {
	const classID = document.getElementById("classroom_id").value;
	const start = document.getElementById("start_date").value;
	const end = document.getElementById("end_date").value;

	const url = `/classrooms/class_stats/${classID}?start_date=${start}&end_date=${end}`;

	try {
		const response = await fetch(url);
		const resData = await response.json();

		successfulRateChart.updateOptions({
			xaxis: {
				categories: resData.labels,
				labels: {
					style: { colors: themeColors.labels },
					rotate: 0,
				},
			},
			legend: { show: false },
			userData: { roomIds: resData.ids },
		});

		successfulRateChart.updateSeries([
			{
				name: "Успішність кімнати",
				data: resData.success_rates,
			},
		]);
	} catch (err) {
		console.error("Помилка:", err);
	}
}
