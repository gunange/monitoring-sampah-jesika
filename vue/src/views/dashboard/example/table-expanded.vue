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
						<h6><i class="pi pi-sparkles" /> <span>Example</span></h6>
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
						<template #item-operation="item">
							<div class="" style="position: relative">
								<SpeedDial
									direction="left"
									style="
										position: absolute;
										top: -10px;
										height: 25px;
										right: 48%;
									"
									:model="[
										{
											label: 'Delete',
											icon: 'pi pi-trash',
											severity: 'danger',
											command: () => $refs.ref_cruds.open('del', item.id),
										},
										{
											label: 'View Data',
											icon: 'pi pi-eye',
											severity: 'info',
											command: () =>
												$refs.ref_cruds.open('view-data', item.id),
										},
										{
											label: 'Reset Password',
											icon: 'pi pi-sync',
											severity: 'warn',
											command: () =>
												$refs.ref_cruds.open('reset-password', item.id),
										},
									]"
								>
									<template #button="{ toggleCallback }">
										<Button
											class=""
											@click="toggleCallback"
											icon="pi pi-align-right"
											size="small"
										/>
									</template>
									<template #item="{ item, toggleCallback }">
										<Button
											:icon="item.icon"
											:title="item.label"
											rounded
											:severity="item.severity ?? 'secondary'"
											@click="toggleCallback"
										/>
									</template>
								</SpeedDial>
							</div>
						</template>

						<template #item-status="item">
							<i class="pi pi-check text-green-500" v-if="item.validasi" />
							<i class="pi pi-times text-red-500" v-else />
						</template>

						<template #expand="item">
							<div
								class="p-4 text-sm bg-gray-50 border border-gray-200 rounded-md"
							>
								<p class="mb-1 text-primary font-semibold">Deskripsi Produk:</p>
								<p class="text-gray-700 leading-relaxed">
									{{ item.deskripsi || "Tidak ada deskripsi." }}
								</p>
							</div>
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
	import { dataEnv } from "@/components/dashboard/panitia/config/index.ts";
	import { MainData } from "@/components/dashboard/panitia/cruds/calon-mahasiswa/controller";
	import Cruds from "@/components/dashboard/panitia/cruds/calon-mahasiswa/views/index.vue";

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
						{ text: "No Regis", value: "no_regis" },
						{ text: "Jenjang", value: "jenjang" },
						{ text: "Prodi", value: "data.prodi.label" },
						{ text: "Nama", value: "data.nama" },
						{ text: "No Heandphone", value: "data.no_hp" },
						{ text: "Valid", value: "status" },
						{ text: "Operation", value: "operation" },
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
				return main.items;
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
