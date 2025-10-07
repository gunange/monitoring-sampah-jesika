<script setup>
	import { ref, computed } from "vue";
	import { breakpoints } from "@/config/vue-prime/appPrimeConfig.ts";

	import { Cruds } from "../controller";

	const main = new Cruds();

	const modal = main.modal;

	/* ----- computed ----- */
	const statusActive = ref(null);
	const items = ref([]);

	// Mapping status tindak lanjut ke status pengaduan
	const statusMap = {
		DITERIMA: "DIPROSES",
		MENUJU_LOKASI: "DIPROSES",
		SELESAI: "SELESAI",
		DIBATALKAN: "DITOLAK",
		DITOLAK: "DITOLAK",
	};

	/* ----- action dialog ----- */
	const open = async (act, data) => {
		statusActive.value = data.active;

		items.value =
			data?.TindakLanjut.map((e) => {
				return { ...e, tanggal_id: main.time.formatDate(e.tanggal, true) };
			}) ?? [];

		await main.open();
	};
	const close = async () => {
		main.close();
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<Dialog
			v-model:visible="modal.show"
			:breakpoints="breakpoints.dialog"
			:style="{ width: '75vw' }"
			modal
		>
			<template #header>
				<h6 class="text-indigo-400 text-sm flex items-center">
					<i class="pi pi-list mr-2"></i> <span>Riwayat Tindak Lanjut</span>
				</h6>
			</template>
			<template #default>
				<DataTable
					:value="items"
					tableStyle="min-width: 100%"
					:rowClass="
						({ status }) =>
							statusMap[status] === statusActive
								? 'bg-gradient-to-r from-indigo-100 to-indigo-200 text-indigo-900 font-medium'
								: ''
					"
					scrollable
					scrollHeight="300px"
					class="text-sm"
				>
					<Column field="status" header="Status"></Column>
					<Column field="Petugas.nama" header="Petugas"></Column>
					<Column field="tanggal_id" header="Tanggal"></Column>
					<Column header="Keterangan">
						<template #body="slotProps">
						  {{ slotProps.data.keterangan || '-' }}
						</template>
					  </Column>
				</DataTable>
			</template>
		</Dialog>
	</main>
</template>
