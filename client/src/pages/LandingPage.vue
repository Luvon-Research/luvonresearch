<script setup lang="ts">
import { watchEffect, ref, onMounted } from "vue";
import { SignInButton, useAuth, useSession, Waitlist } from "@clerk/vue";
import { useRouter } from "vue-router";
import { Button } from "primevue";
import { onBeforeUnmount } from "vue";
import LandingPageInfoCard from "@/components/LandingPageInfoCard.vue";
import Dialog from "primevue/dialog";

// Remove AOS imports and any animation-related code
let vantaEffect: any = null;
const isScrolled = ref(false);

onMounted(() => {
  // Remove AOS initialization, keep other onMounted code
  if (window.VANTA && window.VANTA.DOTS) {
    vantaEffect = window.VANTA.DOTS({
      el: "#vanta-background",
      showLines: false,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.0,
      minWidth: 200.0,
      speed: 1.0,
      verticalSpeed: 2,
      horizontalSpeed: 2,
      scale: 1.0,
      scaleMobile: 1.0,
      color: 0x5158c7,
      color2: 0x7784ec,
      backgroundColor: 0xffffff,
    });
  }

  const vh = window.innerHeight;

  // Add scroll listener for navbar
  const handleScroll = () => {
    isScrolled.value = window.scrollY > 50;
  };

  window.addEventListener("scroll", handleScroll, { passive: true });

  onScroll = () => {
    if (!section.value) return;
    const top = section.value.offsetTop;
    const scrollY = window.scrollY;

    let progress = scrollY - top;
    const max = steps.length * vh - vh;
    progress = Math.max(0, Math.min(progress, max));
    activeStep.value = Math.floor(progress / vh);
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Cleanup function
  const cleanup = () => {
    window.removeEventListener("scroll", handleScroll);
    window.removeEventListener("scroll", onScroll);
  };

  onBeforeUnmount(cleanup);
});

onBeforeUnmount(() => {
  // Clean up Vanta effect
  if (vantaEffect) {
    vantaEffect.destroy();
  }
});

interface Step {
  title: string;
  description: string;
  side: "left" | "right";
}

const steps: Step[] = [
  {
    title: "Create your research workspace",
    description:
      "Set up a dedicated space for your research project and invite your team members to collaborate.",
    side: "left",
  },
  {
    title: "Import your research data",
    description:
      "Seamlessly import data from various sources including PDFs, spreadsheets, and databases into one centralized location.",
    side: "right",
  },
  {
    title: "Analyze and collaborate",
    description:
      "Use our powerful tools to analyze your data, create visualizations, and collaborate with your team in real-time.",
    side: "left",
  },
  {
    title: "Generate insights",
    description:
      "Leverage AI-powered features to extract meaningful insights and patterns from your research data.",
    side: "right",
  },
  {
    title: "Share your findings",
    description:
      "Create professional reports and presentations to effectively communicate your research findings with stakeholders.",
    side: "left",
  },
];

const section = ref<HTMLElement | null>(null);
const activeStep = ref(0);

let onScroll: () => void;

// Particle animation functions
function getParticleStyle(index: number) {
  const delay = Math.random() * 20;
  const duration = 15 + Math.random() * 10;
  const size = 2 + Math.random() * 4;
  const left = Math.random() * 100;
  const opacity = 0.3 + Math.random() * 0.7;

  return {
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    width: `${size}px`,
    height: `${size}px`,
    opacity: opacity,
  };
}

function getStarStyle(index: number) {
  const delay = Math.random() * 5;
  const duration = 2 + Math.random() * 3;
  const left = Math.random() * 100;
  const top = Math.random() * 100;
  const size = 1 + Math.random() * 2;

  return {
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    width: `${size}px`,
    height: `${size}px`,
  };
}

// Add smooth scroll function
const scrollToWaitlist = () => {
  const waitlistSection = document.querySelector(".waitlist-section");
  if (waitlistSection) {
    waitlistSection.scrollIntoView({ behavior: "smooth" });
  }
};
</script>

<template class="landing-container">
  <!-- Vanta.js background -->
  <div id="vanta-background" class="vanta-container"></div>

  <section class="sticky-navbar" :class="{ scrolled: isScrolled }">
    <div class="d-flex justify-content-between">
      <div class="d-flex align-items-center">
        <img class="logo" src="@/assets/logo.svg" />
        <p class="logo-title">Luvon AI</p>
      </div>

      <div class="d-flex align-items-center">
        <a
          href="https://calendly.com/veyyakulashabd/30min"
          target="_blank"
          class="book-demo-btn"
          >Book a Demo</a
        >
        <Button
          variant="outlined"
          iconPos="right"
          label="Join Waitlist"
          icon="pi pi-list-check"
          class="join-waitlist-btn-outlined"
          @click="scrollToWaitlist"
        />
      </div>
    </div>
  </section>

  <section class="title-section" id="title-section">
    <div class="d-flex justify-content-center">
      <h1 class="main-title">
        Less Time on Data. More Time <br />
        on <span class="special-text">Science</span>
      </h1>
    </div>
    <div class="d-flex justify-content-center">
      <p class="subtitle">
        Streamline your research workflow with Luvon's AI-powered platform. From
        data collection to analysis, we help scientists focus on what matters
        most - making discoveries.
      </p>
    </div>

    <div class="d-flex justify-content-center">
      <div class="d-flex align-items-center">
        <a
          href="https://calendly.com/veyyakulashabd/30min"
          target="_blank"
          class="book-demo-btn"
          >Book a Demo</a
        >
        <Button
          iconPos="right"
          label="Join Waitlist"
          icon="pi pi-list-check"
          class="join-waitlist-btn"
          @click="scrollToWaitlist"
        />
      </div>
    </div>

    <div class="d-flex justify-content-center">
      <img class="header-image" src="../assets/luvon-screenshot.png" alt="Img"/>
    </div>
  </section>

  <section id="section-2" class="section-2">
    <div class="d-flex justify-content-center">
      <h2 class="subheading">
        Data entry shouldn't <br />
        feel like a drag
      </h2>
    </div>

    <div class="d-flex justify-content-center section-2-cards">
      <div class="row gap-4 justify-content-center">
        <LandingPageInfoCard
          title="Live Collaboration"
          description="Work together in real-time with your team using our integrated collaborative spreadsheets."
          img="src/assets\luvon-collaboration.png"
        />
        <LandingPageInfoCard
          title="AI-Powered Analysis"
          description="Let AI do the heavy lifting. Our intelligent assistant analyzes your data automatically."
          img="https://framerusercontent.com/images/yeqACn9LkszdOq5t3gWkxc7pdU.png?scale-down-to=1024"
        />
        <LandingPageInfoCard
          title="Smart Data Completion"
          description="Never worry about incomplete datasets again. Our AI can detect and fill missing values intelligently while maintaining data integrity."
          img="https://framerusercontent.com/images/yeqACn9LkszdOq5t3gWkxc7pdU.png?scale-down-to=1024"
        />
        <LandingPageInfoCard
          title="Instant Visualizations"
          description="Transform your data into beautiful charts and graphs with a single prompt. No more wrestling with complex charting tools."
          img="https://framerusercontent.com/images/yeqACn9LkszdOq5t3gWkxc7pdU.png?scale-down-to=1024"
        />
      </div>
    </div>
  </section>

  <section id="meet-luvon" class="meet-luvon-section">
    <div class="mask-wrapper">
      <div class="d-flex justify-content-center">
        <h2 class="meet-luvon-header">
          Meet <span class="mask-text">Luvon✨</span>
        </h2>
      </div>
    </div>

    <div class="meet-luvon-container desktop">
      <img
        src="@/assets/luvon_info.svg"
        alt="Luvon Info"
        class="meet-luvon-info-img"
      />
      <h4 class="meet-luvon-img-title">
        Accelerate your <br />
        research with <span class="meet-luvon-img-badge">AI</span>
      </h4>
      <p class="meet-luvon-img-subhead">
        With Luvon's advanced AI capabilities, you can accelerate your research
        process by up to 3x while maintaining the highest quality standards. Our
        intelligent platform automates tedious tasks, provides real-time
        insights, and helps you uncover hidden patterns in your data.
      </p>
      <div class="meet-luvon-img-actions align-items-center">
        <a
          href="https://calendly.com/veyyakulashabd/30min"
          target="_blank"
          class="book-demo-btn"
          >Book a Demo</a
        >
        <Button
          iconPos="right"
          label="Join Waitlist"
          icon="pi pi-list-check"
          class="join-waitlist-btn"
          @click="scrollToWaitlist"
        />
      </div>
    </div>

    <div class="meet-luvon-container mobile">
      <img
        src="@/assets/luvon_info_mobile.svg"
        alt="Luvon Info"
        class="meet-luvon-info-img"
      />
      <h4 class="meet-luvon-img-title">
        Accelerate your <br />
        research with <span class="meet-luvon-img-badge">AI</span>
      </h4>
      <p class="meet-luvon-img-subhead">
        With Luvon's advanced AI capabilities, you can accelerate your research
        process by up to 3x while maintaining the highest quality standards. Our
        intelligent platform automates tedious tasks, provides real-time
        insights, and helps you uncover hidden patterns in your data.
      </p>
      <div class="meet-luvon-img-actions align-items-center">
        <a
          href="https://calendly.com/veyyakulashabd/30min"
          target="_blank"
          class="book-demo-btn"
          >Book a Demo</a
        >
        <Button
          iconPos="right"
          label="Join Waitlist"
          icon="pi pi-list-check"
          class="join-waitlist-btn"
          @click="scrollToWaitlist"
        />
      </div>
    </div>
  </section>

  <section id="how-it-works" class="how-it-works-section">
    <div class="d-flex justify-content-center">
      <h2 class="subheading">How it works</h2>
    </div>
    <div class="d-flex justify-content-center">
      <p class="subtitle">
        With Luvon, you can streamline your research workflow with powerful
        AI-assisted tools for data analysis, collaboration, and insight
        generation - all in one integrated platform.
      </p>
    </div>

    <section ref="section" class="how-it-works">
      <!-- this container's height = steps * 100vh -->
      <div
        class="scroll-container"
        :style="{ height: `${steps.length * 100}vh` }"
      >
        <!-- this pins once the section hits top -->
        <div class="pin">
          <div class="timeline">
            <div class="timeline-line"></div>

            <div
              v-for="(step, i) in steps"
              :key="i"
              class="timeline-item"
              :class="step.side"
            >
              <div class="card" :class="{ 'active-card': activeStep === i }">
                <h4 class="timeline-card-title">{{ step.title }}</h4>
                <p class="timeline-card-description">{{ step.description }}</p>
              </div>

              <div class="marker">
                <div class="dot" :class="{ active: activeStep === i }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </section>

  <!-- Add Waitlist component here -->
  <section class="waitlist-section">
    <div class="d-flex justify-content-center">
      <div class="row">
        <div class="col">
          <div class="waitlist-sidebar">
            <h3 class="subheading">Join waitlist</h3>
            <p class="subtitle">
              Join our waitlist to get noitified when Luvon releases to the
              public!
            </p>
          </div>
        </div>

        <div class="col waitlist-box">
          <Waitlist />
        </div>
      </div>
    </div>
  </section>

  <section id="get-started-section" class="get-started-section">
    <div class="getting-started-card">
      <div class="getting-started-content">
        <p class="getting-started-icon">✧˖°.</p>
        <h2 class="getting-started-title">
          Get researching<br />
          with Luvon today!
        </h2>
        <div class="getting-started-actions">
          <a
            href="https://calendly.com/veyyakulashabd/30min"
            target="_blank"
            class="book-demo-btn"
            >Book a Demo</a
          >
        </div>
      </div>
    </div>
  </section>

  <section class="footer" id="footer">
    <div class="d-flex justify-content-center">
      <p>Copyright © 2025. LuvonAI. All rights reserved.</p>
    </div>
  </section>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Onest:wght@100..900&display=swap");

* {
  font-family: "DM Sans", sans-serif;
}

.landing-container {
  scroll-behavior: smooth;
  position: relative;
  overflow-x: hidden;
}
.sticky-navbar {
  position: fixed;
  top: 0;
  height: 5rem;
  width: 100vw;
  background-color: rgba(255, 255, 255, 0.95);
  z-index: 9999;
}

.sticky-navbar.scrolled {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.sticky-navbar.scrolled .logo-title {
  color: #5158c7;
}

.sticky-navbar.scrolled .book-demo-btn {
  color: #5158c7;
}

.sticky-navbar.scrolled .join-waitlist-btn-outlined {
  color: #5158c7;
  border-color: #5158c7;
}

.sticky-navbar.scrolled .join-waitlist-btn-outlined:hover {
  background-color: #5158c7 !important;
  color: white !important;
}

@keyframes bounceIn {
  0% {
    transform: translateY(-100%);
    opacity: 0;
  }
  60% {
    transform: translateY(10px);
    opacity: 1;
  }
  80% {
    transform: translateY(-5px);
  }
  100% {
    transform: translateY(0);
  }
}

.logo {
  margin: 1rem;
  width: 2.5rem;
}

.logo-title {
  font-size: 25px;
  font-weight: bold;
  margin-top: 0.5rem;
}

.book-demo-btn {
  text-decoration: none;
  color: black;
  font-weight: 600;
  cursor: pointer;
}

.join-waitlist-btn-outlined {
  margin-left: 1rem;
  margin-right: 1rem;
  color: #5158c7;
  border-color: #5158c7;
}
.join-waitlist-btn-outlined:hover {
  background-color: #5158c7 !important;
  color: white !important;
}

.main-title {
  font-size: 60px;
  text-align: center;
  font-weight: 500;
  margin-top: 22vh;
}
.main-title .special-text {
  color: #5158c7;
  font-weight: 500;
}

.subtitle {
  text-align: center;
  color: rgb(140, 140, 140);
  width: 30vw;
  margin-top: 0.4rem;
  font-size: 18px;
  line-height: normal;
}

.join-waitlist-btn {
  margin-left: 1rem;
  margin-right: 1rem;
  color: white;
  background-color: #5158c7;
  cursor: pointer;
}
.join-waitlist-btn:hover {
  background-color: #7784ec !important;
}

.header-image {
  width: 80vw;
  margin-top: 6vh;
  border-radius: 20px;
  border: 0.1px solid rgb(204, 204, 204);
  padding: 1rem;
  background-color: white;
}

.section-2 {
  margin-top: 10vh;
  position: relative;
  z-index: 2;
  background: transparent;
}

.subheading {
  font-weight: 500;
  color: black;
  max-width: 30vw;
  text-align: center;
  font-size: 40px;
}

.section-2-cards {
  margin-top: 3rem;
  max-width: 90vw;
  margin-left: auto;
  margin-right: auto;
}

.meet-luvon-section {
  margin-top: 10vh;
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  padding: 2rem;
}

.meet-luvon-header {
  font-size: 120px;
  font-weight: 500;
  text-align: center;
  color: black;
}

.mask-wrapper {
  /* enough height to scroll through the effect */
  height: min-content;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mask-text {
  font-size: inherit;
  font-weight: bold;

  /* Only the Luvon text gets the parallax background */
  -webkit-text-fill-color: transparent;
  background-clip: text;
  -webkit-background-clip: text;
  background-image: url("https://i.pinimg.com/564x/02/0b/15/020b15b5f5af324af93bed131b47a34c.jpg");
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  background-attachment: fixed; /* Parallax effect only on the text */
}

.meet-luvon-info-img {
  width: 80vw;
  margin-left: auto;
  margin-right: auto;
}

.meet-luvon-container {
  position: relative;
}

/* Top left text */
.meet-luvon-img-title {
  position: absolute;
  top: 10vh;
  left: 20vw;
  font-size: 30px;
  color: white;
}

.meet-luvon-img-subhead {
  position: absolute;
  top: 21vh;
  left: 20vw;
  font-size: 18px;
  max-width: 40vw;
  margin-top: 0.1rem;
  font-weight: 300;
  color: #e4e4e4;
}

.meet-luvon-img-actions {
  .book-demo-btn {
    color: white;
  }
  position: absolute;
  top: 37vh;
  left: 20vw;
}

.meet-luvon-img-badge {
  background-color: #bda4ff;
  padding-inline: 0.5rem;
  border-radius: 5px;
}

.mobile {
  display: none;
}
.desktop {
  display: block;
}

.how-it-works-section {
  margin-top: 10vh;
}

.how-it-works {
  text-align: center;
  padding: 4rem 1rem;
}

/* scroll‐container is tall so you can scroll through steps */
.scroll-container {
  position: relative;
}

/* pin this block at top */
.pin {
  position: sticky;
  top: 120px; /* adjust so your heading/subheading remain above */
}

/* timeline styling as before */
.timeline {
  position: relative;
  margin: 0 auto;
  padding: 2rem 0;
  width: 100%;
  max-width: 800px;
}
.timeline-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 4px;
  background-color: #7157ff;
  transform: translateX(-50%);
}
.timeline-item {
  position: relative;
  display: flex;
  width: 100%;
  margin-bottom: 4rem;
  align-items: center;
  transition: transform 0.3s;
}
.timeline-item.left .card {
  margin-right: auto;
  margin-left: 0;
}
.timeline-item.right {
  flex-direction: row-reverse;
}
.timeline-item.right .card {
  margin-left: auto;
  margin-right: 0;
}

.timeline-card-title {
  font-size: 20px;
}

.timeline-card-description {
  font-size: 15px;
  color: #505050;
}

.card {
  background: #f0f0f0;
  padding: 1.5rem 2rem;
  border-radius: 10px;
  max-width: 45%;
  text-align: left;
  transition: transform 0.3s, box-shadow 0.3s;
}
/* scale up the active card */
.active-card {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.marker {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}
.dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 4px solid #7157ff;
  background: white;
  transition: background-color 0.3s, transform 0.3s;
}
/* highlight the active dot */
.dot.active {
  background: #7157ff;
  transform: scale(1.2);
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.get-started-section {
  padding: 4rem 0;
  margin-bottom: 4rem;
}

.getting-started-card {
  position: relative;
  min-height: 50vh;
  width: 80vw;
  margin: 0 auto;
  border-radius: 20px;
  background-image: url("https://i.pinimg.com/originals/31/cd/41/31cd41c991b956a6b7b8a060a5cb3460.jpg");
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  background-attachment: fixed;

  .book-demo-btn {
    color: white;
  }
}

/* center your content in the card */
.getting-started-content {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: white;
}

/* optional sparkle icon */
.getting-started-icon {
  font-size: 7rem;
  color: white !important;
}

/* headline */
.getting-started-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  margin-top: -3rem;
}

/* -------------- Clerk Sign‑In Override -------------- */
/* button:focus {
  outline: none;
} */

/* Option 1: Smooth CSS scroll behavior */
html {
  scroll-behavior: smooth;
}

/* Option 2: Custom smooth scrolling with CSS transitions */
* {
  font-family: "DM Sans", sans-serif;
}

/* Add momentum scrolling for webkit browsers */
body {
  -webkit-overflow-scrolling: touch;
}

/* Smooth scroll with custom timing */
html {
  scroll-behavior: smooth;
  scroll-padding-top: 5rem; /* Account for fixed navbar */
}

/* Optional: Add a subtle scroll snap effect for sections */
.landing-container {
  /* Remove the old scroll-behavior: smooth; since we're setting it on html */
}

/* Add smooth transitions to elements that animate on scroll */
.section-2,
.meet-luvon-section,
.how-it-works-section,
.get-started-section {
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

/* Optional: Add scroll snap for a more polished feel */
.title-section,
.section-2,
.meet-luvon-section,
.how-it-works-section,
.get-started-section {
  scroll-snap-align: start;
}

.landing-container {
  scroll-snap-type: y proximity; /* Use 'proximity' for subtle snapping */
}

/* Add Vanta background styles */
.vanta-container {
  position: absolute;
  top: 0vh;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 0;
}

/* Three.js sphere overlay */
.three-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 1;
  pointer-events: none;
  opacity: 0.8;
}

/* Ensure content stays above both backgrounds */
.sticky-navbar {
  position: fixed;
  top: 0;
  height: 5rem;
  width: 100vw;
  background-color: rgba(255, 255, 255, 0.95);
  z-index: 9999;
}

.title-section,
.section-2 {
  position: relative;
  z-index: 2;
  background: transparent;
}

/* Remove the gradient overlay that might be interfering */
.section-2::after {
  display: none;
}

/* Ensure the landing container doesn't cause shifting */
.landing-container {
  position: relative;
  overflow-x: hidden;
}

/* Add styles for the new waitlist section */
.waitlist-section {
  margin: 4rem auto;
}

.waitlist-sidebar {
  .subheading {
    text-align: left;
    color: black;
    z-index: 9999;
  }

  .subtitle {
    text-align: left;
    max-width: 25vw;
    color: black;
    z-index: 99999;
  }
  margin-right: 5vw;
  margin-top: 15vh;
  text-align: left;
  z-index: 99999;
}

/* Add AOS fade-up animation override for smoother animations */
[data-aos="fade-up"] {
  transform: translate3d(0, 30px, 0);
}

[data-aos="fade-right"] {
  transform: translate3d(-30px, 0, 0);
}

[data-aos="fade-left"] {
  transform: translate3d(30px, 0, 0);
}

/* Optional: Add custom animations */
@keyframes floatAnimation {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0);
  }
}

