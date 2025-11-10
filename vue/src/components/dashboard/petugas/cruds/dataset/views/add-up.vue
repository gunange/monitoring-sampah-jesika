<script setup>
	import { ref, computed, reactive } from "vue";

	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";
	import { Cruds } from "../controller";
	import { api } from "@/config/apiConfig.js";

	const main = new Cruds();

	const modal = main.modal;
	const form = ref({});
	const ref_form = ref();
	/* ----- machine-learning ----- */
	const imgVersion = ref("0");
	const running = ref(false);
	const pathMl = `${api.url_api}machine-learning`;

	/* ----- computed ----- */
	const urlMlStream = computed(
		() => `${api.url_ml_http}/camera/last-frame?v=${imgVersion.value}`
	);

	/* ----- action dialog ----- */
	const open = async (act, uid) => {
		main.modal.act = act;
		main.modal.label = "Add Dataset";
		form.value = {};

		await checkMl();
		await main.open(act);
		if(!running.value) return;
		refreshStream();
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

	/* ----- method ----- */
	const refreshStream = () => {
		imgVersion.value = Date.now();
	};

	const checkMl = async () => {
		const res = await fetch(pathMl, { cache: "no-store" });
		const json = await res.json(); // { name: 'Machine Learning', running: boolean }
		const wasRunning = running.value;
		running.value = !!json.running;
		if (running.value && !wasRunning) {
			refreshStream();
		}
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<!-- eslint-disable vue/no-v-model-argument -->
		<Dialog
			v-model:visible="modal.show"
			:breakpoints="breakpoints.dialog"
			:style="{ width: '60vw' }"
			modal
		>
			<template #header>
				<h6 class="text-primary text-sm flex items-center">
					<i class="pi pi-tags mr-2"></i>
					<span>{{ modal.label }}</span>
				</h6>
			</template>
			<div class="text-center" v-if="!running">
				<div class="mt-2 text-xs text-gray-500">
					Status Machine Learning: <b>{{ running ? "RUNNING" : "STOPPED" }}</b>
				</div>
			</div>

			<VeeForm @submit="onSave" :initial-values="form" ref="ref_form" v-else>
				<div class="text-xs grid grid-cols-1 gap-4">
					<img
						:key="imgVersion"
						:src="urlMlStream"
						alt="Live Stream"
						class="w-full rounded-sm"
					/>

					<div class="form">
						<VeeField
							v-slot="{}"
							name="label"
							rules="required"
							v-model="form.label"
						>
							<label>
								<span>Label</span>
								<span class="text-red-500"
									>* <VeeErrorMessage name="label"
								/></span>
							</label>

							<v-select
								placeholder="Pilih Label"
								v-model="form.label"
								:options="['Aman', 'Tidak Bersih', 'Sampah Menumpuk']"
							/>
						</VeeField>
					</div>
				</div>

				<button type="submit" class="hidden" ref="refBtnAddAndUp">submit</button>
			</VeeForm>
			<template #footer>
				<div class="flex justify-end" v-if="running">
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
