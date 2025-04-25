<script setup>
import { ref } from "vue";

import ResearchCenterSidebar from "@/components/ResearchCenterSidebar.vue";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import InputGroup from "primevue/inputgroup";
</script>

<template>
  <h3 class="title">Research Center</h3>
  <div class="d-flex">
    <ResearchCenterSidebar />
    <div class="chat-section">
      <div class="empty-section">
        <center>
          <h2 class="gradient-text">Hello, Pranav</h2>
          <p class="subtext">
            I'm Luvon. Ask me anything about your project and I'm happy to help!
          </p>
          <div class="d-flex justify-content-center">
            <div class="row">
              <div class="command-card">
                <p class="command-title">Generate Graph</p>
                <p class="command-subtitle">Generate graphs according to your data</p>
              </div>

              <div class="command-card">
                <p class="command-title">Summarize Research</p>
                <p class="command-subtitle">Ask questions on whole project-wide context</p>
              </div>

              <div class="command-card">
                <p class="command-title">Summarize Data</p>
                <p class="command-subtitle">Summarize data that is collected and uploaded</p>
              </div>
            </div>
          </div>
        </center>
      </div>

      <div class="d-flex justify-content-center">
        <InputGroup class="chat-input-group">
          <InputText
            v-model="searchTerm"
            placeholder="Ask anything..."
            class="chat-input"
          />
          <Button icon="pi pi-send" />
        </InputGroup>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title {
  margin-left: 1rem;
}
.chat-section {
  margin-left: 2vw;
  width: 60%;
  margin-left: 20%;
  height: 100%;
}

.chat-input-group {
  width: 50vw;
  position: fixed;
  bottom: 0;
  margin-bottom: 2rem;
}
.chat-input {
  outline: none;
}

.empty-section {
  margin-top: 20vh;
}

.subtext {
  color: rgb(101, 100, 100);
  max-width: 40%;
}

.gradient-text {
  background: linear-gradient(to bottom right, #00c9ff 0%, #92fe9d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

.command-card {
  height: 5rem;
  max-width: 12rem;
  width: fit-content;
  border: 1px gray solid;
  border-radius: 8px;
  margin-right: 1rem;
  transition: background-color 0.1s ease-in;
}

.command-card:hover{
    cursor: pointer;
    background-color: #e6e6e6;
}

.command-title{
    color: black;
    font-weight: bold;
    margin: 0;
    padding: 0;
    text-align: left;
}

.command-subtitle{
    margin-top: 0rem;
    padding: 0;
    color: gray;
    text-align: left;
    font-size: 13px;
}
</style>