.floating {
  animation: floatAnimation 3s ease-in-out infinite;
}

/* Mobile Responsive Breakpoints */
/* Extra small devices (phones, 600px and down) */
@media only screen and (max-width: 800px) {
  .main-title {
    font-size: 45px;
    max-width: 80vw;
  }

  .subtitle {
    width: 85vw;
    margin-top: 0.5rem;
    font-size: 18px;
  }

  .header-image {
    width: 85vw;
  }

  .subheading {
    max-width: 70vw;
    text-align: center;
    font-size: 35px;
  }

  .meet-luvon-header {
    font-size: 90px;
    font-weight: 500;
    text-align: center;
  }

  .desktop {
    display: none;
  }

  .mobile {
    display: block;
  }

  .meet-luvon-info-img {
    width: 95vw;
    margin-left: auto;
    margin-right: auto;
  }

  .meet-luvon-img-title {
    position: absolute;
    top: 5vh;
    left: 15vw;
    font-size: 25px;
  }

  .meet-luvon-img-subhead {
    position: absolute;
    top: 13vh;
    left: 15vw;
    font-size: 16px;
    max-width: 70vw;
  }

  .meet-luvon-img-actions {
    .book-demo-btn {
      color: white;
    }
    position: absolute;
    top: 36vh;
    left: 15vw;
  }

  .getting-started-card {
    height: 60vh;
  }

  .getting-started-title {
    font-size: 2.5rem;
    width: 80vw;
  }

  .waitlist-section {
    margin: 4rem auto;
  }

  .waitlist-box {
    margin-left: 8%;
    margin-right: auto;
    width: 100%;
  }

  .waitlist-sidebar {
    .subheading {
      text-align: center;
      margin-left: auto;
      margin-right: auto;
    }

    .subtitle {
      text-align: center;
      margin-left: auto;
      margin-right: auto;
      max-width: 90vw;
    }
    margin-right: auto;
    margin-left: auto;
    margin-top: 15vh;
    text-align: center;
  }

  .logo-title {
  display: none;
}
}
/*
.login-signup {
  margin: 1.4rem;
  font-weight: bold;
  text-decoration: none;
  color: white;
  cursor: pointer;
  transition: 0.7s ease-in;
}

.login-signup:hover {
  background: linear-gradient(to bottom right, #00c9ff 0%, #92fe9d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
  */
