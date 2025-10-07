<template>
  <div>
    <modal-card :modal="md" ref="ref_modal">
      <template #body>
        <div class="card">
          <div class="card-header border-bottom color-no-implement text-danger allow-dark">
            <span><i class="bi bi-image"></i> Pick Image</span>
          </div>
          <div class="card-body card-scroll">
            <div class="d-flex flex-column align-items-center" v-if="rx.load">
              <img src="@/assets/image/other/bola.gif" style="width: 350px; height: auto" />
            </div>
            <div v-else>
              <VuePictureCropper
                :boxStyle="{
                  width: '100%',
                  height: '100%',
                  backgroundColor: '#f8f8f8',
                  margin: 'auto',
                }"
                :img="pic"
                :options="options"
                :presetMode="presetMode"
              />
            </div>
          </div>
          <div class="card-footer d-flex justify-content-end border-top text-bg-light">
            <div class="btn-group">
              <button
                class="btn btn-sm btn-outline-secondary"
                type="button"
                data-bs-dismiss="modal"
              >
                Cencel
              </button>
              <button class="btn btn-sm btn-primary" type="button" @click="getResult">
                Pick Image
              </button>
            </div>
          </div>
        </div>
      </template>
    </modal-card>
    <input
      ref="refUploadInput"
      type="file"
      accept="image/jpg, image/jpeg, image/png, image/gif"
      @change="selectFile"
      v-show="false"
    />
  </div>
</template>

<script setup>
import VuePictureCropper, { cropper } from 'vue-picture-cropper'
import ModalCard from '@/widgets/modal/ModalWidget.vue'
import { onMounted, ref, computed, reactive } from 'vue'

const ref_modal = ref()
const refUploadInput = ref()

const emit = defineEmits(['onPick'])

const pic = ref()
const nameFile = ref('name-file')
const result = reactive({
  dataURL: '',
  blobURL: '',
  file: null,
})

const rx = ref({
  load: true,
})

const openModal = () => {
  rx.value.load = true
  ref_modal.value.open()
}
const closeModal = () => {
  rx.value.load = true
  ref_modal.value.close()
}

const selectFile = (e) => {
  rx.value.load = true
  pic.value = ''
  result.dataURL = ''
  result.blobURL = ''
  result.file = null

  // Get selected files
  const { files } = e.target
  if (!files || !files.length) return

  // Convert to dataURL and pass to the cropper component
  const file = files[0]
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
    // Update the picture source of the `img` prop
    pic.value = String(reader.result)

    // Show Modal
    openModal()

    // Finish Load
    setTimeout(() => {
      rx.value.load = false
    }, 700)

    // Clear selected files of input element
    if (!refUploadInput.value) return
    refUploadInput.value.value = ''
  }
}

const getResult = async () => {
  if (!cropper) return

  const base64 = cropper.getDataURL()
  const blob = await cropper.getBlob()

  if (!blob) return

  const file = await cropper.getFile({
    fileName: 'Nama Avatar',
  })

  result.dataURL = base64
  result.file = file
  result.blobURL = URL.createObjectURL(blob)

  emit('onPick', result)
  closeModal()
}

const atPick = () => {
  refUploadInput.value.click()
}

defineExpose({ openModal, closeModal, atPick, nameFile })
defineProps({
  md: {
    id: 'modal-pick',
    class: 'modal-lg',
  },
  options: {
    viewMode: 1,
    dragMode: 'move',
    aspectRatio: 1,
    cropBoxResizable: false,
  },
  presetMode: {
    mode: 'fixedSize',
    width: 250,
    height: 250,
  },
})
</script>
