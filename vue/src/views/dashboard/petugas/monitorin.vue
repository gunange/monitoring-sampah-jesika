<template>
	<div>
		
		<div class="px-5 mt-5">
			<div class="card p-3 text-center">
				<img :src="urlMlStream" alt="Live Stream" class="w-full rounded-sm">
			</div>
		</div>
	</div>
</template>

<script>
	import BradcumpWidget from "@/widgets/others/bardcump-widget.vue";
	import { dataEnv } from "@/components/dashboard/admin/config/index.ts";
	import { api } from "@/config/apiConfig.js";

	export default {
		name: "MainView",
		components: {
			BradcumpWidget,
		},
		computed: {
			pathRoute() {
				return dataEnv.path_route;
			},
			// Gunakan host ML dari env untuk MJPEG stream
			urlMlStream() {
				return `${api.url_ml_http}/camera/stream`;
			},
		},
	};
</script>
