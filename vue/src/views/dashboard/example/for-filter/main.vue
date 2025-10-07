<template>
  <div>
    <div class="px-5 mt-5">
      <BradcumpWidget
        :home="{
          icon: 'pi pi-home',
          route: `/${pathRoute}`,
        }"
        :items="[{ label: 'Library', route: `/${pathRoute}` }]"
      />
    </div>
    <div class="px-5 mt-5">
      <FilterView />
    </div>
    <div class="px-5 mt-5">
      <TableView />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

import BradcumpWidget from '@/widgets/others/bardcump-widget.vue'

// config path
import { dataEnv } from '@/components/dashboard/admin/config/index.ts'
import { MainData } from '@/components/dashboard/admin/cruds/software/controller'
import TableView from './table.vue'
import FilterView from './filter.vue'

const main = new MainData()

export default {
  components: {
    BradcumpWidget,
    TableView,
    FilterView,
  },
  data() {
    return {}
  },

  computed: {
    pathRoute() {
      return dataEnv.path_route
    },
  },
}
</script>
