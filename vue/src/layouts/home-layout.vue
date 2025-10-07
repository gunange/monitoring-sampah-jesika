<script setup>
	import { onMounted } from "vue";
	import { RouterView } from "vue-router";

	import "@/assets/css/home/main.css";
	import "@/assets/css/home/responsif.css";
	import "@/assets/css/home/costume.css";

	import LoadingArea from "@/widgets/others/loading-area.vue";
	import LandingPageWidget from "@/widgets/layouts/home/Main.vue";

	import { LoadHtml } from "@/controller/tools";

	const tools = new LoadHtml();

	const isLoadHtml = tools.items.html.load;

	onMounted(() => {
		tools.run();
	});
</script>

<template>
	<div class="home">
		<LoadingArea v-show="isLoadHtml" />
		<LandingPageWidget v-show="!isLoadHtml">
			<router-view />
		</LandingPageWidget>
	</div>
</template>

<script>
	import { AuthController } from "@/controller/controllers/AuthController";
	import { Controller as UserStorageController } from "@/components/home/controller";
	import { RequestApiController } from "@/controller/others/RequestApiController";
	import { path_api } from "@/components/home/data-env";

	const auth = new AuthController();
	const apiC = new RequestApiController();
	export default {
		computed: {
			user() {
				return auth.user;
			},
		},
		// async beforeRouteEnter(to, from, next) {
		// 	apiC.setupNewPath(`${apiC.url}${path_api}`);
		// 	await auth.init();
		// 	apiC.resetPath();

		// 	if (auth.store.isAuth && auth.store.user.Role.role === "s1sw4") {
		// 		const store = new UserStorageController() ;
				
		// 		store.store.isAuth = true;
		// 		auth.setToken();
		// 		next();
		// 		return;
		// 	}

		// 	next();
		// },
		// async beforeRouteLeave(to, from, next) {
		// 	await auth.reset();
		// 	await new UserStorageController().dispose();
		// 	next();
		// },
	};
</script>
