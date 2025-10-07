<template>
  <div class="card">
    <div class="card-header flex justify-between">
      <div class="flex-none flex items-center">
        <h6>
          <i class="pi pi-sparkles" /> <span>Asset Lab </span>
          <span v-if="id">( {{ item.label }} )</span>
        </h6>
      </div>

      <div class="flex items-center justify-end">
        <Button
          icon="pi pi-refresh"
          class="ml-2"
          size="small"
          v-tooltip.top="'Refresh'"
          outlined
          @click="reset"
        />

        <Button
          icon="pi pi-plus"
          class="ml-2"
          size="small"
          v-tooltip.top="'Tambah Data'"
          outlined
          @click="$refs.ref_cruds.open('add', id)"
          v-if="id"
        />
      </div>
    </div>
    <div class="card-body">
      <div class="search-easy-table mb-5">
        <InputGroup class="">
          <InputGroupAddon>
            <i class="pi pi-search text-primary"></i>
          </InputGroupAddon>
          <InputText placeholder="Search.." v-model="table.search" />
        </InputGroup>
      </div>
      <EasyDataTable
        :items="items"
        :loading="loadItems"
        :headers="table.th"
        :search-value="table.search"
        :sort-by="table.sort"
        :sort-type="table.sortType"
        :rowsItems="table.rowsItems"
        :rowsPerPage="table.rowsPerPage"
        rows-per-page-message="Jumlah data per-halaman"
        rows-of-page-separator-message="dari"
        theme-color="rgb(var(--primary))"
        table-class-name="customize-table"
        empty-message="Data tidak ditemukan"
        show-index
      >
        <template #header-operation>
          <div class="text-center">
            <i class="pi pi-spin pi-cog"></i>
          </div>
        </template>
        <template #item-operation="item">
          <div class="" style="position: relative">
            <SpeedDial
              direction="left"
              style="position: absolute; top: -10px; height: 25px; right: 48%"
              :model="[
                {
                  label: 'Update',
                  icon: 'pi pi-pencil text-red',
                  severity: 'success',
                  command: () => $refs.ref_cruds.open('up', item.id),
                },
                {
                  label: 'Delete',
                  icon: 'pi pi-trash',
                  severity: 'danger',
                  command: () => $refs.ref_cruds.open('del', item.id),
                },
              ]"
            >
              <template #button="{ toggleCallback }">
                <Button class="" @click="toggleCallback" icon="pi pi-align-right" size="small" />
              </template>
              <template #item="{ item, toggleCallback }">
                <Button
                  :icon="item.icon"
                  :title="item.label"
                  rounded
                  :severity="item.severity ?? 'secondary'"
                  @click="toggleCallback"
                />
              </template>
            </SpeedDial>
          </div>
        </template>

        <template #loading>
          <img src="/assets/gif/bola.gif" style="width: 100px; height: 80px" />
        </template>

        <template #expand="item">
          <div class="" v-if="item.catatan">
            <b>Catatan</b>
            <p>{{ item.catatan }}</p>
          </div>
        </template>
      </EasyDataTable>
    </div>

    <Cruds ref="ref_cruds" />
  </div>
</template>

<script>
import { ref } from 'vue'

import BradcumpWidget from '@/widgets/others/bardcump-widget.vue'

// config path
import { dataEnv } from '@/components/dashboard/admin/config/index.ts'
import { MainData } from '@/components/dashboard/admin/cruds/asset-lab/controller'
import Cruds from '@/components/dashboard/admin/cruds/asset-lab/views/index.vue'

const main = new MainData()

export default {
  components: {
    BradcumpWidget,
    Cruds,
  },
  data() {
    return {
      table: ref({
        search: ref(''),
        th: [
          { text: 'Assets', value: 'nama' },
          { text: 'Kondisi', value: 'kondisi' },

          { text: 'Operation', value: 'operation' },
        ],
        isUpdate: false,
        itemsSelected: [],
        sort: ['tanggal', 'waktu'],
        sortType: ['desc', 'desc'],
        rowsItems: [15, 25, 50],
        rowsPerPage: 15,
      }),
    }
  },

  computed: {
    pathRoute() {
      return dataEnv.path_route
    },
    items() {
      return main.items.filter((e) => e.lab_id === this.id)
    },
    item() {
      return main.data.dataOnly
    },
    id() {
      return main.data.id
    },
    loadItems() {
      return main.data.load
    },
  },
  methods: {
    reset() {
      return main.reset()
    },
    validasiItem(item) {
      if (item.KomputerStatus) {
        return this.$refs.ref_cruds.open('up', item.KomputerStatus)
      } else {
        return this.$refs.ref_cruds.open('add', item.id)
      }
    },
  },
  async mounted() {
    await main.init()
  },
}
</script>
