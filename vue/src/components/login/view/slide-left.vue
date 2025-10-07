<script setup>
	import { appLogo, appCode, appName, appDeskripsi } from "@/config/appInfo.js";
</script>
<template>
	<div class="left flex-initial w-3/8 text-indigo-900 max-lg:hidden relative">
		<div class="pt-6 p-4">
			<router-link to="/">
				<div class="flex justify-start align-items-center">
					<div class="">
						<img class="w-12" :src="appLogo" alt="Logo" />
					</div>
					<div class="ps-2 flex justify-center flex-col">
						<h4 class="font-bold">{{ appCode }}</h4>
						<p class="text-xs">{{ appName }}</p>
					</div>
				</div>
			</router-link>
			<div class="mt-10">
				<p class="text-[40px] g-ff-sacramento font-bold mb-3">Selamat Datang</p>
				<div class="w-16 h-[3px] bg-yellow-400 my-3 rounded-full" />
				<p class="lg:w-[85%] leading-relaxed text-[11px]">
					{{ appDeskripsi }}
				</p>
				<p class="mt-4 italic text-sm text-yellow-300">
					"Bekerja cerdas adalah bagian dari budaya kita."
				</p>

				<div class="shape-art mt-6" />
			</div>
		</div>
	</div>
</template>
