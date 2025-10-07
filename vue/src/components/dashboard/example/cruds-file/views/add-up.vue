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

	const itemProduk = computed(() => {
		return atribut.produk.items.map((e) => {
			return {
				...e,
				label: `${e.nama} - ${e.harga}`,
			};
		});
	});

	/* ----- action dialog ----- */
	const open = async (act, uid) => {
		main.modal.act = act;
		main.modal.label = "act" == "up" ? "Update Oderan" : "Order Beras";
		form.value = {};

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
					<div class="form" v-if="modal.act == 'add'">
						<VeeField
							v-slot="{ field }"
							name="produk_id"
							rules="required"
							v-model="form.produk_id"
						>
							<label>
								<span>Produk</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="produk_id"
								/></span>
							</label>

							<v-select
								placeholder="Pilih Produk"
								:reduce="(x) => x.id"
								v-model="form.produk_id"
								:options="itemProduk"
								:appendToBody="true"
								:loading="atribut.produk.data.load"
								@open="atribut.produk.init()"
							/>
						</VeeField>
					</div>

					<div class="form" >
						<VeeField
							v-slot="{ field }"
							name="jumlah"
							rules="required|number"
							v-model="form.jumlah"
						>
							<label>
								<span>Jumlah</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="jumlah"
								/></span>
							</label>

							<InputNumber
								v-model="form.jumlah"
								inputId="jumlah"
								placeholder="Masukkan Jumlah"
								showButtons
								buttonLayout="horizontal"
								:step="1"
								mode="decimal"
								:useGrouping="false"
								fluid
							>
								<template #incrementbuttonicon>
									<span class="pi pi-plus" />
								</template>
								<template #decrementbuttonicon>
									<span class="pi pi-minus" />
								</template>
							</InputNumber>
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
