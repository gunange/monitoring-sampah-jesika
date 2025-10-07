<script setup>
	import { ref, computed, reactive } from "vue";

	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";
	import { Cruds } from "../controller";
	import { atribut } from "@/services/atribut";

	const main = new Cruds();

	const modal = main.modal;
	const form = ref({});
	const ref_form = ref();
	/* ----- computed ----- */

	/* ----- action dialog ----- */
	const open = async (act, uid) => {
		main.modal.act = act;
		main.modal.label = "act" == "up" ? "Update Oderan" : "Order Beras";
		form.value = {};
		await atribut.jenisPengaduan.init()

		await main.open(act);
		ref_form.value.resetForm();

		if (act == "up") {
			main.setUid(uid);
			ref_form.value.setValues(main.data);
		}
	};
	const close = async () => {
		main.close();
	};

	/* ----- on submit ----- */
	const onSave = async (e, { resetForm }) => {
		if (modal.proses_form) return;
		modal.proses_form = true;

		if (modal.act == "add") {
			await main.add(e);
		} else if (modal.act == "up") {
			await main.up(e);
		}
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<Dialog
			v-model:visible="modal.show"
			:breakpoints="breakpoints.dialog"
			:style="{ width: '30vw' }"
			modal
		>
			<template #header>
				<h6 class="text-primary text-sm flex items-center">
					<i class="pi pi-tags mr-2"></i>
					<span>{{ modal.label }}</span>
				</h6>
			</template>

			<VeeForm @submit="onSave" :initial-values="form" ref="ref_form">
				<div class="text-xs grid grid-cols-1 gap-4">
					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="jenis_id"
							rules="required"
							v-model="form.jenis_id"
						>
							<label>
								<span>Jenis Pengaduan</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="jenis_id"
								/></span>
							</label>
							<v-select
								placeholder="Pilih Jenis Pengaduan"
								:reduce="(x) => x.id"
								label="nama"
								v-model="form.jenis_id"
								:options="atribut.jenisPengaduan.items"
								:appendToBody="true"
								:loading="atribut.jenisPengaduan.data.load"
							/>
						</VeeField>
					</div>

					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="keterangan"
							rules="required"
							v-model="form.keterangan"
						>
							<label>
								<span>Keterangan</span>
								<span class="text-red-500">
									* <VeeErrorMessage name="keterangan" />
								</span>
							</label>
							<Textarea
								v-bind="field"
								placeholder="Masukan Keterangan"
								class="text-xs mt-2 w-full"
								rows="3"
								autocomplete="off"
							/>
						</VeeField>
					</div>

					<div class="form">
						<VeeField
							v-slot="{ field }"
							name="alamat_kejadian"
							rules="required"
							v-model="form.alamat_kejadian"
						>
							<label>
								<span>Alamat Kejadian</span>
								<span class="text-red-500">
									* <VeeErrorMessage name="alamat_kejadian" />
								</span>
							</label>
							<Textarea
								v-bind="field"
								placeholder="Masukan Alamat Kejadian"
								class="text-xs mt-2 w-full"
								rows="3"
								autocomplete="off"
							/>
						</VeeField>
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
						@click="$refs.refBtnAddAndUp.click()"
						:loading="modal.proses_form"
						outlined
					/>
				</div>
			</template>
		</Dialog>
	</main>
</template>
