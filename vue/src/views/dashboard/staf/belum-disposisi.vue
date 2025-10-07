<template>
	<div>
		<div class="px-5 mt-5">
			<BradcumpWidget
				:home="{
					icon: 'pi pi-home',
					route: `/${pathRoute}`,
				}"
				:items="[{ label: 'Library', route: `/${pathRoute}` }]"
			/>
		</div>
		<div class="px-5 mt-5">
			<div class="card">
				<div class="card-header flex justify-between">
					<div class="flex-none flex items-center">
						<h6><i class="pi pi-sparkles" /> <span>Belum Didisposisi</span></h6>
					</div>

					<div class="flex items-center justify-end">
						<Button
							icon="pi pi-refresh"
							class="ml-2"
							size="small"
							v-tooltip.top="'Refresh'"
							outlined
							@click="reset"
						/>

					</div>
				</div>
				<div class="card-body">
					<div class="search-easy-table mb-5">
						<InputGroup class="">
							<InputGroupAddon>
								<i class="pi pi-search text-primary"></i>
							</InputGroupAddon>
							<InputText placeholder="Search.." v-model="table.search" />
						</InputGroup>
					</div>
					<EasyDataTable
						:items="items"
						:loading="loadItems"
						:headers="table.th"
						:search-value="table.search"
						:sort-by="table.sort"
						:sort-type="table.sortType"
						:rowsItems="table.rowsItems"
						:rowsPerPage="table.rowsPerPage"
						rows-per-page-message="Jumlah data per-halaman"
						rows-of-page-separator-message="dari"
						theme-color="rgb(var(--primary))"
						table-class-name="customize-table"
						empty-message="Data tidak ditemukan"
						show-index
					>
						<template #header-operation>
							<div class="text-center">
								<i class="pi pi-spin pi-cog"></i>
							</div>
						</template>
						

						<template #item-lampiran="item">
							<Button
								label="Lihat"
								icon="pi pi-eye"
								size="small"
								class="p-button-sm p-button-outlined"
								@click="$refs.ref_cruds.open('show', item)"
							/>
						</template>

						<template #loading>
							<img src="/assets/gif/bola.gif" style="width: 100px; height: 80px" />
						</template>
					</EasyDataTable>
				</div>
			</div>
		</div>
		<Cruds ref="ref_cruds" />
	</div>
</template>

<script>
	import { ref } from "vue";

	import BradcumpWidget from "@/widgets/others/bardcump-widget.vue";

	// config path
	import { dataEnv } from "@/components/dashboard/staf/config/index.ts";
	import { MainData } from "@/components/dashboard/staf/cruds/surat-masuk/controller";
	import Cruds from "@/components/dashboard/staf/cruds/surat-masuk/views/index.vue";

	const main = new MainData();

	export default {
		components: {
			BradcumpWidget,
			Cruds,
		},
		data() {
			return {
				table: ref({
					search: ref(""),
					th: [
						{ text: "Nomor", value: "nomor" },
						{ text: "Pengirim", value: "pengirim" },
						{ text: "Perihal", value: "perihal" },
						{ text: "Tanggal Surat", value: "tanggal_id" },
						{ text: "Lampiran", value: "lampiran" },
						{ text: "Staf", value: "Staf.nama" },
						
					],
					isUpdate: false,
					itemsSelected: [],
					sort: ["tanggal", "waktu"],
					sortType: ["desc", "desc"],
					rowsItems: [15, 25, 50],
					rowsPerPage: 15,
				}),
			};
		},

		computed: {
			pathRoute() {
				return dataEnv.path_route;
			},
			items() {
				return main.items.filter((e)=> e.Disposisi === null);
			},
			loadItems() {
				return main.data.load;
			},
		},
		methods: {
			reset() {
				return main.reset();
			},
		},
		async mounted() {
			await main.init();
		},
	};
</script>
