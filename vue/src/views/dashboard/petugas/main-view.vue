<template>
	<div>
		<div class="px-5 mt-5">
			<BradcumpWidget
				:home="{
					icon: 'pi pi-home',
					route: pathRoute,
				}"
				:items="[{ label: 'Library', route: `/${pathRoute}` }]"
			/>
		</div>
		<div class="px-5 mt-5">
			<MlConfigComp />
		</div>
		<div class="px-5 mt-5">
			<MlInfoComp />
		</div>
	</div>
</template>

<script>
	import BradcumpWidget from "@/widgets/others/bardcump-widget.vue";
	import { dataEnv } from "@/components/dashboard/admin/config/index.ts";

	import MlComp from "@/components/dashboard/petugas/components/ml-view.vue";
	import MlConfigComp from "@/components/dashboard/petugas/components/ml-config.vue";
	import MlInfoComp from "@/components/dashboard/petugas/components/ml-info-view.vue";

	export default {
		name: "MainView",
		components: {
			BradcumpWidget,
			MlComp,
			MlInfoComp,
			MlConfigComp,
		},
		computed: {
			pathRoute() {
				return dataEnv.path_route;
			},
		},
	};
</script>
