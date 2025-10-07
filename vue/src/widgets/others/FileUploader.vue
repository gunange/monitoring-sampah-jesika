<script setup>
	const props = defineProps({
		accept: {
			type: [String, Array],
			default: () => ["image/*"],
		},
		maxFileSize: {
			type: Number,
			default: 1000000,
		},
		totalSizePercent: {
			type: Number,
			default: 0,
		},
	});

	const emit = defineEmits(["file-selected"]);

	const onSelect = (event) => {
		const file = event.files?.[event.files.length - 1] || null;
		if (file) {
			emit("file-selected", file);
		}
	};
</script>

<template>
	<div class="card">
		<FileUpload
			name="file"
			:accept="Array.isArray(accept) ? accept.join(',') : accept"
			:maxFileSize="maxFileSize"
			customUpload
			:auto="false"
			:fileLimit="1"
			:multiple="false"
			@select="onSelect"
			:progress="totalSizePercent"
		>
			<template #header="{ chooseCallback, files }">
				<div class="flex flex-wrap justify-between items-center flex-1 gap-4">
					<div class="flex gap-2">
						<Button
							@click="chooseCallback()"
							icon="pi pi-file-plus"
							label="Pilih File"
							outlined
							size="small"
							severity="secondary"
						/>
					</div>
					<ProgressBar
						:value="totalSizePercent"
						:showValue="false"
						class="md:w-20rem w-full md:ml-auto my-2 h-[10px]"
						v-if="files && files.length > 0"
					>
						<span class="whitespace-nowrap">{{ totalSizePercent }} % </span>
					</ProgressBar>
				</div>
			</template>

			<template #content="{ files, removeFileCallback }">
				<div class="flex flex-col gap-4">
					<div v-if="files && files.length > 0">
						<div class="p-4 border border-surface rounded flex gap-4 items-center">
							<div>
								<img
									:src="files[files.length - 1].objectURL"
									:alt="files[files.length - 1].name"
									height="160"
									class="rounded shadow"
								/>
								<div class="flex flex-col flex-grow overflow-hidden gap-1 mt-2">
									<div class="flex justify-between items-center gap-2">
										<div class="truncate">
											<span class="font-medium text-sm">{{
												files[files.length - 1].name
											}}</span>
											<small class="text-muted block"
												>{{
													(files[files.length - 1].size / 1024).toFixed(2)
												}}
												KB</small
											>
										</div>
										<Button
											icon="pi pi-times"
											@click="removeFileCallback(0)"
											label="Hapus"
											outlined
											size="small"
											severity="danger"
											class="shrink-0"
										/>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</template>

			<template #empty>
				<div class="flex items-center justify-center flex-col py-10">
					<i
						class="pi pi-cloud-upload !border-2 !rounded-full !p-8 !text-4xl !text-muted-color"
					/>
					<p class="mt-6 mb-0">Drag and drop a file here to upload.</p>
				</div>
			</template>
		</FileUpload>
	</div>
</template>
