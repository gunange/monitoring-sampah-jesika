import { format, parse } from 'date-fns'

/* 
!  confing

?  npm i @vueuse/core
?  npm install date-fns --save 

*/

export class TimeApp {
  realTime = false

  formatDate(date, time = false) {
    const formatDate = time ? 'eeee, dd MMMM y (HH:mm:ss)' : 'eeee, dd MMMM y'
    return format(date ?? new Date(), formatDate)
  }
  dateToTime(date, time = false) {
    const formatDate = time ? 'HH:mm:ss' : 'HH:mm:ss'
    return format(date ?? new Date(), formatDate)
  }

  formatTo(date, formatDate = 'yyyy-MM-dd') {
    return format(date ?? new Date(), formatDate)
  }
  parseTo(date) {
    return new Date(date)
  }

  calculateAge(birthdate, detail = false) {
    const today = new Date()
    const birthDate = new Date(birthdate ?? '')
    let years = today.getFullYear() - birthDate.getFullYear()
    let months = today.getMonth() - birthDate.getMonth()
    let days = today.getDate() - birthDate.getDate()

    if (months < 0 || (months === 0 && days < 0)) {
      years--
      months += 12
    }
    if (days < 0) {
      const previousMonth = new Date(today.getFullYear(), today.getMonth(), 0)
      days += previousMonth.getDate()
    }

    if (detail) {
      return `${years} tahun ${months} bulan ${days} hari`
    } else {
      return years
    }
  }
}
