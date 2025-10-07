<script setup>
import { ref } from 'vue'

import AddAndUp from './add-up.vue'
import DelData from './del.vue'
import SwitchStatus from './switch-status.vue'

const ref_add_and_up = ref()
const ref_del = ref()
const switch_status = ref()

const open = async (act = '', data = null) => {
  if (act == 'add' || act == 'up') {
    ref_add_and_up.value.open(act, data)
  } else if (act == 'del') {
    ref_del.value.open(act, data)
  } else if (act == 'switch-status') {
    switch_status.value.open(act, data)
  }
}

defineExpose({ open, close })
</script>

<template>
  <main>
    <AddAndUp ref="ref_add_and_up" />
    <DelData ref="ref_del" />
    <SwitchStatus ref="switch_status" />
  </main>
</template>
