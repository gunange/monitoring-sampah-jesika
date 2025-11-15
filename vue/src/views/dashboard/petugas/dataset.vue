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
						<h6><i class="pi pi-sparkles" /> <span>Dataset Setting</span></h6>
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

						<Button
							icon="pi pi-plus"
							class="ml-2"
							size="small"
							v-tooltip.top="'Tambah Data'"
							outlined
							@click="$refs.ref_cruds.open('add')"
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
											label: 'Image Preview',
											icon: 'pi pi-image',
											severity: 'info',
											command: () =>
												$refs.ref_cruds.open('show', item),
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

						<template #loading>
							<img src="/assets/gif/bola.gif" style="width: 100px; height: 80px" />
						</template>

						<template #expand="item">
							<div class="p-4 text-sm bg-gray-50 border border-gray-200 rounded-md">
								<p class="mb-2 text-primary font-semibold">Detail Fitur:</p>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div>
										<p><span class="font-medium">Laplacian Var:</span> {{ item.laplacian_var }}</p>
										<p><span class="font-medium">Edge Ratio:</span> {{ item.edge_ratio }}</p>
										<p><span class="font-medium">Shape Area Ratio:</span> {{ item.shape_area_ratio }}</p>
									</div>
									<div>
										<p class="font-medium mb-1">Frame (JSON):</p>
										<pre class="p-2 bg-white border rounded text-xs overflow-auto max-h-40">{{ formatJSON(item.frame) }}</pre>
										<p class="font-medium mt-3 mb-1">ROI (JSON):</p>
										<pre class="p-2 bg-white border rounded text-xs overflow-auto max-h-40">{{ formatJSON(item.roi) }}</pre>
									</div>
								</div>
							</div>
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
	import { dataEnv } from "@/components/dashboard/petugas/config/index.ts";
	import { MainData } from "@/components/dashboard/petugas/cruds/dataset/controller";
	import Cruds from "@/components/dashboard/petugas/cruds/dataset/views/index.vue";

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
						{ text: "Label", value: "label" },
						{ text: "h_mean", value: "h_mean" },
						{ text: "h_std", value: "h_std" },
						{ text: "s_mean", value: "s_mean" },
						{ text: "s_std", value: "s_std" },
						{ text: "v_mean", value: "v_mean" },
						{ text: "v_std", value: "v_std" },
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
			formatJSON(value) {
				try {
					return typeof value === "string"
						? JSON.stringify(JSON.parse(value), null, 2)
						: JSON.stringify(value, null, 2);
				} catch (e) {
					return value ?? "-";
				}
			},
		},
		async mounted() {
			await main.init();
		},
	};
</script>
