<script setup>
	import { ref } from "vue";

	import AddAndUp from "./add-up.vue";
	import DelData from "./del.vue";
	import FileShow from "./file-show.vue";
	import FileUpload from "./upload.vue";


	const ref_add_and_up = ref();
	const ref_del = ref();
	const ref_file_show = ref();
	const ref_file_upload = ref();

	

	const open = async (act = "", data = null) => {
		if (act == "add" || act == "up") {
			ref_add_and_up.value.open(act, data);
		} 
		else if (act == "show") {
			ref_file_show.value.open(act, data);
		}
		else if (act == "upload") {
			ref_file_upload.value.open(act, data);
		}
		else if (act == "del") {
			ref_del.value.open(act, data);
		}
	};

	defineExpose({ open, close });
</script>

<template>
	<main>
		<AddAndUp ref="ref_add_and_up" />
		<DelData ref="ref_del" />
		<FileShow ref="ref_file_show" />
		<FileUpload ref="ref_file_upload" />
	</main>
</template>
