<script setup>
	import { ref, computed } from "vue";
	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";

	import { Cruds } from "../controller";

	const main = new Cruds();
	const modal = main.modal;
	const fileInfo = ref({});
	const form = ref({});

	const imageType = [
		"image/jpeg",
		"image/png",
		"image/gif",
		"image/bmp",
		"image/svg+xml",
		"image/webp",
	];

	/* ----- computed ----- */

	/* ----- action dialog ----- */
	const open = async (act, item) => {
		main.setUid(item.id);
		form.value = main.data;

		const { data, status } = await main.getFileInfo(form.value.storage_uid);

		if (status == 200) {
			fileInfo.value = data;
		}

		await main.open();
	};
	const close = async () => {
		main.close();
	};

	/* ----- on submit ----- */
	const onSave = async () => {
		if (modal.proses_form) return;
		modal.proses_form = true;

		await main.del();
		close();
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<!-- eslint-disable vue/no-v-model-argument -->
		<Dialog
			v-model:visible="modal.show"
			:breakpoints="breakpoints.dialog"
			:style="{ width: '65vw' }"
			modal
		>
			<template #header>
				<h6 class="text-blue-400 text-sm flex items-center">
					<i class="pi pi-file mr-2"></i> <span>File Show</span>
				</h6>
			</template>
			<template #default>
				<div class="" v-if="fileInfo?.mime_type">
					<div class="" v-if="imageType.includes(fileInfo?.mime_type)">
						<Image
							:src="main.urlStorage + '/' + form.storage_uid"
							alt="Image"
							imageClass="w-full"
						/>
					</div>
					<div
						class="flex justify-center flex-col items-center bg-gray-300 h-[200px] text-white rounded"
						v-else
					>
						<i class="pi pi-exclamation-circle text-[80px] mb-5" />
						<p>File Tidak Support</p>
					</div>
				</div>
				<div class="text-red-400 text-center" v-else>
					<i class="pi pi-exclamation-circle text-[80px] mb-3" />
					<p>File Tidak Ditemukan Hubungi Panitia/Admin</p>
				</div>
			</template>
		</Dialog>
	</main>
</template>
