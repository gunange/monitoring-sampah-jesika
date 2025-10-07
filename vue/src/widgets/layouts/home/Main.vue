<template>
	<div>
		<Header />
		<slot></slot>
		<FooterCostume />
	</div>
</template>

<script>
import Header from './Header.vue';
import FooterCostume from './FooterCostume.vue';


export default {
	components : {
		Header,
		FooterCostume,
	}
}
</script>