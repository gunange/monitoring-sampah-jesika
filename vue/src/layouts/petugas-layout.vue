<script setup>
	import { RouterView } from "vue-router";
	import MainDashboard from "@/widgets/layouts/dashboard/main-dashboard.vue";

	import { dashboard, dataEnv } from "@/components/dashboard/petugas/config/index";
</script>

<template>
	<main>
		<MainDashboard
			:sidebar="dashboard.sidebar"
			title="Petugas"
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
	import { Controller as UserStorageController } from "@/components/dashboard/petugas/controller.ts";
	import { RequestApiController } from "@/controller/others/RequestApiController";
	import { wsHeandler } from "@/components/dashboard/petugas/ws-heandler";

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

			if (auth.store.isAuth && auth.store.user.User.role === "p3tug45") {
				auth.setToken();
				wsHeandler.init(auth.token);
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
			wsHeandler.close();
			next();
		},
	};
</script>
