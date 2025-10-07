<template>
  <div class="not-found">
    <div class="d-block text-center">
      <h1>Opps !</h1>
      <p class="mt-5 mb-3 text-2xl">Halaman yang anda cari tidak ditemukan</p>
      <Button label="Kembail" onclick="window.location.href = history.go(-1)" />
    </div>
  </div>
</template>

<style scoped>
.not-found {
  width: 100%;
  height: 90vh;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  color: rgb(var(--surface-500));
}
h1 {
  font-size: 15pc;
  color: rgb(var(--primary));
  font-weight: 700;
}
</style>
