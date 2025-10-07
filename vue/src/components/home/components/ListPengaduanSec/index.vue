<script setup>
	import { ref } from "vue";

	import FileShow from "./file-show.vue";
	import TindakLanjut from "./tindak-lanjut.vue";

	const ref_file_show = ref();
	const ref_tindak_lanjut = ref();

	const open = async (act = "", data = null) => {
		if (act == "show") {
			ref_file_show.value.open(act, data);
		} else if (act == "tindak-lanjut") {
			ref_tindak_lanjut.value.open(act, data);
		}
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<FileShow ref="ref_file_show" />
		<TindakLanjut ref="ref_tindak_lanjut" />
	</main>
</template>
