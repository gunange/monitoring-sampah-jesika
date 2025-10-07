<script setup>
	import { RouterView } from "vue-router";
	import MainDashboard from "@/widgets/layouts/dashboard/main-dashboard.vue";

	import { dashboard, dataEnv } from "@/components/dashboard/camat/config/index";
</script>

<template>
	<main>
		<MainDashboard
			:sidebar="dashboard.sidebar"
			title="Camat"
			:sub-title="'@' + user?.User?.username"
			:nama="user?.nama"
			:navbar="dashboard.navbar"
		>
			<router-view />
		</MainDashboard>
	</main>
</template>

<script>
	import { AuthController } from "@/controller/controllers/AuthController.ts";
	import { Controller as UserStorageController } from "@/components/dashboard/camat/controller.ts";
	import { RequestApiController } from "@/controller/others/RequestApiController";

	const auth = new AuthController();
	const apiC = new RequestApiController();
	export default {
		computed: {
			user() {
				return auth.user;
			},
		},
		async beforeRouteEnter(to, from, next) {
			apiC.setupNewPath(`${apiC.url}${dataEnv.path_api}`);
			await auth.init();
			apiC.resetPath();

			if (auth.store.isAuth && auth.store.user.User.role === "c4m4t") {
				auth.setToken();
				next();
				return;
			}

			await auth.signOut(() => {
				next("/login");
			});
		},
		async beforeRouteLeave(to, from, next) {
			await auth.reset();
			await new UserStorageController().dispose();
			next();
		},
	};
</script>
