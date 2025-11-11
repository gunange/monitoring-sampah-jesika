<script setup>
	import { ref } from "vue";

	import Add from "./add.vue";
	import DelData from "./del.vue";
	import FileShow from "./file-show.vue";

	const ref_add = ref();
	const ref_del = ref();
  const ref_file_show = ref();

	const open = async (act = "", data = null) => {
		if (act == "add") {
			ref_add.value.open(act, data);
		} else if (act == "del") {
			ref_del.value.open(act, data);
		} else if (act == "show") {
			ref_file_show.value.open(act, data);
		}
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<Add ref="ref_add" />
		<DelData ref="ref_del" />
    <FileShow ref="ref_file_show" />
	</main>
</template>
