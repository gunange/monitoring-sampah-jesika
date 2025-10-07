<script setup>
	import { appLogo, appCode, appName, appDeskripsi } from "@/config/appInfo.js";
	const props = defineProps({
		home: {
			type: Object,
			default: {
				icon: "pi pi-home",
			},
		},
		items: {
			type: Array,
			default: [
				{ label: "Electronics", route: "/admin" },
				{ label: "Computer" },
				{ label: "Accessories" },
			],
		},
		title: {
			type: String,
			default: appName,
		},
		subTitle: {
			type: String,
			default: appDeskripsi,
		},
	});
</script>

<template>
	<div class="rounded-lg p-4 breadcump shadow-sm">
		<p class="text-blue-500 text-2xl">{{ title }}</p>
		<p class="text-gray-500 dark:text-slate-300 text-xs mt-2">{{ subTitle }}</p>
		<Breadcrumb :home="home" :model="items" class="mt-6 text-sm">
			<template #item="{ item, props }">
				<router-link
					:to="item.route"
					v-if="item.route"
					class="text-zinc-600 dark:text-slate-400 hover:text-blue-600 transition duration-150"
				>
					<span :class="item.icon" />
					<span class="">{{ item.label }}</span>
				</router-link>
				<div
					v-else
					class="cursor-pointer text-zinc-600 dark:text-slate-400 hover:text-blue-600 transition duration-150"
				>
					<span :class="item.icon" />
					<span class="">{{ item.label }}</span>
				</div>
			</template>
		</Breadcrumb>
	</div>
</template>
