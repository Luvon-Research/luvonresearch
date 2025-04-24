<script setup>
import Button from "primevue/button";
import { ref } from "vue";

import Stepper from "primevue/stepper";
import StepList from "primevue/steplist";
import StepPanels from "primevue/steppanels";
import Step from "primevue/step";
import StepPanel from "primevue/steppanel";
import InputText from "primevue/inputtext";
import FloatLabel from "primevue/floatlabel";
import Textarea from "primevue/textarea";
const projectName = ref(null);
const projectDescription = ref(null);
</script>

<template>
  <div class="d-flex justify-content-center">
    <Stepper value="1" linear>
      <StepList style="width: 40vw">
        <Step value="1">Get Started</Step>
        <Step value="2">Project Info</Step>
        <Step value="3">Complete</Step>
      </StepList>
      <StepPanels>
        <StepPanel v-slot="{ activateCallback }" value="1">
          <div class="flex flex-col h-48">
            <center>
              <img
                src="../assets/undraw_designer.svg"
                class="create-project-img"
              />
              <h4 class="create-title">Create Research Project</h4>
              <p class="create-subtitle">
                Create a research project with all the details
              </p>
              <Button
                label="Create"
                icon="pi pi-arrow-right"
                iconPos="right"
                @click="activateCallback('2')"
              />
            </center>
          </div>
        </StepPanel>
        <StepPanel v-slot="{ activateCallback }" value="2">
          <div class="flex flex-col h-48">
            <div class="d-flex justify-content-center">
              <div class="project-name-section">
                <FloatLabel class="project-input" variant="in">
                  <Textarea
                    id="project-desc"
                    v-model="projectDescription"
                    class="project-description-input"
                    placeholder="Include as much information as you can about your project. Including what you are researching, what data you collect, the goal of your research, etc..."
                    rows="5"
                    autoResize
                  />
                  <label for="project-desc">Project Description</label>
                </FloatLabel>
              </div>
            </div>
          </div>
          <center class="flex justify-between btn-section">
            <Button
              label="Back"
              severity="secondary"
              icon="pi pi-arrow-left"
              @click="activateCallback('1')"
            />
            <Button
              label="Submit"
              icon="pi pi-sparkles"
              iconPos="right"
              @click="activateCallback('3')"
            />
          </center>
        </StepPanel>
        <StepPanel v-slot="{ activateCallback }" value="3">
          <div class="flex flex-col h-48">
            <center
              class=""
            >
            <img src="../assets/complete.svg" alt="" class="complete-img">
            <h4 class="create-title">You're all set!</h4>
            <p>Your research center is now available. Click below to access it.</p>
            <Button label="Take me there" icon="pi pi-arrow-right" iconPos="right"></Button>
          </center>
          </div>
        </StepPanel>
      </StepPanels>
    </Stepper>
  </div>
</template>

<style scoped>
.create-project-img {
  width: 15vw;
  margin-top: 8vh;
}

.create-title {
  font-weight: bold;
  margin-top: 2rem;
}

.create-subtitle {
  color: gray;
}

.project-name-input {
  width: 25vw;
}

.project-name-section {
  margin-top: 1rem;
}

.project-input {
  margin-top: 1rem;
}

.btn-section {
  margin-top: 1rem;
}

.project-description-input {
  width: 25vw;
  min-height: 13rem;
}

.complete-img{
    width: 13rem;
}
</style>
