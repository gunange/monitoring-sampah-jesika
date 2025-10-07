<template>
	<section class="px-4 py-12 bg-gray-50">
		<h2
			class="text-4xl md:text-5xl font-extrabold text-center mb-10 text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-indigo-500 to-blue-600"
		>
			Riwayat Pengaduan
		</h2>
		<div class="max-w-5xl mx-auto">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6" v-if="items.length">
				<div
					v-for="(item, i) in items"
					:key="i"
					class="bg-white p-5 rounded-xl shadow-sm hover:shadow-md transition duration-300 border border-gray-100"
				>
					<div class="flex justify-between items-center mb-2">
						<h3 class="text-lg font-semibold text-gray-800">
							{{ item.JenisPengaduan.nama }}
						</h3>
						<Tag value="Selesai" severity="success" />
					</div>
					<p class="text-gray-600 text-sm line-clamp-3">
						<span>{{ item.keterangan || "Tidak ada keterangan." }}</span
						><br />
						<span class="text-xs italic">{{
							item.JenisPengaduan.deskripsi || ""
						}}</span>
					</p>
					<Divider />
					<div class="text-xs text-gray-500 flex justify-between mb-3">
						<span class="flex items-center gap-1">
							<i class="pi pi-calendar"></i> {{ item.tanggal }}
						</span>
						<span>Pelanggan: {{ item?.Pelanggan?.nama || "Tidak diketahui" }}</span>
					</div>
					<div class="flex gap-2">
						<Button
							label="Riwayat Tindak Lanjut"
							icon="pi pi-list"
							severity="secondary"
							outlined
							size="small"
							class="!border-indigo-300 !bg-indigo-50 hover:!bg-indigo-100 text-indigo-800 font-medium"
							@click="
								$refs.ref_cruds.open('tindak-lanjut', {
									active: item.status,
									...item,
								})
							"
						/>
						<Button
							label="Lihat Lampiran"
							icon="pi pi-paperclip"
							severity="secondary"
							outlined
							size="small"
							class="!border-blue-300 !bg-blue-50 hover:!bg-blue-100 text-blue-800 font-medium"
							@click="$refs.ref_cruds.open('show', item)"
						/>
					</div>
				</div>
			</div>

			<div v-else class="text-center text-gray-400 mt-12">
				<i class="pi pi-info-circle text-xl mb-2 block" />
				<p>Belum ada pengaduan yang selesai.</p>
			</div>
		</div>
		<Cruds ref="ref_cruds" />
	</section>
</template>

<script>
	import Cruds from "./ListPengaduanSec/index.vue";
	import { Cruds as CrudsController } from "./ListPengaduanSec/controller.ts";
	import { atribut } from "@/services/atribut";

	const main = new CrudsController();

	export default {
		components: {
			Cruds,
		},
		computed: {
			items() {
				return atribut.pengaduan.items
					.filter((e) => e.status === "SELESAI")
					.map((e) => ({
						...e,
						tanggal: main.time.formatDate(e.created_at, true),
					}));
			},
		},
		mounted() {
			atribut.pengaduan.init();
		},
	};
</script>
