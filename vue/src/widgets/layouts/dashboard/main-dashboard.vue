<script setup>
import '@/assets/css/dashboard/main.css'
import '@/assets/css/dashboard/responsif.css'
import '@/assets/css/dashboard/costume.css'

import ContentDashboard from './content-dashboard.vue'
import SideDashboard from './side-dashboard.vue'
import GantiPassword from './ganti-password.vue'

import { dashboardStore } from '@/stores/others/dashboard'
import { storeToRefs } from 'pinia'
const { sidebarActive } = storeToRefs(dashboardStore())

const props = defineProps({
  navbar: {
    type: Object,
    default: {
      profilMenu: [
        {
          label: 'Logout',
          icon: 'pi pi-power-off text-red-500',
          command: () => {
            console.log('OK')
          },
        },
      ],
      notif: [
        {
          label: 'Notif 1',
          icon: 'pi pi-paperclip',
          command: () => {
            console.log('OK')
          },
        },
      ],
      message: [
        {
          label: 'Message 1',
          icon: 'pi pi-paperclip',
          command: () => {
            console.log('OK')
          },
        },
        {
          label: 'Message 2',
          icon: 'pi pi-paperclip',
          command: () => {
            console.log('OK')
          },
        },
      ],
    },
  },

  sidebar: {
    type: Object,
    default: {
      menu: [
        {
          label: 'Router',
          icon: 'pi pi-palette',
          items: [
            {
              label: 'Styled',
              icon: 'pi pi-eraser',
              route: '/',
            },
            {
              label: 'Unstyled',
              icon: 'pi pi-heart',
              route: '/',
            },
          ],
        },
        {
          label: 'Programmatic',
          icon: 'pi pi-link',
          command: () => {
            // router.push('/introduction');
          },
        },
        {
          label: 'External',
          icon: 'pi pi-home',
          items: [
            {
              label: 'Vue.js',
              icon: 'pi pi-star',
              url: 'https://vuejs.org/',
            },
            {
              label: 'Vite.js',
              icon: 'pi pi-bookmark',
              url: 'https://vuejs.org/',
            },
          ],
        },
      ],
    },
  },
  title: {
    type: String,
    default: 'Title',
  },
  subTitle: {
    type: String,
    default: 'Sub Title',
  },
  nama: {
    type: String,
    default: 'Unknow',
  },
})
</script>

<template>
  <main class="dashboard">
    <div class="wrapper" :class="{ 'side-active': sidebarActive }">
      <SideDashboard :menu="sidebar.menu" :title="title" :sub-title="subTitle" />
      <ContentDashboard
        :profil-menu="navbar.profilMenu"
        :notif="navbar.notif"
        :message="navbar.message"
        :nama="nama"
      >
        <slot></slot>
      </ContentDashboard>
    </div>
    <GantiPassword />
  </main>
</template>
