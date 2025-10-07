<script setup>
	import { ref, computed, reactive } from "vue";
	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";

	const modal = reactive({
		show: false,
		message: "",
	});

	/* ----- computed ----- */
	const form = ref();

	/* ----- action dialog ----- */
	const open = async (data) => {
		console.log(data);
		modal.show = true;
		form.value = data ?? {};
	};
	const close = async () => {
		modal.show = false;
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
			class="rounded-lg shadow-lg"
		>
			<template #header>
				<div class="flex items-center text-green-600 gap-2">
					<i class="pi pi-check-circle text-lg"></i>
					<h5 class="font-semibold">Pendaftaran Berhasil</h5>
				</div>
			</template>

			<template #default>
				<div class="text-center p-4">
					<p class="text-gray-700 text-sm mb-4">
						Selamat! Pendaftaran berhasil dilakukan.
					</p>
					<p class="text-sm text-gray-600">
						<b>Username:</b> <span class="text-black">{{ form?.username }}</span
						><br />
						<b>Password:</b> <span class="text-black">{{ form?.password }}</span>
					</p>
				</div>
			</template>

			<template #footer>
				<div class="flex justify-end pb-2">
					<Button
						type="button"
						label="Tutup"
						size="small"
						class="p-button-success"
						icon="pi pi-check"
						@click="close"
					/>
				</div>
			</template>
		</Dialog>
	</main>
</template>
