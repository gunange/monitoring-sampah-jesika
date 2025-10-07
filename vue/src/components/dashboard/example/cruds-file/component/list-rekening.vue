<template>
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 p-3">
		<div
			v-for="item in items"
			:key="item.id"
			:class="[
				'border border-blue-300 rounded-md p-3 shadow-sm hover:shadow transition-all text-xs space-y-1 relative overflow-hidden',
				'bg-blue-50',
			]"
		>
			<div class="absolute inset-0 opacity-10 pointer-events-none" aria-hidden="true">
				<svg class="w-full h-full text-cyan-400" width="100%" height="100%">
					<defs>
						<pattern
							id="bubble-pattern"
							width="60"
							height="60"
							patternUnits="userSpaceOnUse"
						>
							<circle
								cx="20"
								cy="20"
								r="6"
								fill="currentColor"
								stroke="currentColor"
							/>
							<circle
								cx="50"
								cy="10"
								r="2"
								fill="currentColor"
								stroke="currentColor"
							/>
							<circle
								cx="10"
								cy="50"
								r="3"
								fill="currentColor"
								stroke="currentColor"
							/>
							<circle
								cx="30"
								cy="40"
								r="4"
								fill="currentColor"
								stroke="currentColor"
							/>
						</pattern>
					</defs>
					<rect width="100%" height="100%" fill="url(#bubble-pattern)" />
				</svg>
			</div>
			<p class="text-[13px] font-bold text-indigo-700 uppercase tracking-wide">
				{{ item.nama_bank }}
			</p>
			<h3 class="font-semibold text-gray-700 truncate">{{ item.nama_pemilik }}</h3>
			<p class="text-gray-600">
				<span class="text-[11px] font-medium">No. Rekening:</span>
				<span class="text-[11px] ml-1">{{ item.no_rekening }}</span>
			</p>
		</div>
	</div>
</template>

<script>
	import { atribut } from "@/services/atribut";
	export default {
		computed: {
			items() {
				return atribut.rekening.items;
			},
		},
		mounted() {
			atribut.rekening.init();
		},
	};
</script>
