<script setup>
	import IconField from "primevue/iconfield";
	import InputIcon from "primevue/inputicon";
	import OverlayBadge from "primevue/overlaybadge";
	import { onMounted } from "vue";

	import { ref } from "vue";

	import { dashboardStore } from "@/stores/others/dashboard";
	import { appLogo } from "@/config/appInfo.js";

	const sideActive = dashboardStore();

	const search = ref("");

	const props = defineProps({
		profilMenu: {
			type: Array,
		},

		nama: {
			type: String,
			default: "Unknow",
		},
	});

	onMounted(() => {
		if (window.innerWidth < 640) {
			sideActive.sidebarActive = false;
		}
	});
</script>

<template>
	<div>
		<div class="flex">
			<div class="flex-none">
				<Button
					id="menu-toggle"
					@click="sideActive.sidebarActive = !sideActive.sidebarActive"
					class="px-5 text-[.9rem]"
				>
					<i :class="{ 'lni lni-chevron-left me-2': sideActive.sidebarActive }"></i>
					<span class="pi pi-list"></span>
					<span class="max-sm:hidden">Menu</span>
				</Button>
			</div>
			<div class="flex-none w-2/4 search px-5 max-sm:hidden">
				<IconField>
					<InputIcon class="pi pi-search text-xs" />
					<InputText
						v-model="search"
						placeholder="Search.."
						variant="filled"
						class="w-full text-xs dark:bg-slate-600"
					/>
				</IconField>
			</div>
			<div class="flex-1 flex justify-end align-items-center">
				<div
					class="ml-10 flex justify-end cursor-pointer items-center text-slate-500"
					@click="$refs.profilMenu.toggle"
				>
					<p class="text-xs font-bold dark:text-blue-400">{{ nama }}</p>
					<div class="image ml-3">
						<img :src="appLogo" alt="" />
						<span class="status"></span>
					</div>
					<div class="flex justify-center items-center ml-1">
						<i class="pi pi-chevron-down text-blue-400 text-[.5rem]"></i>
					</div>
				</div>
				<Menu
					ref="profilMenu"
					:model="profilMenu"
					:popup="true"
					class="animated fadeInUp text-xs"
					pt:root:style="top : 95px; min-width: 14.5rem;"
				/>
			</div>
		</div>
	</div>
</template>
