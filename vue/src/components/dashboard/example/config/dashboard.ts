import { routerStore } from '@/stores/services/router-store'
import { AuthController } from '@/controller/controllers/AuthController'
import { path_route } from './data-env'
const route = routerStore()

const notif = [
  {
    label: 'Notif 1',
    icon: 'pi pi-paperclip',
    command: () => {
      console.log('OK')
    },
  },
]

const menu = [
  {
    label: 'Home',
    icon: 'pi pi-home',
    route: `${path_route}/main`,
  },
  {
    label: 'Feeder',
    icon: 'pi pi-th-large',
    route: `${path_route}/feeder`,
  },
]

const profilMenu = [
  {
    label: 'Logout',
    icon: 'pi pi-power-off text-red-500',
    command: () => {
      const auth = new AuthController()
      auth.signOut(() => {
        route.router.replace('/login')
      })
    },
  },
]

const message = [
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
]

export const sidebar = {
  menu: menu,
}

export const navbar = {
  profilMenu: profilMenu,
  message: message,
  notif: notif,
}
