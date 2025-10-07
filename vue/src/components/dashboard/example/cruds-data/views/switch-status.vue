<script setup>
import { ref, computed, reactive } from 'vue'

import { breakpoints } from '@/config/vue-prime/appPrimeConfig.ts'
import { Cruds } from '../controller'

const main = new Cruds()

const modal = main.modal
const form = ref({})
const ref_form = ref()
/* ----- computed ----- */

/* ----- action dialog ----- */
const open = async (act, uid) => {
  main.modal.act = act
  main.modal.label = 'Perbahrui Token'

  await main.open(act)

  main.setUid(uid)
  form.value = main.data
}
const close = async () => {
  main.close()
}

/* ----- on submit ----- */
const onSave = async () => {
  if (modal.proses_form) return
  modal.proses_form = true
  await main.switchStatus()
}

defineExpose({ open, close })
</script>

<template>
  <main>
    <Dialog
      v-model:visible="modal.show"
      :breakpoints="breakpoints.dialog"
      :style="{ width: '30vw' }"
      modal
    >
      <template #header>
        <h6 class="text-primary text-sm flex items-center">
          <i class="pi pi-tags mr-2"></i>
          <span>{{ modal.label }}</span>
        </h6>
      </template>

      <template #default>
        <div class="text-center">
          <p>
            Apakah anda akan {{ form.enable ? 'Menonaktifkan' : 'Mengaktifkan' }} priode
            <b>{{ form.label }} </b> ?
          </p>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end">
          <Button
            type="button"
            label="Save"
            size="small"
            icon="pi pi-send"
            @click="onSave"
            :loading="modal.proses_form"
            outlined
          />
        </div>
      </template>
    </Dialog>
  </main>
</template>
