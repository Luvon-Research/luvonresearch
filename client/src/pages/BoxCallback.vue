<script setup>
import { useUser } from "@clerk/vue";
import { useRoute, useRouter } from "vue-router";
import { onMounted } from "vue";

const { user } = useUser();
const route = useRoute();
const router = useRouter();

onMounted(async () => {
  const code = route.query.code;
  router.push("/dashboard"); 
  }
);
</script>
