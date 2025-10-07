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
  main.modal.label = 'act' == 'up' ? 'Update' : 'Tambah'
  form.value = {}

  await main.open(act)
  ref_form.value.resetForm()

  if (act == 'up') {
    main.setUid(uid)
    ref_form.value.setValues(main.data)
  }
}
const close = async () => {
  main.close()
}

/* ----- on submit ----- */
const onSave = async (e, { resetForm }) => {
  if (modal.proses_form) return
  modal.proses_form = true

  if (modal.act == 'add') {
    await main.add(e)
  } else if (modal.act == 'up') {
    await main.up(e)
  }
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

      <VeeForm @submit="onSave" :initial-values="form" ref="ref_form">
        <div class="text-xs grid grid-cols-1 gap-4">
          <div class="form">
            <VeeField v-slot="{ field }" name="label" rules="required" v-model="form.label">
              <label>
                <span>Label</span>
                <span class="text-red-500"> * <VeeErrorMessage name="label" /> </span>
              </label>

              <InputText
                v-bind="field"
                placeholder="Masukan Input Sesuai Field.."
                class="text-xs"
                autocomplete="off"
              />
            </VeeField>
          </div>

          <div class="form">
            <VeeField v-slot="{ field }" name="priode" rules="required" v-model="form.priode">
              <label>
                <span>Priode</span>
                <span class="text-red-500"> * <VeeErrorMessage name="priode" /> </span>
              </label>

              <InputText
                v-bind="field"
                placeholder="Masukan Input 2024.1 jika ganjil. dan masukan 2024.2 jika genap"
                class="text-xs"
                autocomplete="off"
              />
            </VeeField>
          </div>

          <div class="form">
            <VeeField v-slot="{ field }" name="tahun" rules="required" v-model="form.tahun">
              <label>
                <span>Tahun</span>
                <span class="text-red-500"> * <VeeErrorMessage name="tahun" /> </span>
              </label>

              <InputText
                v-bind="field"
                placeholder="Masukan Input Sesuai Field.."
                class="text-xs"
                autocomplete="off"
              />
            </VeeField>
          </div>
        </div>

        <button type="submit" class="hidden" ref="refBtnAddAndUp">submit</button>
      </VeeForm>
      <template #footer>
        <div class="flex justify-end">
          <Button
            type="button"
            label="Save"
            size="small"
            icon="pi pi-send"
            @click="$refs.refBtnAddAndUp.click()"
            :loading="modal.proses_form"
            outlined
          />
        </div>
      </template>
    </Dialog>
  </main>
</template>
