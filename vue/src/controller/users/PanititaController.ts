import axios from 'axios'
import { pathApi } from '@/components/dashboard/panitia/config'
import { delay } from '../tools'

export class PanitiaController {
  profil = {
    sukses: false,
    load: false,
    data: {},
  }

  async init() {
    await this.initProfil()
  }
  async initProfil() {
    if (this.profil.load) return
    this.profil.load = true

    const { data, status } = await axios(`${pathApi}`)
    if (status == 200) this.profil.data = data.data
    this.profil.sukses = status === 200
    this.profil.load = false
  }

  async reset() {
    this.profil.data = {}
    this.profil.sukses = false
    this.profil.load = false

    await delay(200)
  }
}
