<script setup>
	import { ref, computed, reactive } from "vue";

	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";
	import { Cruds } from "./controller";
	import { generateUniqID } from "@/controller/tools/other.ts";

	import { atribut } from "@/services/atribut";

	import DialogSukses from "./DialogSukses.vue";

	const main = new Cruds();

	const modal = main.modal;
	const form = ref({});
	const ref_form = ref();
	const ref_dialog = ref();
	/* ----- computed ----- */

	/* ----- on submit ----- */
	const onSave = async (e, { resetForm }) => {
		if (modal.proses_form) return;
		modal.proses_form = true;

		const req = await main.add(e);

		if (req.status == 200) {
			ref_dialog.value.open(req.data);
			resetForm();
		} else {
			await main.toast.add({
				severity: "error",
				summary: req.message,
				detail: req.error,
				life: 5000,
			});
		}

		modal.proses_form = false;
	};

	/* ----- method ----- */
</script>

<template>
	<main>
		<h2 class="text-xl font-semibold text-yellow-500 mb-4 text-center">
			Formulir Pendaftaran Pelanggan
		</h2>
		<VeeForm @submit="onSave" :initial-values="form" ref="ref_form">
			<div class="text-xs grid grid-cols-1 gap-4">
				<div class="form">
					<VeeField
						v-slot="{ field }"
						name="no_staf"
						rules="required|between:9,9"
						v-model="form.no_staf"
					>
						<label>
							<span>No. Pelanggan</span>
							<span class="text-red-500"
								>* <VeeErrorMessage name="no_staf"
							/></span>
						</label>
						<InputText
							v-bind="field"
							placeholder="Masukan No. Pelanggan"
							class="text-xs"
							autocomplete="off"
						/>
					</VeeField>
				</div>

				<div class="form">
					<VeeField
						v-slot="{ field }"
						name="nama"
						rules="required"
						v-model="form.nama"
					>
						<label>
							<span>Nama</span>
							<span class="text-red-500">* <VeeErrorMessage name="nama" /></span>
						</label>
						<InputText
							v-bind="field"
							placeholder="Masukan Nama"
							class="text-xs"
							autocomplete="off"
						/>
					</VeeField>
				</div>

				<div class="form">
					<VeeField
						v-slot="{ field }"
						name="no_hp"
						rules="required|phone"
						v-model="form.no_hp"
					>
						<label>
							<span>No. HP</span>
							<span class="text-red-500">* <VeeErrorMessage name="no_hp" /></span>
						</label>
						<InputText
							v-bind="field"
							placeholder="Masukan No. HP"
							class="text-xs"
							autocomplete="off"
						/>
					</VeeField>
				</div>

				<div class="form">
					<VeeField
						v-slot="{ field }"
						name="alamat"
						rules="required"
						v-model="form.alamat"
					>
						<label>
							<span>Alamat</span>
							<span class="text-red-500">* <VeeErrorMessage name="alamat" /></span>
						</label>
						<InputText
							v-bind="field"
							placeholder="Masukan Alamat"
							class="text-xs"
							autocomplete="off"
						/>
					</VeeField>
				</div>
			</div>

			<div class="flex justify-end mt-5">
				<Button
					type="submit"
					label="Daftar"
					size="small"
					icon="pi pi-send"
					:loading="modal.proses_form"
					outlined
				/>
			</div>
		</VeeForm>
		<DialogSukses ref="ref_dialog" />
	</main>
</template>
