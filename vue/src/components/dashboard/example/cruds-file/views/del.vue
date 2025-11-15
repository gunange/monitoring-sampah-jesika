<script setup>
	import { ref, computed } from "vue";
	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";

	import { Cruds } from "../controller";

	const main = new Cruds();

	const modal = main.modal;

	/* ----- computed ----- */
	const ref_data = ref({});

	/* ----- action dialog ----- */
	const open = async (act, uid) => {
		main.setUid(uid);
		ref_data.value = main.data;
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
			:style="{ width: '30vw' }"
			modal
		>
			<template #header>
				<h6 class="text-red-300 text-sm flex items-center">
					<i class="pi pi-trash mr-2"></i> <span>Hapus Data</span>
				</h6>
			</template>
			<template #default>
				<div class="text-center">
					<p>
						Apakah anda akan menghapus data <b>{{ ref_data.label }} </b> ?
					</p>
				</div>
			</template>
			<template #footer>
				<div class="flex justify-end">
					<Button
						type="button"
						label="Hapus"
						icon="pi pi-trash"
						size="small"
						@click="onSave"
						:loading="modal.proses_form"
						outlined
					></Button>
				</div>
			</template>
		</Dialog>
	</main>
</template>
