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
                        height: 400,
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
                const pruned = items.length > 30 ? items.slice(-30) : items;
                return [...pruned].reverse().slice(0, 18);
            },
        },
        mounted() {
            this.chart = new ApexCharts(this.$refs.chart, this.chartOptions);
            this.chart.render();
            this.updateChart(this.item);
        },
        watch: {
            item(newItems) {
                if (!this.chart) return;
                this.updateChart(newItems);
            },
        },
        methods: {
            buildSeries(items) {
                const now = Date.now();
                const points = items.map((it, idx, arr) => {
                    const raw = (it?.features?.shape_area_ratio ?? it?.features?.edge_ratio ?? 0);
                    const ratio = Math.max(0, Math.min(1, raw));
                    const y = Math.round(ratio * 100);
                    const x = now - (arr.length - idx) * 1000;
                    return { x, y };
                });
                return points;
            },
            computeBounds(points) {
                if (!points || points.length === 0) return { min: 0, max: 100 };
                const ys = points.map(p => p.y);
                let min = Math.min(...ys);
                let max = Math.max(...ys);
                const range = max - min;
                const pad = Math.max(2, Math.round(range * 0.2));
                min = Math.max(0, min - pad);
                max = Math.min(100, max + pad);
                if (max - min < 10) {
                    const center = (min + max) / 2;
                    min = Math.max(0, Math.round(center - 8));
                    max = Math.min(100, Math.round(center + 8));
                }
                return { min, max };
            },
            updateChart(items) {
                const data = this.buildSeries(items);
                const { min, max } = this.computeBounds(data);
                this.chart.updateOptions({ yaxis: { min, max } });
                this.chart.updateSeries([{ name: "Trash Index", data }]);
            },
        },
    };
</script>