/* -------------- Container + Orbs -------------- */
/* .landing-container {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow: hidden;
  background-color: #0d0d0d;
}

.landing-container::before {
  content: "";
  position: absolute;
  top: -20%;
  left: -15%;
  width: 700px;
  height: 700px;
  background: radial-gradient(
    circle at center,
    rgba(0, 201, 255, 0.6),
    transparent 70%
  );
  filter: blur(200px);
  z-index: 0;
}
.landing-container::after {
  content: "";
  position: absolute;
  bottom: -20%;
  right: -15%;
  width: 800px;
  height: 800px;
  background: radial-gradient(
    circle at center,
    rgba(146, 254, 157, 0.6),
    transparent 70%
  );
  filter: blur(200px);
  z-index: 0;
} */

/* -------------- Navbar -------------- */
/* .menubar {
  position: relative;
  z-index: 1;
  background: transparent !important;
  border: none;
} */

/* -------------- Page Content -------------- */
/* .landing-page {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.content {
  text-align: center;
  padding: 2rem;
  color: #f2f2f2;
} */

/* -------------- Typography & Badges -------------- */
/* .badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.05);
  color: #aaa;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}
h1 {
  font-family: "Inter", sans-serif;
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0.5rem 0;
}
.subtitle {
  font-size: 1;
  color: #bbb;
  margin: 1rem 0 2rem;
  line-height: 1.6;
}
.highlight {
  color: #00e7a0;
} */

/* -------------- Gradient Text -------------- */
/* .gradientText {
  background: linear-gradient(to bottom right, #00c9ff 0%, #92fe9d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: "Playfair Display", serif;
  font-weight: 700;
} */

/* -------------- Buttons -------------- */

/* -------------- "Get Started" Navbar Button -------------- */
/* .actions .get-started-btn {
  font-size: 0.875rem;
  font-weight: 700;
}

.get-started-btn2 {
  font-size: 0.875rem;
  font-weight: bold;
} */
</style>
