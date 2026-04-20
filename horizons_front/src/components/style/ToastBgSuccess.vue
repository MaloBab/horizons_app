<template>
  <svg class="absolute inset-0 w-full h-full" viewBox="0 0 320 72" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <radialGradient id="vinyl-groove" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#064e3b"/>
        <stop offset="30%"  stop-color="#065f46"/>
        <stop offset="60%"  stop-color="#047857"/>
        <stop offset="100%" stop-color="#022c22"/>
      </radialGradient>
      <radialGradient id="label-center" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#34d399"/>
        <stop offset="60%"  stop-color="#059669"/>
        <stop offset="100%" stop-color="#064e3b"/>
      </radialGradient>
      <radialGradient id="needle-glow" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#6ee7b7" stop-opacity=".6"/>
        <stop offset="100%" stop-color="#6ee7b7" stop-opacity="0"/>
      </radialGradient>
    </defs>

    <!-- Fond -->
    <rect width="320" height="72" fill="#022c22"/>

    <!-- Lignes de scan horizontales subtiles -->
    <line x1="0" y1="12" x2="320" y2="12" stroke="rgba(52,211,153,.04)" stroke-width="1"/>
    <line x1="0" y1="24" x2="320" y2="24" stroke="rgba(52,211,153,.04)" stroke-width="1"/>
    <line x1="0" y1="36" x2="320" y2="36" stroke="rgba(52,211,153,.04)" stroke-width="1"/>
    <line x1="0" y1="48" x2="320" y2="48" stroke="rgba(52,211,153,.04)" stroke-width="1"/>
    <line x1="0" y1="60" x2="320" y2="60" stroke="rgba(52,211,153,.04)" stroke-width="1"/>

    <!-- Vinyle principal -->
    <g class="vinyl-spin" style="transform-origin: 72px 36px">
      <circle cx="72" cy="36" r="34"  fill="url(#vinyl-groove)"/>
      <!-- Sillons concentriques -->
      <circle cx="72" cy="36" r="32"  fill="none" stroke="rgba(6,95,70,.8)"  stroke-width=".5"/>
      <circle cx="72" cy="36" r="28"  fill="none" stroke="rgba(6,95,70,.7)"  stroke-width=".5"/>
      <circle cx="72" cy="36" r="24"  fill="none" stroke="rgba(5,150,105,.6)" stroke-width=".5"/>
      <circle cx="72" cy="36" r="20"  fill="none" stroke="rgba(5,150,105,.5)" stroke-width=".5"/>
      <circle cx="72" cy="36" r="16"  fill="none" stroke="rgba(4,120,87,.5)"  stroke-width=".5"/>
      <circle cx="72" cy="36" r="12"  fill="none" stroke="rgba(4,120,87,.4)"  stroke-width=".5"/>
      <!-- Étiquette centrale -->
      <circle cx="72" cy="36" r="9"   fill="url(#label-center)"/>
      <circle cx="72" cy="36" r="2.5" fill="rgba(2,44,34,.9)"/>
      <!-- Reflet sur le vinyle -->
      <ellipse cx="60" cy="24" rx="8" ry="4" fill="rgba(110,231,183,.07)" transform="rotate(-30,60,24)"/>
    </g>

    <!-- Bras de lecture -->
    <g class="needle-arm" style="transform-origin: 118px 8px">
      <line x1="118" y1="8" x2="100" y2="44" stroke="rgba(167,243,208,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="118" cy="8" r="3" fill="rgba(167,243,208,.4)" stroke="rgba(167,243,208,.6)" stroke-width=".8"/>
      <!-- Tête de lecture -->
      <rect x="96" y="43" width="8" height="4" rx="1" fill="rgba(52,211,153,.5)" stroke="rgba(110,231,183,.4)" stroke-width=".5"/>
    </g>
    <!-- Halo de lecture -->
    <ellipse cx="100" cy="45" rx="12" ry="6" fill="url(#needle-glow)"/>

    <!-- Onde sonore émanant du vinyle -->
    <g class="sound-wave" style="transform-origin: 72px 36px">
      <circle cx="72" cy="36" r="38" fill="none" stroke="rgba(52,211,153,.25)" stroke-width="1.2"/>
      <circle cx="72" cy="36" r="44" fill="none" stroke="rgba(52,211,153,.15)" stroke-width="1"/>
      <circle cx="72" cy="36" r="50" fill="none" stroke="rgba(52,211,153,.08)" stroke-width=".8"/>
    </g>

    <!-- Égaliseur à droite -->
    <g class="eq-bars" style="transform-origin: 200px 54px">
      <rect class="eq eq1" x="170" y="40" width="4" height="22" rx="2" fill="rgba(52,211,153,.6)" style="transform-origin:172px 62px"/>
      <rect class="eq eq2" x="178" y="44" width="4" height="18" rx="2" fill="rgba(16,185,129,.55)" style="transform-origin:180px 62px"/>
      <rect class="eq eq3" x="186" y="38" width="4" height="24" rx="2" fill="rgba(52,211,153,.65)" style="transform-origin:188px 62px"/>
      <rect class="eq eq4" x="194" y="46" width="4" height="16" rx="2" fill="rgba(5,150,105,.5)"  style="transform-origin:196px 62px"/>
      <rect class="eq eq5" x="202" y="42" width="4" height="20" rx="2" fill="rgba(52,211,153,.6)" style="transform-origin:204px 62px"/>
      <rect class="eq eq6" x="210" y="36" width="4" height="26" rx="2" fill="rgba(16,185,129,.55)" style="transform-origin:212px 62px"/>
      <rect class="eq eq7" x="218" y="44" width="4" height="18" rx="2" fill="rgba(52,211,153,.5)" style="transform-origin:220px 62px"/>
    </g>

    
    <line x1="244" y1="33" x2="306" y2="33" stroke="rgba(52,211,153,.1)" stroke-width=".5"/>
    <rect x="244" y="36" width="44" height="2" rx="1" fill="rgba(52,211,153,.12)"/>
    <rect x="244" y="41" width="62" height="2" rx="1" fill="rgba(52,211,153,.08)"/>
    <rect x="244" y="46" width="34" height="2" rx="1" fill="rgba(52,211,153,.06)"/>

    <!-- Barre de progression lecture -->
    <rect x="244" y="54" width="66" height="1.5" rx=".75" fill="rgba(52,211,153,.15)"/>
    <rect x="244" y="54" width="28" height="1.5" rx=".75" fill="rgba(52,211,153,.5)"/>
    <circle cx="272" cy="54.75" r="2.5" fill="rgba(110,231,183,.7)"/>
  </svg>
</template>

<style scoped>
.vinyl-spin {
  animation: spin 4s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.needle-arm {
  animation: needleBob 4s ease-in-out infinite;
}
@keyframes needleBob {
  0%, 100% { transform: rotate(0deg);   }
  50%       { transform: rotate(2.5deg); }
}

.sound-wave {
  animation: wavePulse 2s ease-out infinite;
}
@keyframes wavePulse {
  0%   { transform: scale(1);    opacity: 1; }
  100% { transform: scale(1.15); opacity: 0; }
}

.eq { animation: eqBounce 1.8s ease-in-out infinite; }
.eq1 { animation-delay: 0.00s; }
.eq2 { animation-delay: 0.25s; }
.eq3 { animation-delay: 0.50s; }
.eq4 { animation-delay: 0.75s; }
.eq5 { animation-delay: 0.15s; }
.eq6 { animation-delay: 0.40s; }
.eq7 { animation-delay: 0.65s; }
@keyframes eqBounce {
  0%, 100% { transform: scaleY(0.3); }
  50%       { transform: scaleY(1);   }
}
</style>