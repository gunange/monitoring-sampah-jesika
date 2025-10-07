<script setup>
import { ref } from 'vue'
import { Controller } from '../controller.ts'
import ErrorModal from './../error.vue'

const main = new Controller()

const form = ref({})

const ref_modal_err = ref()
const ref_form = ref()

const onSave = async (e) => {
  await main.onSubmit(e)

  if (!main.post.sukses) {
    ref_modal_err.value.open(main.post.message, main.post.errors)
  }
}
</script>
<template>
  <div class="basis-2/3">
    <VeeForm ref="ref_form" :initial-values="form" @submit="onSave" class="max-sm:h-[100%]">
      <div class="form text-xs pt-10 grid grid-cols-1 gap-4 max-sm:h-[100%] max-sm:flex flex-col">
        <div class="max-sm:basis-1/3">
          <VeeField v-slot="{ field }" name="username" rules="required" v-model="form.username">
            <label
              >Account
              <span class="text-red-500">* <VeeErrorMessage name="username" /> </span>
            </label>

            <InputText
              v-bind="field"
              placeholder="Masukan Username"
              class="text-xs"
              autocomplete="off"
            />
          </VeeField>
        </div>
        <div class="max-sm:basis-1/3">
          <VeeField v-slot="{ field }" name="password" rules="required" v-model="form.password">
            <label
              >Password
              <span class="text-red-500">* <VeeErrorMessage name="password" /> </span>
            </label>

            <InputText
              v-bind="field"
              placeholder="Masukan Password"
              class="text-xs"
              autocomplete="off"
            />
          </VeeField>
        </div>

        <div class="mt-5 max-sm:basis-2/3 grid-cols-1 max-sm:grid place-items-end gap-4">
          <Button
            type="submit"
            label="Sign In"
            icon="pi pi-key"
            class="text-[.8rem] w-full"
            :loading="main.post.load"
          />
        </div>
      </div>
    </VeeForm>

    <ErrorModal ref="ref_modal_err" />
  </div>
</template>
