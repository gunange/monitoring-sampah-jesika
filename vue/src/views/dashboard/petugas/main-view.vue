<template>
  <div>
    <div class="px-5 mt-5">
      <BradcumpWidget
        :home="{
          icon: 'pi pi-home',
          route: pathRoute,
        }"
        :items="[{ label: 'Library', route: `/${pathRoute}` }]"
      />
    </div>
    <div class="px-5 mt-5 grid min-sm:grid-cols-3 gap-4">
      <MlComp />
    </div>
  </div>
</template>

<script>
import BradcumpWidget from '@/widgets/others/bardcump-widget.vue'
import { dataEnv } from '@/components/dashboard/admin/config/index.ts'

import MlComp from '@/components/dashboard/admin/components/ml-view.vue'

export default {
  name: 'MainView',
  components: {
    BradcumpWidget,
    MlComp,
  },
  computed: {
    pathRoute() {
      return dataEnv.path_route
    },
  },
}
</script>
