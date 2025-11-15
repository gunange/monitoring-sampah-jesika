<script setup>
	import { ref, computed, reactive } from "vue";

	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";
	import { Cruds, MainData } from "../controller";
	import FileUploader from "@/widgets/others/FileUploader.vue";
	import { atribut } from "@/services/atribut";
	import { appMaxFileSize } from "@/config/appInfo";

	const main = new Cruds();

	const modal = main.modal;
	const form = ref({});
	const ref_form = ref();

	/* ----- computed ----- */

	/* ----- method ----- */

	/* ----- action dialog ----- */
	const open = async (act, data) => {
		main.modal.act = act;
		percentUpload.value = 0;
		main.modal.label = "Upload Lampiran";
		form.value = {};

		main.setUid(data.id);
		await main.open(act);
	};
	const close = async () => {
		main.close();
	};

	/* ----- heandle fileuploader ----- */

	const maxFileSize = ref(appMaxFileSize);
	const selectedFile = ref(null);
	const percentUpload = ref(0);

	const onFileSelected = (file) => {
		selectedFile.value = file;
	};

	/* ----- on submit ----- */
	const onSave = async () => {
		if (modal.proses_form) return;
		const e = {}
		modal.proses_form = true;
		if (selectedFile.value) {
			e.file = selectedFile.value;
		} else {
			await main.toast.add({
				severity: "error",
				summary: "Error",
				detail: "Lampiran Wajib Upload",
				life: 5000,
			});
			modal.proses_form = false;
			return;
		}

		// Kirim request
		await main.upload(e, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
			onUploadProgress: (progressEvent) => {
				percentUpload.value = Math.round(
					(progressEvent.loaded * 100) / progressEvent.total
				);
			},
		});
		selectedFile.value = null;
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
		>
			<template #header>
				<h6 class="text-primary text-sm flex items-center">
					<i class="pi pi-upload mr-2"></i>
					<span> {{ modal.label }} </span>
				</h6>
			</template>

			<div class="">
				<FileUploader
					:accept="atribut.allow_types"
					:maxFileSize="maxFileSize"
					:totalSizePercent="percentUpload"
					@file-selected="onFileSelected"
				/>
			</div>

			<template #footer>
				<div class="flex justify-end">
					<Button
						type="button"
						label="Save"
						size="small"
						icon="pi pi-send"
						outlined
						@click="onSave"
						:loading="modal.proses_form"
					/>
				</div>
			</template>
		</Dialog>
	</main>
</template>
