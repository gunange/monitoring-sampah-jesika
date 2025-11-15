<template>
	<div class="px-5 mt-5">
		<div class="card p-3">
			<div ref="chart"></div>
		</div>
	</div>
</template>

<script>
    import { infoCtrl } from "@/components/dashboard/petugas/controllers/info";
    import ApexCharts from "apexcharts";

    export default {
        name: "MlComp",
        data() {
            return {
                chart: null,
                chartOptions: {
                    chart: {
                        id: "traffic-realtime",
                        height: 350,
                        type: "line",
                        animations: {
                            enabled: true,
                            easing: "linear",
                            dynamicAnimation: { speed: 800 },
                        },
                        toolbar: { show: false },
                        zoom: { enabled: false },
                    },
                    dataLabels: { enabled: false },
                    stroke: { curve: "smooth" },
                    title: { text: "Traffic Trash Index", align: "left" },
                    markers: { size: 0 },
                    xaxis: { type: "datetime" },
                    yaxis: { max: 100, min: 0 },
                    legend: { show: false },
                    series: [
                        { name: "Trash Index", data: [] },
                    ],
                },
            };
        },
        computed: {
            item() {
                const items = infoCtrl.items ?? [];
                const pruned = items.length > 20 ? items.slice(-20) : items;
                return [...pruned].reverse().slice(0, 10);
            },
        },
        mounted() {
            this.chart = new ApexCharts(this.$refs.chart, this.chartOptions);
            this.chart.render();
            const initial = this.buildSeries(this.item);
            this.chart.updateSeries([{ name: "Trash Index", data: initial }]);
        },
        watch: {
            item(newItems) {
                if (!this.chart) return;
                const data = this.buildSeries(newItems);
                this.chart.updateSeries([{ name: "Trash Index", data }]);
            },
        },
        methods: {
            buildSeries(items) {
                const now = Date.now();
                const gate = 5;
                const points = items
                    .filter(it => (it?.features?.laplacian_var ?? gate) >= gate)
                    .map((it, idx, arr) => {
                        const ratio = Math.max(0, Math.min(1, it?.features?.shape_area_ratio ?? 0));
                        const y = Math.round(ratio * 100);
                        const x = now - (arr.length - idx) * 1000;
                        return { x, y };
                    });
                return points;
            },
        },
    };
</script>
