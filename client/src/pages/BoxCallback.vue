<script setup>
import { useRoute, useRouter } from "vue-router";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { useSession } from "@clerk/vue";
const { session } = useSession();
import { ref } from "vue";

const router = useRouter();
const route = useRoute();
const email = ref("");
const API_URL = import.meta.env.VITE_API_URL;
const errorText = ref("");

async function completeIntegration() {
  console.log(email.value);
  if (email.value !== "") {
    const code = route.query.code;

    const payload = {
      code,
      user_id: email.value,
    };

    let response = await fetch(`${API_URL}/api/box/exchange`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.value.id}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let res = await response.json();
      errorText.value = `Something went wrong: ${res['detail']}`
    } else {
      router.push("/dashboard");
    }
  }
}
</script>

<template>
  <div class="full-center">
    <div>
      <h3>Box Email</h3>
      <p class="subtitle">
        Please input the email of you BOX account that you just connected
      </p>
      <InputText placeholder="Input email" v-model="email" />
      <Button
        label="Complete Integration"
        icon="pi pi-external-link"
        class="box-button"
        @click="completeIntegration"
      />
      <p class="error-text">{{ errorText }}</p>
    </div>
  </div>
</template>

<style scoped>
.error-text{
  color: red;
  margin-top: 1rem;
}
.box-button {
  background-color: #0061d5;
  color: white;
  font-weight: bold;
  border-radius: 6px;
  margin-top: 0.5rem;
  margin-left: 1rem;
}

.subtitle {
  color: gray;
  width: 100%;
  text-align: center;
}
/* ensure the wrapper fills the viewport */
.full-center {
  display: flex;
  align-items: center; /* vertical centering */
  justify-content: center; /* horizontal centering */
  height: 100vh; /* full viewport height */
  margin: 0; /* reset any body margins if needed */
  text-align: center;
}
</style>

