<script setup>
	import { appLogoLight, appCode, appName } from "@/config/appInfo.js";
</script>

<template>
	<section
		class="relative h-[93vh] bg-no-repeat bg-cover bg-center px-4 text-white flex items-center justify-center"
		style="
			background-image: linear-gradient(
					to right,
					rgba(79, 70, 229, 0.85),
					rgba(99, 102, 241, 0.75)
				),
				url('/assets/background/ake-gaale.png');
		"
	>
		<!-- Overlay -->
		<div
			class="absolute inset-0 bg-gradient-to-r from-indigo-900/40 via-indigo-900/30 to-indigo-900/30 backdrop-blur-sm z-0"
		></div>

		<!-- Content -->
		<div class="relative z-10 text-center max-w-4xl px-6 py-12 animate-fade-in-up">
			<img
				:src="appLogoLight"
				alt="Logo Ake Gaale"
				class="mx-auto mb-6 w-24 md:w-32 drop-shadow-xl"
			/>
			<h1
				class="text-5xl md:text-6xl font-extrabold leading-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-indigo-200 drop-shadow-lg mb-6"
			>
				Daftar Akun Pengaduan
			</h1>
			<p class="text-white/90 text-base md:text-xl font-light max-w-2xl mx-auto mb-8">
				Laporkan masalah air seperti kebocoran atau gangguan distribusi langsung ke
				camat Perumda Ake Gaale dengan mudah dan cepat.
			</p>
			<Button
				as="a"
				label="Daftar sebagai staf"
				href="#registrasi"
				v-smooth-scroll
				rel="noopener"
				class="px-8 py-3 text-white bg-indigo-600 hover:bg-indigo-700 hover:scale-105 ring-1 ring-white/20 rounded-full shadow-lg transition duration-300"
			/>
		</div>
	</section>
</template>
