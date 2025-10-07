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
		percentUpload.value = 0;
		main.modal.act = act;
		main.modal.label = act === "add" ? "Tambah" : "Update" + " Surat Masuk";
		form.value = {};

		await main.open(act);

		if (act === "up") {
			main.setUid(data.id);

			ref_form.value.setValues({ ...main.data, tanggal: new Date(main.data.tanggal) });
		}
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

		if (modal.act === "add") {
			percentUpload.value = 0;
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
		}

		// Kirim request
		if (modal.act === "add") {
			await main.addWithFile(e, {
				headers: {
					"Content-Type": "multipart/form-data",
				},
				onUploadProgress: (progressEvent) => {
					percentUpload.value = Math.round(
						(progressEvent.loaded * 100) / progressEvent.total
					);
				},
			});
		} else {
			await main.up(e);
		}
		selectedFile.value = null;
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<Dialog
			v-model:visible="modal.show"
			:breakpoints="breakpoints.dialog"
			:style="{ width: '40vw' }"
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
							name="nomor"
							rules="required"
							v-model="form.nomor"
						>
							<label>
								<span>Nomor</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="nomor"
								/></span>
							</label>
							<InputText
								v-bind="field"
								placeholder="Masukan nomor surat"
								class="text-xs"
								autocomplete="off"
							/>
						</VeeField>
					</div>

					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="pengirim"
							rules="required"
							v-model="form.pengirim"
						>
							<label>
								<span>Pengirim</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="pengirim"
								/></span>
							</label>
							<InputText
								v-bind="field"
								placeholder="Masukan nama pengirim"
								class="text-xs"
								autocomplete="off"
							/>
						</VeeField>
					</div>

					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="perihal"
							rules="required"
							v-model="form.perihal"
						>
							<label>
								<span>Perihal</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="perihal"
								/></span>
							</label>
							<InputText
								v-bind="field"
								placeholder="Masukan perihal surat"
								class="text-xs"
								autocomplete="off"
							/>
						</VeeField>
					</div>

					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="tanggal"
							rules="required"
							v-model="form.tanggal"
						>
							<label>
								<span>Tanggal</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="tanggal"
								/></span>
							</label>
							<DatePicker
								v-bind="field"
								v-model="form.tanggal"
								dateFormat="DD, dd  MM yy"
								class="text-xs w-full"
								showIcon
							/>
						</VeeField>
					</div>

					<div class="" v-if="modal.act === 'add'">
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
