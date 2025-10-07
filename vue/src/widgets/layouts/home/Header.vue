<template>
	<header class="sticky top-0 z-50 bg-white dark:bg-zinc-900 shadow-md md:px-25">
		<div class="py-4 flex justify-between items-center">
			<h1 class="text-xl font-bold text-primary">{{ appName }}</h1>
			<div class="">
				<Button
					label="Login"
					icon="pi pi-sign-in"
					size="small"
					@click="$router.push('/login')"
				/>
			</div>
		</div>
	</header>
</template>

<script>
	import { Controller as UserStorageController } from "@/components/home/controller";
	import { appName } from "@/config/appInfo";

	import { AuthController } from "@/controller/controllers/AuthController.ts";

	const auth = new AuthController();

	const userStorage = new UserStorageController();
	export default {
		data() {
			return {
				appName,
			};
		},
		components: {},

		computed: {
			isAuthorized() {
				return userStorage.isAuth;
			},
		},
		methods: {
			async logout() {
				await auth.signOut(() => {
					this.$router.push("/login");
				});
			},
		},
	};
</script>
