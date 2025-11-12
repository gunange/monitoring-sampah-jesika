<template>
	<div class="card relative p-3 text-center py-5">
		<p class="mb-3 text-primary font-bold">Machine Learning</p>
		<i class="pi pi-microchip-ai text-[120px] text-gray-400 mb-3" />
		<p class="mt-3 text-sm">
			<span>Status </span>
			<span
				:class="{
					'text-pink-500': !machineRunning,
					'text-green-500': machineRunning,
				}"
				>{{ run ? (machineRunning ? "RUNNING" : "STOPPED") : "UNAVAILABLE" }}</span
			>
		</p>

		<!-- Tombol Play/Pause posisi absolut pojok kanan bawah -->
		<div class="absolute bottom-4 right-4" v-if="run">
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
	import {MainData} from "@/components/dashboard/petugas/cruds/ml-config/controller.ts";

	const main = new MainData()

	export default {
		name: "MlComp",
		data() {
			return {
			};
		},
		computed: {
			machineRunning() {
				return main.machineRunning ?? false
			},
			run(){
				return main.data.run;
			}
		},
		methods: {
			async toggleMachine() {
				try {
					await main.toggleMachine();
				} catch (e) {
				}
			},
		},

		
	};
</script>
