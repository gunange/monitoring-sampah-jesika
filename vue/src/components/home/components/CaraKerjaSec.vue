<template>
	<div class="md:px-25 py-12 bg-gray-50">
		<div class="text-center mb-10">
			<h2 class="text-3xl font-bold text-yellow-500">Cara Kerja</h2>
			<p class="text-gray-600 mt-2 text-sm md:text-base">
				Berikut adalah langkah-langkah dalam melakukan stafan beras Bulog secara
				daring.
			</p>
		</div>
		<Timeline
			:value="events"
			align="alternate"
			class="customized-timeline max-w-4xl mx-auto"
		>
			<template #marker="slotProps">
				<span
					class="flex w-10 h-10 items-center justify-center text-white rounded-full z-10 shadow-md"
					:style="{ backgroundColor: slotProps.item.color }"
				>
					<i :class="slotProps.item.icon"></i>
				</span>
			</template>
			<template #content="slotProps">
				<Card class="mt-4 shadow-md border border-gray-100">
					<template #title>
						<span class="font-semibold text-lg text-gray-800">{{
							slotProps.item.status
						}}</span>
					</template>
					<template #content>
						<p class="text-sm text-gray-600">
							{{ slotProps.item.description }}
						</p>
					</template>
				</Card>
			</template>
		</Timeline>
	</div>
</template>

<script setup>
	import { ref } from "vue";

	const events = ref([
		{
			status: "Registrasi Akun",
			icon: "pi pi-user-plus",
			color: "#007bff",
			description: "Pelanggan membuat akun untuk melaporkan pengaduan.",
		},
		{
			status: "Login ke Sistem",
			icon: "pi pi-sign-in",
			color: "#6c757d",
			description:
				"Pelanggan masuk ke dalam sistem menggunakan akun yang telah dibuat.",
		},
		{
			status: "Buat Pengaduan",
			icon: "pi pi-pencil",
			color: "#28a745",
			description:
				"Pelanggan mengisi form pengaduan dengan memilih jenis pengaduan, lokasi kejadian, dan deskripsi masalah.",
		},
		{
			status: "Verifikasi Pengaduan",
			icon: "pi pi-search",
			color: "#17a2b8",
			description:
				"Petugas menerima dan memverifikasi data pengaduan yang dikirim staf.",
		},
		{
			status: "Tindak Lanjut",
			icon: "pi pi-send",
			color: "#ffc107",
			description:
				"Petugas menuju lokasi kejadian untuk menangani masalah yang dilaporkan.",
		},
		{
			status: "Pengaduan Selesai",
			icon: "pi pi-check-circle",
			color: "#198754",
			description:
				"Petugas menyelesaikan masalah dan menandai pengaduan sebagai selesai.",
		},
	]);
</script>

<style lang="scss" scoped>
	@media screen and (max-width: 960px) {
		::v-deep(.customized-timeline) {
			.p-timeline-event:nth-child(even) {
				flex-direction: row;

				.p-timeline-event-content {
					text-align: left;
				}
			}

			.p-timeline-event-opposite {
				flex: 0;
			}
		}
	}
</style>
