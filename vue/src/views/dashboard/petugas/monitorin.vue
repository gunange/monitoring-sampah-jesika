<template>
	<div class="px-5 mt-5">
		<div class="card p-3 text-center relative">
            <!-- Overlay info terbaru -->
            <div
                v-if="latestInfo && running"
                class="absolute top-3 left-3 z-10 max-w-[75%] text-left p-2 bg-black/50 rounded-[5px] shadow-lg"
            >
                <div class="text-left text-xs text-white">
                    <p class="font-semibold">Status Monitoring: {{ latestData?.label }}</p>
                    <div class="mt-1 space-y-0.5">
                        <p>Resolusi Frame: {{ latestData?.frame?.width }} x {{ latestData?.frame?.height }}</p>
                        <p>ROI: x={{ latestData?.roi?.x }}, y={{ latestData?.roi?.y }}, w={{ latestData?.roi?.w }}, h={{ latestData?.roi?.h }}</p>

                        <p>Rata-rata Rona (Hue): {{ latestData?.features?.h_mean }}</p>
                        <p>Simpangan Baku Rona (Hue): {{ latestData?.features?.h_std }}</p>

                        <p>Rata-rata Kejenuhan (Saturation): {{ latestData?.features?.s_mean }}</p>
                        <p>Simpangan Baku Kejenuhan (Saturation): {{ latestData?.features?.s_std }}</p>

                        <p>Rata-rata Kecerahan (Value): {{ latestData?.features?.v_mean }}</p>
                        <p>Simpangan Baku Kecerahan (Value): {{ latestData?.features?.v_std }}</p>

                        <p>Variansi Laplacian: {{ latestData?.features?.laplacian_var }}</p>
                        <p>Rasio Tepi (Edge Ratio): {{ latestData?.features?.edge_ratio }}</p>
                        <p>Rasio Luas Bentuk (Shape Area Ratio): {{ latestData?.features?.shape_area_ratio }}</p>
                    </div>
                </div>
            </div>
			<!-- kunci dengan :key agar <img> benar2 di-recreate -->
			<img
				:key="imgVersion"
				:src="urlMlStream"
				alt="Live Stream"
				class="w-full rounded-sm"
				v-if="running"
			/>
			<div class="mt-2 text-xs text-gray-500" v-else>
				Status Machine Learning: <b>{{ running ? "RUNNING" : "STOPPED" }}</b>
			</div>
		</div>
	</div>
</template>

<script>
	import { api } from "@/config/apiConfig.js";
    import { infoCtrl } from "@/components/dashboard/petugas/controllers/info";
	import { MainData } from "@/components/dashboard/petugas/cruds/ml-config/controller.ts";
	

	const main = new MainData();

	export default {
		name: "MainView",
		data() {
			return {
				imgVersion: "0",
			};
		},
		computed: {
			// tambahkan cache-buster ?v=imgVersion
			urlMlStream() {
				return `${api.url_ml_http}/camera/stream?v=${this.imgVersion}`;
			},
			pathMl() {
				return `${api.url_api}machine-learning`;
			},
            latestInfo() {
                const items = infoCtrl.items ?? [];
                return items.length ? items[items.length - 1] : null;
            },
            latestData() {
                const item = this.latestInfo;
                if (!item) return null;
                return item.data ?? item;
            },

			running() {
				return main.machineRunning;
			},
			
        },
		methods: {
			refreshStream() {
				this.imgVersion = Date.now();
			},
			
           
		},
		async mounted() {
			this.refreshStream();
		},
	};
</script>
