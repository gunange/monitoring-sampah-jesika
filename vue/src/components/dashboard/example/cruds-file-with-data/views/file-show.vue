<script setup>
	import { ref, computed } from "vue";
	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";
	import PdfVue from "@/widgets/others/PdfVue/PdfUrl.vue";

	import { Cruds } from "../controller";

	const main = new Cruds();
	const modal = main.modal;
	const fileInfo = ref({});
	const form = ref({});
	const ref_pdf = ref();

	const imageType = [
		"image/jpeg",
		"image/png",
		"image/gif",
		"image/bmp",
		"image/svg+xml",
		"image/webp",
	];

	const pdfType = ["application/pdf"];

	/* ----- computed ----- */

	/* ----- action dialog ----- */
	const open = async (act, item) => {
		ref_pdf.value = null;
		main.setUid(item.id);
		form.value = main.data;

		const { data, status } = await main.getFileInfo(form.value.storageUid);

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
			:style="{ width: '45vw' }"
			modal
			maximizable
		>
			<template #header>
				<h6 class="text-blue-400 text-sm flex items-center">
					<i class="pi pi-file mr-2"></i> <span>File Show</span>
				</h6>
				<ButtonGroup v-if="ref_pdf">
					<Button
						icon="pi pi-minus-circle"
						severity="warn"
						outlined
						@click="$refs.ref_pdf.perkecil"
					/>
					<Button
						icon="pi pi-plus-circle"
						outlined
						@click="$refs.ref_pdf.perbesar"
					/>
				</ButtonGroup>
			</template>
			<template #default>
				<div class="" v-if="fileInfo?.mime_type">
					<div class="" v-if="imageType.includes(fileInfo?.mime_type)">
						<Image
							:src="main.urlStorage + '/' + form.storageUid"
							alt="Image"
							imageClass="w-full"
						/>
					</div>
					<div class="w-full" v-else-if="pdfType.includes(fileInfo?.mime_type)">
						<PdfVue :url="main.urlStorage + '/' + form.storageUid" ref="ref_pdf" />
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
