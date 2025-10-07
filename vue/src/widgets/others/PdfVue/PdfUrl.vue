<script setup>
import { ref } from 'vue'
import { VuePDF, usePDF } from '@tato30/vue-pdf'
import '@tato30/vue-pdf/style.css'

const props = defineProps({
  url: {
    type: String,
    required: true,
  },
  enableXfa: {
    type: Boolean,
    default: false,
  },
})

const { pdf, pages } = usePDF({
  url: props.url,
  enableXfa: props.enableXfa,
})

const fitParent = ref(true)

const width = ref(650)

// Fungsi untuk kontrol

const perbesar = () => {
  fitParent.value = false
  width.value += 100
}
const perkecil = () => {
  fitParent.value = false
  width.value = Math.max(200, width.value - 100)
}
function onLoaded(value) {
  emit('loaded', value)
}

const downloadPDF = async (fileName = 'Document') => {
  try {
    const response = await fetch(props.url)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = fileName + '.pdf'
    a.click()

    URL.revokeObjectURL(url)
  } catch (_) {}
}

const emit = defineEmits(['loaded'])

defineExpose({ perbesar, perkecil, downloadPDF })
</script>
<template>
  <div style="height: 80vh; overflow-y: auto">
    <div v-for="page in pages" :key="page" class="mb-4">
      <VuePDF
        :pdf="pdf"
        :page="page"
        :width="width"
        :fit-parent="fitParent"
        @loaded="onLoaded"
        class="w-full"
      />
    </div>
  </div>
</template>
