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
			<div class="card p-3 text-center">
				<p>Main View</p>
			</div>
		</div>
	</div>
</template>

<script>
	import BradcumpWidget from "@/widgets/others/bardcump-widget.vue";
	import { dataEnv } from "@/components/dashboard/admin/config/index.ts";

	export default {
		name: "MainView",
		components: {
			BradcumpWidget,
		},
		computed: {
			pathRoute() {
				return dataEnv.path_route;
			},
		},
	};
</script>
