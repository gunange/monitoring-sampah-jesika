<script setup>
import { appLogo } from '@/config/appInfo'
</script>

<template>
  <main>
    <div id="loading-area">
      <div class="content-loading">
        <div class="row text-light text-center mt-4">
          <div class="col-lg-2 col-md-4 col-8 px-lg-0 px-5 mx-auto mb-4">
            <div class="hero-video-head">
              <div class="video-inner">
                <img class="img-fluid" :src="appLogo" alt="" />
                <div class="promo-video">
                  <div class="waves-block">
                    <div class="waves wave-1"></div>
                    <div class="waves wave-2"></div>
                    <div class="waves wave-3"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <h6 class="title text-light">Title</h6>
          <p class="sub-title">Title</p>
        </div>
      </div>
    </div>
  </main>
</template>
