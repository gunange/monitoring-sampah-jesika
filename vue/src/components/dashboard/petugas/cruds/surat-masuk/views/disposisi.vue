<script setup>
	import { ref, computed, reactive } from "vue";

	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";
	import { Cruds } from "../controller";

	const main = new Cruds();

	const modal = main.modal;
	const form = ref({});
	const ref_form = ref();
	/* ----- computed ----- */

	/* ----- action dialog ----- */
	const open = async (act, item) => {
		main.modal.act = act;
		main.modal.label = "Disposisi Surat Masuk";
		form.value = {};

		await main.open(act);
		ref_form.value.resetForm();

		main.setUid(item.id);
	};
	const close = async () => {
		main.close();
	};

	/* ----- on submit ----- */
	const onSave = async (e, { resetForm }) => {
		if (modal.proses_form) return;
		modal.proses_form = true;

		await main.disposisi(e);
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
							name="catatan"
							rules="required"
							v-model="form.catatan"
						>
							<label>
								<span>Catatan</span>
								<span class="text-red-500">
									* <VeeErrorMessage name="catatan" />
								</span>
							</label>

							<Textarea
								v-bind="field"
								placeholder="Masukkan catatan disposisi"
								class="text-xs mt-2 w-full"
								rows="4"
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
