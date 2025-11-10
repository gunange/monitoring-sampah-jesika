<template>
	<div class="px-5 mt-5">
		<div class="card p-3 text-center">
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
	// import BradcumpWidget jika dipakai

	export default {
		name: "MainView",
		data() {
			return {
				running: false,
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
		},
		methods: {
			refreshStream() {
				this.imgVersion = Date.now();
			},
			async init() {
				const res = await fetch(this.pathMl, { cache: "no-store" });
				const json = await res.json(); // { name: 'Machine Learning', running: boolean }
				const wasRunning = this.running;
				this.running = !!json.running;
				if (this.running && !wasRunning) {
					this.refreshStream();
				}
			},
		},
		async mounted() {
			await this.init();
		},
	};
</script>
