<template>
  <div class="card">
    <div class="card-body grid grid-cols-1 gap-4 text-xs">
      <div class="form rm">
        <v-select
          placeholder="Silahkan Pilih Laboratorium"
          :options="listLab"
          v-model="lab"
          @update:model-value="onSelectLab"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { MainData as MainDataLab } from '@/components/dashboard/admin/cruds/labs/controller'
import { MainData } from '@/components/dashboard/admin/cruds/asset-lab/controller'

const main = new MainData()
const mainLab = new MainDataLab()

export default {
  data() {
    return {
      lab: null,
    }
  },
  computed: {
    listLab() {
      return mainLab.items.map((item) => {
        return {
          label: item.nama,
          value: item.id,
        }
      })
    },
    item() {
      return main.data
    },
  },
  methods: {
    onSelectLab(e) {
      this.item.id = e?.value
      this.item.dataOnly = e ?? {}
    },
  },
  async mounted() {
    await mainLab.init()
  },
}
</script>
