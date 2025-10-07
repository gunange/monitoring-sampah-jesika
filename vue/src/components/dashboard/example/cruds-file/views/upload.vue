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

	const itemsRekening = computed(() => {
		return atribut.rekening.items.map((e) => {
			return { ...e, label: `${e.no_rekening} - ${e.nama_bank}` };
		});
	});

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
	const onSave = async (e, { resetForm }) => {
		if (modal.proses_form) return;
		modal.proses_form = true;
		if (selectedFile.value) {
			e.file = selectedFile.value;
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

			<VeeForm @submit="onSave" :initial-values="form" ref="ref_form">
				<div class="text-xs grid grid-cols-1 gap-4">
					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="rekening_id"
							rules="required"
							v-model="form.rekening_id"
						>
							<label>
								<span>Jenis Berkas</span>
								<span class="text-red-500">
									* <VeeErrorMessage name="rekening_id" />
								</span>
							</label>

							<v-select
								placeholder="Pilih Rekening"
								v-model="form.rekening_id"
								:reduce="(x) => x.id"
								:appendToBody="true"
								:options="itemsRekening"
								:loading="atribut.rekening.data.load"
								@open="atribut.rekening.init()"
							/>
						</VeeField>
					</div>

					<div class="">
						<FileUploader
							:accept="atribut.allow_types"
							:maxFileSize="maxFileSize"
							:totalSizePercent="percentUpload"
							@file-selected="onFileSelected"
						/>
					</div>
				</div>

				<button type="submit" class="hidden" ref="refBtnAddAndUp">submit</button>
			</VeeForm>

			<template #footer>
				<div class="flex justify-end">
					<Button
						type="button"
						label="Save"
						size="small"
						icon="pi pi-send"
						outlined
						@click="$refs.refBtnAddAndUp.click()"
						:loading="modal.proses_form"
					/>
				</div>
			</template>
		</Dialog>
	</main>
</template>
