<script setup>
import ProjectSetup from './ProjectSetup.vue';
import ResearchCenterChat from './ResearchCenterChat.vue';

</script>

<template>
    <main class="main-container">
        <div v-if="false">
        <ProjectSetup />
    </div>

    <div v-if="true">
        <ResearchCenterChat />
    </div>
    </main>

</template>

<style scoped>
.main-container{
    overflow-y: hidden;
}
</style>