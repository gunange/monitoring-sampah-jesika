<template>
	<section
		class="bg-gradient-to-b from-indigo-50 to-white py-16 px-6 md:px-25 min-h-screen"
		id="registrasi"
	>
		<h2 class="text-3xl font-bold text-center text-yellow-500 mb-4">
			Registrasi Akun staf
		</h2>
		<div class="w-20 h-1.5 bg-indigo-600 mx-auto mb-6 rounded-full"></div>
		<p class="text-center text-gray-600 mb-10 max-w-2xl mx-auto">
			Lengkapi data diri Anda untuk dapat melaporkan pengaduan staf secara daring
			melalui sistem Ake Gaale.
		</p>
		<div class="flex flex-col md:flex-row items-center justify-center">
			<!-- Kiri -->
			<div class="w-full md:w-1/2 mb-10 md:mb-0 text-center md:text-left px-4">
				<h2 class="text-3xl md:text-4xl font-bold text-indigo-700 mb-4">
					Mulai Laporkan Pengaduan Anda Sekarang
				</h2>
				<p class="text-gray-600 text-base md:text-lg mb-6">
					Daftarkan diri Anda untuk menyampaikan pengaduan seperti kebocoran, air
					mati, atau kerusakan meteran secara langsung kepada camat Perumda Ake
					Gaale.
				</p>
				<img
					src="/assets/ilustration/registrasi-1.png"
					alt="Ilustrasi Registrasi"
					class="mx-auto md:mx-0 w-full max-w-sm"
				/>
			</div>
			<!-- Kanan -->
			<div
				class="w-full md:w-1/2 p-8 bg-white rounded-xl shadow-md border border-gray-200"
			>
				<FormComp />
			</div>
		</div>
	</section>
</template>

<script>
	import FormComp from "./RegisSec/FormComp.vue";

	export default {
		components: {
			FormComp,
		},
	};
</script>
