import axios from 'axios'
import { pathApi } from '@/components/dashboard/calon-mahasiswa/config'
import { delay } from '../tools'
import { reactive } from 'vue'

export class CalonMahasiswaController {
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
    if (status == 200) {
      data.data.data.tanggal_lahir = new Date(data.data.data.tanggal_lahir)
      if (data.data.data_ayah)
        data.data.data_ayah.tanggal_lahir = new Date(data.data.data_ayah.tanggal_lahir)
      if (data.data.data_ibu)
        data.data.data_ibu.tanggal_lahir = new Date(data.data.data_ibu.tanggal_lahir)

      this.profil.data = data.data
    }

    this.profil.sukses = status === 200
    this.profil.load = false
  }
  setProfil(data) {
    this.profil.data['data'] = data ?? {}
  }
  setDataAyah(data) {
    this.profil.data['data_ayah'] = data ?? {}
  }
  setDataIbu(data) {
    this.profil.data['data_ibu'] = data ?? {}
  }
  setDataWali(data) {
    this.profil.data['data_wali'] = data ?? {}
  }

  async reset() {
    this.profil.data = {}
    this.profil.sukses = false
    this.profil.load = false

    await delay(200)
  }
}
