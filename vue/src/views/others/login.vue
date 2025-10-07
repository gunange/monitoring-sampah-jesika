<script setup>
import '@/assets/css/login/main.css'
import '@/assets/css/login/responsif.css'
import '@/assets/css/login/costume.css'

import SlideRight from '@/components/login/view/slide-right.vue'
import SlideLeft from '@/components/login/view/slide-left.vue'
</script>

<template>
  <div class="login bg-indigo-300 flex justify-center items-center">
    <div
      class="wrapper flex w-[90%] md:w-[85%] xl:w-[75%] h-[90vh] xl:h-[90vh] overflow-hidden rounded-3xl"
    >
      <SlideLeft />
      <SlideRight />
    </div>
  </div>
</template>

<script>
import { AuthController } from '@/controller/controllers/AuthController.ts'
import { Controller } from '@/components/login/controller.ts'
import { RequestApiController } from '@/controller/others/RequestApiController'

const auth = new AuthController()
const apiC = new RequestApiController()

export default {
  async beforeRouteEnter(to, from, next) {
    apiC.setupNewPath(`${apiC.url}user`)
    await auth.init()
    apiC.resetPath()

    if (auth.isAuth) {
      const controller = new Controller()
      const routeTo = controller.routeRedirect({
        role: auth.user?.Role.role,
      })

      if (routeTo) {
        next(routeTo)
        return
      }
    }
    next()
  },
}
</script>
