<template>
	<div class="card relative p-3 text-center py-4">
		<div class="card-header flex justify-between">
			<div class="flex-none flex items-center">
				<h6><i class="pi pi-sparkles" /> <span>Log Actifity Monitoring</span></h6>
			</div>
		</div>
		<div class="card-body">
			<Message
				size="small"
				icon="pi pi-exclamation-circle"
				closable
				v-for="(e, i) in infoCtrlItem"
				:key="i"
				class="mb-3"
				:severity="getSeverity(e.label)"
			>
				<div class="flex justify-between">
					<div class="text-left text-xs">
						<p>Status Montioring: {{ e.label }}</p>
						<div class="">
							<span>Rata-rata Rona (Hue): {{ e.features.h_mean }}, </span>
							<span
								>Rata-rata Kejenuhan (Saturation): {{ e.features.s_mean }},
							</span>
							<span>Rata-rata Kecerahan (Value): {{ e.features.v_mean }}, </span>
							<span>Simpangan Baku Rona (Hue): {{ e.features.h_std }}, </span>
							<span
								>Simpangan Baku Kejenuhan (Saturation): {{ e.features.s_std }},
							</span>
							<span>Simpangan Baku Kecerahan (Value): {{ e.features.v_std }}</span>
						</div>
					</div>
					<div class="flex justify-center items-center flex-none">
						<Button
							type="button"
							label="Save Logs"
							size="small"
							class="mt-2"
							@click="addLogs({...e})"
						/>
					</div>
				</div>
			</Message>
		</div>
	</div>
</template>

<script>
	import { infoCtrl } from "@/components/dashboard/petugas/controllers/info";
	import { Cruds } from "@/components/dashboard/petugas/cruds/save-logs/controller.ts";

	const logCtrl = new Cruds();

	export default {
		name: "MlInfoComp",
		data() {
			return {};
		},
		computed: {
			infoCtrlItem() {
				const items = infoCtrl.items ?? [];
				const pruned = items.length > 20 ? items.slice(-20) : items;
				return [...pruned].reverse().slice(0, 5);
			},
		},

		methods: {
			getSeverity(status) {
				const s = (status ?? "").toString().toLowerCase();
				if (s.includes("aman")) return "success";
				if (s.includes("tidak bersih")) return "warn";
				if (s.includes("menumpuk")) return "error";
				return "info";
			},
			async addLogs(e) {
				await logCtrl.add({
					label: e.label,
					frame: e.frame,
					roi: e.roi,
					h_mean: e.features.h_mean,
					s_mean: e.features.s_mean,
					v_mean: e.features.v_mean,
					h_std: e.features.h_std,
					s_std: e.features.s_std,
					v_std: e.features.v_std,
					laplacian_var: e.features.laplacian_var,
					edge_ratio : e.features.edge_ratio,
					shape_area_ratio : e.features.shape_area_ratio,
				});
			},
		},
		mounted() {},
	};
</script>
