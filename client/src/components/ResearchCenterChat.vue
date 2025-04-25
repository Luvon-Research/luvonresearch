<script setup>
import { ref } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import InputGroup from "primevue/inputgroup";
import ChatSuggestion from "./ChatSuggestion.vue";

const collapsed = ref(true);

const chatInput = ref("");

function inputCommandSuggestion(value){
  chatInput.value = value;
  console.log(value)
}
</script>

<template>
  <div class="main-container">
    <div class="d-flex">
      <div :class="['sidebar', { collapsed }]">
        <!-- Menu -->
        <Panel class="menu" :style="{ display: collapsed ? 'none' : 'block' }">
          <h4 class="history-label">History</h4>
          <div class="history-new-chat">
            <center>
              <p class="history-item-text-new-chat">
                New Chat<i class="pi pi-plus new-chat-icon"></i>
              </p>
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
      <button @click="collapsed = !collapsed" class="toggle-btn">
        <i :class="'pi pi-chevron-' + (collapsed ? 'right' : 'left')"></i>
      </button>

      <div class="chat-section">
        <div class="empty-section">
          <center>
            <h2 class="gradient-text">Hello, Pranav</h2>
            <p class="subtext">
              I'm Luvon. Ask me anything about your project and I'm happy to
              help!
            </p>
            <div class="container">
              <div class="row row-cols-2 g-0 justify-content-center">
                <div class="col-auto d-flex justify-content-center">
                  <ChatSuggestion
                    title="Perform Research"
                    icon="pi-search-plus"
                    color="rgb(186, 255, 203)"
                    prompt="Research and bring me and analysis on "
                    @select="inputCommandSuggestion"
                  />
                </div>
                <div class="col-auto d-flex justify-content-center">
                  <ChatSuggestion
                    title="Create Chart"
                    icon="pi-chart-bar"
                    color="#ffc9b3"
                    prompt="Create me a chart for "
                    @select="inputCommandSuggestion"
                  />
                </div>
                <div class="col-auto d-flex justify-content-center">
                  <ChatSuggestion
                    title="Generate Report"
                    icon="pi-file-check"
                    color="#c2d6ff"
                    prompt="Generate me a report for "
                    @select="inputCommandSuggestion"
                  />
                </div>
                <div class="col-auto d-flex justify-content-center">
                  <ChatSuggestion
                    title="AutoML Predict"
                    icon="pi-microchip-ai"
                    color="#ffb0b7"
                    prompt="Use ML to predict "
                    @select="inputCommandSuggestion"
                  />
                </div>
                <div class="col-auto d-flex justify-content-center">
                  <ChatSuggestion
                    title="AutoML Predict"
                    icon="pi-microchip-ai"
                    color="#ffb0b7"
                    prompt="Use ML to predict "
                    @select="inputCommandSuggestion"
                  />
                </div>
              </div>
            </div>
          </center>
        </div>

        <div class="d-flex justify-content-center">
          <InputGroup class="chat-input-group">
            <InputText
              v-model="chatInput"
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

.command-subtitle {
  margin-top: 0rem;
  padding: 0;
  color: gray;
  text-align: left;
  font-size: 13px;
  margin-left: 0.2rem;
}

.command-icon {
  margin-right: 10%;
  background-color: rgb(129, 129, 129);
  height: 2.2rem;
  width: 2.2rem;
  margin-top: 4%;
  border-radius: 5px;
  padding-top: 0.5rem;
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

.history-item-active {
  height: 3rem;
  width: 92%;
  margin-left: 4%;
  border-radius: 8px;
  background-color: #e3e3e3;
  cursor: pointer;
}

.history-item {
  height: 3rem;
  width: 92%;
  margin-left: 4%;
  border-radius: 5px;
  background-color: transparent;
}

.history-item:hover {
  background-color: #f4f3f3;
}

.history-item-text {
  margin-left: 1rem;
  padding-top: 0.8rem;
  color: black;
  font-size: 14px;
}

.history-new-chat {
  height: 2.5rem;
  border: 1px gray solid;
  width: 92%;
  border-radius: 5px;
  margin-bottom: 0.4rem;
  margin-left: 4%;
  cursor: pointer;
}

.history-new-chat:hover {
  background-color: #f4f3f3;
}

.history-item-text-new-chat {
  margin-top: 0.5rem;
  font-size: 13px;
}

.new-chat-icon {
  margin-left: 0.3rem;
  font-size: 12px;
  padding-top: 0.2rem;
}

.history-label {
  margin-left: 4%;
  margin-top: 0.5rem;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 1rem;
}
</style>
