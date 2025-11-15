<template>
	<div
		class="card relative p-3 py-5 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-200"
	>
		<div class="">
			<div v-if="item" class="space-y-4 text-sm">
				<!-- Header -->
				<div class="flex items-start justify-between">
					<div>
						<h3 class="font-medium text-base text-slate-900 dark:text-slate-100">
							{{ item.name }}
						</h3>
						<div
							class="mt-1 flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400"
						>
							<!-- Indicasi WS Live (placeholder) -->
							<span class="inline-flex items-center gap-1">
								<span
									class="inline-block w-2 h-2 rounded-full"
									:class="wsLive ? 'bg-emerald-500' : 'bg-gray-400'"
								></span>
								<span>Live</span>
							</span>
							<!-- Timestamp update -->
							<span>Terakhir diperbarui {{ lastUpdated }}</span>
						</div>
					</div>
					<div class="flex items-center gap-2" aria-live="polite">
						<!-- Status chip -->
						<span
							class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 transition-colors duration-200"
						>
							<span
								class="inline-block w-2 h-2 rounded-full"
								:class="item.running ? 'bg-emerald-500' : 'bg-rose-500'"
							></span>
							<span>{{ item.running ? "Running" : "Stopped" }}</span>
						</span>
						<Button
							outlined
							size="small"
							:icon="item.running ? 'pi pi-stop' : 'pi pi-play'"
							:label="item.running ? 'Stop' : 'Start'"
							:severity="item.running ? 'danger' : 'primary'"
							:loading="isLoading"
							@click="toggleMachine"
							class="transition-opacity duration-200"
						/>
						
					</div>
				</div>

				<!-- Divider halus -->
				<div class="border-t border-slate-200 dark:border-slate-700"></div>

				<!-- Section: Ringkasan Sistem -->
				<div class="space-y-2">
					<p class="text-xs font-medium text-slate-700 dark:text-slate-300">
						Ringkasan Sistem
					</p>
					<div class="grid grid-cols-2 gap-4">
						<div
							class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
						>
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2">
									<i class="pi pi-video text-slate-500"></i>
									<span>Camera</span>
								</div>
								<span
									class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
								>
									<i class="pi pi-video text-xs"></i>
									<span>{{ item.detail?.camera ? "ON" : "OFF" }}</span>
								</span>
							</div>
							<div class="mt-3 flex items-center justify-between">
								<div class="flex items-center gap-2">
									<i class="pi pi-cog text-slate-500"></i>
									<span>Klasifikasi (KNN)</span>
								</div>
								<span
									class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
								>
									<i class="pi pi-cog text-xs"></i>
									<span>{{ item.detail?.knn ? "ON" : "OFF" }}</span>
								</span>
							</div>
						<div class="mt-3 flex items-center justify-between">
							<div class="flex items-center gap-2">
								<i class="pi pi-database text-slate-500"></i>
								<span>Dataset</span>
							</div>
							<span class="text-slate-700 dark:text-slate-300">{{
								item.detail?.dataset
							}}</span>
						</div>
						<div class="mt-3 flex items-center justify-between">
							<div class="flex items-center gap-2">
								<i class="pi pi-cog text-slate-500"></i>
								<span>KNN K-Value</span>
							</div>
							<span class="text-slate-700 dark:text-slate-300">{{
								item.detail?.['knn-k-value']
							}}</span>
						</div>
						<div class="mt-3 flex items-center justify-between">
							<div class="flex items-center gap-2">
								<i class="pi pi-clock text-slate-500"></i>
								<span>Interval Mesin</span>
							</div>
							<span class="text-slate-700 dark:text-slate-300">{{
								item.detail?.['machine-interval']
							}} s</span>
						</div>
						</div>

						<div
							class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
						>
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2">
									<i class="pi pi-cog text-slate-500"></i>
									<span>Backend</span>
								</div>
								<span class="text-slate-700 dark:text-slate-300">{{
									item.detail?.["camera-list"]?.backend
								}}</span>
							</div>
							<div class="mt-3 flex items-center justify-between">
								<div class="flex items-center gap-2">
									<i class="pi pi-video text-slate-500"></i>
									<span>Total Kamera</span>
								</div>
								<span class="text-slate-700 dark:text-slate-300">{{
									item.detail?.["camera-list"]?.count
								}}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Divider halus -->
				<div class="border-t border-slate-200 dark:border-slate-700"></div>

				<!-- Section: Daftar Kamera -->
				<div class="space-y-2">
					<p class="text-xs font-medium text-slate-700 dark:text-slate-300">
						Daftar Kamera
					</p>
					<div
						class="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-2 max-h-56 overflow-y-auto"
					>
						<ul class="mt-1 space-y-2">
							<li
								v-for="cam in item.detail?.['camera-list']?.cameras"
								:key="cam.index"
								class="p-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 transition hover:shadow-sm duration-200"
							>
								<div class="grid grid-cols-2 gap-3 items-center">
									<!-- Kiri: index + status -->
									<div class="flex items-center gap-3">
										<span
											class="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
											>#{{ cam.index }}</span
										>
										<span class="inline-flex items-center gap-2">
											<span
												class="inline-block w-2 h-2 rounded-full"
												:class="
													cam.available ? 'bg-emerald-500' : 'bg-rose-500'
												"
											></span>
											<span class="text-slate-700 dark:text-slate-300">{{
												cam.available ? "Available" : "Unavailable"
											}}</span>
										</span>
									</div>
									<!-- Kanan: backend + error (truncate + tooltip) -->
									<div class="flex items-center gap-3">
										<span class="text-slate-700 dark:text-slate-300"
											>Backend: {{ cam.backend }}</span
										>
										<span
											class="text-slate-500 dark:text-slate-400 truncate max-w-[12rem]"
											:title="cam.last_error ?? '-'"
										>
											Error: {{ cam.last_error ?? "-" }}
										</span>
									</div>
								</div>
							</li>
						</ul>

						<div
							v-if="!item.detail?.['camera-list']?.cameras?.length"
							class="py-6 text-center text-xs text-slate-500"
						>
							<i class="pi pi-image mr-1"></i>
							<span>Daftar kamera kosong. Periksa backend atau izin kamera.</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Skeleton saat loading -->
			<div v-else class="space-y-4">
				<div class="animate-pulse space-y-2">
					<div class="h-4 w-1/3 bg-slate-200 rounded"></div>
					<div class="h-3 w-1/5 bg-slate-200 rounded"></div>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div class="p-3 rounded-xl border border-slate-200">
						<div class="h-3 w-1/2 bg-slate-200 rounded mb-2"></div>
						<div class="h-3 w-full bg-slate-200 rounded mb-2"></div>
						<div class="h-3 w-2/3 bg-slate-200 rounded"></div>
					</div>
					<div class="p-3 rounded-xl border border-slate-200">
						<div class="h-3 w-1/2 bg-slate-200 rounded mb-2"></div>
						<div class="h-3 w-2/3 bg-slate-200 rounded"></div>
					</div>
				</div>
				<div class="h-32 rounded-xl border border-slate-200"></div>
			</div>
		</div>

	</div>
</template>

<script>
	import { MainData } from "@/components/dashboard/petugas/cruds/ml-config/controller.ts";

	const main = new MainData();

	export default {
		name: "MlComp",
		data() {
			return {
				isLoading: false,
				wsLive: false, // indikator WS sederhana; bisa dihubungkan ke store jika ada
				lastUpdated: "–",
			};
		},
		computed: {
			item() {
				return main.item;
			},
			run() {
				return main.data.run;
			},
		},
		watch: {
			item: {
				immediate: true,
				handler(val) {
					if (val) {
						const now = new Date();
						const hh = String(now.getHours()).padStart(2, "0");
						const mm = String(now.getMinutes()).padStart(2, "0");
						const ss = String(now.getSeconds()).padStart(2, "0");
						this.lastUpdated = `${hh}:${mm}:${ss}`;
					}
				},
			},
		},
		methods: {
			async toggleMachine() {
				try {
					this.isLoading = true;
					await main.toggleMachine();
				} catch (e) {
				} finally {
					this.isLoading = false;
				}
			},
			async loadMachine() {
				try {
					this.isLoading = true;
					await main.getStatus();
				} catch (e) {
				} finally {
					this.isLoading = false;
				}
			},
		},
	};
</script>
