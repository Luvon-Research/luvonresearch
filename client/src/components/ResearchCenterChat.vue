<script setup>
import { ref } from "vue";

import ResearchCenterSidebar from "@/components/ResearchCenterSidebar.vue";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import InputGroup from "primevue/inputgroup";
import PanelMenu from "primevue/panelmenu";

const collapsed = ref(true);
</script>

<template>
    <div class="main-container">
        <div class="d-flex">
    <div :class="['sidebar', { collapsed }]">
      <!-- Menu -->
      <Panel class="menu" :style="{ display: collapsed ? 'none' : 'block'}">
        <h4 class="history-label">History</h4>
        <div class="history-new-chat">
            <center>
                <p class="history-item-text-new-chat">New Chat<i class="pi pi-plus new-chat-icon"></i></p>
            </center>
        </div>
        <div class="history-item-active">
            <p class="history-item-text">Research Chat</p>
        </div>
        <div class="history-item">
            <p class="history-item-text">Research Chat</p>
        </div>
      </Panel>
    </div>

    <!-- Toggle Button -->
    <Button @click="collapsed = !collapsed" class="toggle-btn">
      <i class="pi pi-table"></i>
    </Button>

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
                <p class="command-title"><i class="pi pi-chart-bar command-icon"></i>Generate Graph</p>
                <p class="command-subtitle">
                  Generate graphs according to your data
                </p>
              </div>

              <div class="command-card">
                <p class="command-title"><i class="pi pi-sparkles command-icon"></i>Summarize Research</p>
                <p class="command-subtitle">
                  Ask questions on whole project-wide context
                </p>
              </div>

              <div class="command-card">
                <p class="command-title"><i class="pi pi-folder-open command-icon"></i>Summarize Data</p>
                <p class="command-subtitle">
                  Summarize data that is collected and uploaded
                </p>
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
    </div>

</template>

<style scoped>
.title {
  margin-left: 1rem;
}
.chat-section {
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
  padding-left: 1rem;
}

.chat-input:focus {
  box-shadow: none !important;
}

.empty-section {
  margin-top: 14vh;
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
  border: 1px solid gray;
  border-radius: 8px;
  margin-right: 1rem;
  transition: background-color 0.2s ease-in;
}

.command-card:hover {
  cursor: pointer;
  background-color: #f1f1f1;
}

.command-title {
  color: black;
  font-weight: bold;
  margin: 0;
  padding: 0;
  text-align: left;
  font-size: 14px;
  margin-left: 0.2rem;
  margin-top: 0.4rem;

}

.command-subtitle {
  margin-top: 0rem;
  padding: 0;
  color: gray;
  text-align: left;
  font-size: 13px;
  margin-left: 0.2rem;
}

.command-icon{
    margin-right: 0.4rem;
}

.sidebar {
  background: #f9f9f9;
  width: 250px;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-top: 0rem;
  height: 73vh;
  overflow-y: auto;   
  border-radius: 5px;
}

.sidebar.collapsed {
  width: 0rem;
}

.toggle-btn {
  margin: 0 0rem 1rem;
  background: white;
  border: none;
  font-size: 1.2rem;
  color: black;
  height: 1rem;
}

.menu {
  flex: 1;
  width: 100%;
}

.history-item-active{
    height: 3rem;
    width: 92%;
    margin-left: 4%;
    border-radius: 8px;
    background-color: #e3e3e3;
    cursor: pointer;
}

.history-item{
    height: 3rem;
    width: 92%;
    margin-left: 4%;
    border-radius: 5px;
    background-color: transparent;
}

.history-item:hover{
    background-color: #f4f3f3;
}

.history-item-text{
    margin-left: 1rem;
    padding-top: 0.8rem;
    color: black;
    font-size: 14px;
}

.history-new-chat{
    height: 2.5rem;
    border: 1px gray solid;
    width: 92%;
    border-radius: 5px;
    margin-bottom: 0.4rem;
    margin-left: 4%;
    cursor: pointer;
}

.history-new-chat:hover{
    background-color: #f4f3f3;
}

.history-item-text-new-chat{
    margin-top: 0.5rem;
    font-size: 13px;
}

.new-chat-icon{
    margin-left: 0.3rem;
    font-size: 12px;
    padding-top: 0.2rem;
}

.history-label{
    margin-left: 4%;
    margin-top: 0.5rem;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 1rem;
}
</style>
