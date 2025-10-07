<script setup>
import { ref, computed, reactive } from 'vue'
import { post } from '@/controller/others/RequestApiController'

import { breakpoints } from '@/config/vue-prime/appPrimeConfig.ts'
import { generateUniqID } from '@/controller/tools/other.ts'

import { AuthController } from '@/controller/controllers/AuthController.ts'

const store = new AuthController().gantiPasswordStore

const form = ref({})
const ref_form = ref()
/* ----- computed ----- */

/* ----- action dialog ----- */
const open = async (act, uid) => {
  store.show = true
  ref_form.value.resetForm()
}

/* ----- on submit ----- */
const onSave = async (e, { resetForm }) => {
  if (store.proses) return
  store.proses = true
  const { data, status } = await post(`user/ganti-password`, e)

  if (status === 201 || status === 200) store.show = false
  store.proses = false
}

/* ----- method ----- */

const generatePassword = () => {
  form.value.password = generateUniqID(5)
}

defineExpose({ open })
</script>

<template>
  <main>
    <Dialog
      v-model:visible="store.show"
      :breakpoints="breakpoints.dialog"
      :style="{ width: '30vw' }"
      modal
    >
      <template #header>
        <h6 class="text-primary text-sm flex items-center">
          <i class="pi pi-tags mr-2"></i>
          <span>Ganti Password</span>
        </h6>
      </template>

      <VeeForm @submit="onSave" :initial-values="form" ref="ref_form">
        <div class="text-xs grid grid-cols-1 gap-4">
          <div class="form">
            <VeeField v-slot="{ field }" name="password" rules="required" v-model="form.password">
              <div class="flex justify-between">
                <label>
                  <span>Password</span>
                  <span class="text-red-500"> * <VeeErrorMessage name="password" /> </span>
                </label>
                <Button
                  label="Generate password"
                  size="small"
                  icon="pi pi-key"
                  @click="generatePassword"
                  outlined
                />
              </div>

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
            :loading="store.proses"
            outlined
          />
        </div>
      </template>
    </Dialog>
  </main>
</template>
