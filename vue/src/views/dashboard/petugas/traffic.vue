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
			<div class="card ">
				<TrafficView/>
			</div>
		</div>
	</div>
</template>

<script>
	import BradcumpWidget from "@/widgets/others/bardcump-widget.vue";
	import TrafficView from "@/components/dashboard/petugas/components/traffic-view.vue";
	import { dataEnv } from "@/components/dashboard/admin/config/index.ts";

	export default {
		name: "MainView",
		components: {
			BradcumpWidget,
			TrafficView
		},
		computed: {
			pathRoute() {
				return dataEnv.path_route;
			},
		},
	};
</script>
