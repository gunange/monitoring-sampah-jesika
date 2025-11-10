<template>
	<div class="card relative p-3 text-center py-5">
		<p class="mb-3 text-primary">Machine Learning</p>
		<i class="pi pi-microchip-ai text-[120px] text-gray-400" />
		<p
			class="mt-3 font-bold"
			:class="{ 'text-pink-500': !machineRunning, 'text-green-500': machineRunning }"
		>
			Status : {{ machineRunning  ? 'Running' : 'Off'}}
		</p>

		<!-- Tombol Play/Pause posisi absolut pojok kanan bawah -->
		<div class="absolute bottom-4 right-4">
			<Button
				@click="toggleMachine"
				size="small"
				:icon="machineRunning ? 'pi pi-power-off' : 'pi pi-play'"
				:severity="machineRunning ? 'danger' : 'success'"
				aria-label="Toggle Machine Learning"
			/>
		</div>
	</div>
</template>

<script>
	import { api } from "@/config/apiConfig.js";

	export default {
		name: "MlComp",
		data() {
			return {
				machineRunning: false,
			};
		},
		computed: {
			pathMl() {
				return `${api.url_api}machine-learning`;
			},
			pathMlStart() {
				return `${api.url_api}machine-learning/start`;
			},
			pathMlStop() {
				return `${api.url_api}machine-learning/stop`;
			},
		},

		methods: {
			async getStatus() {
				const res = await fetch(this.pathMl);
				const data = await res.json();
				this.machineRunning = data.running;
			},
			async toggleMachine() {
				try {
					const url = this.machineRunning ? this.pathMlStop : this.pathMlStart;
					const res = await fetch(url);
					const data = await res.json();
					this.machineRunning = data.running;
				} catch (e) {
					// Jika gagal, jangan ubah status; bisa tambahkan toast bila diperlukan
					console.error("Toggle machine failed:", e);
				}
			},
		},

		mounted() {
			this.getStatus();
		},
	};
</script>
