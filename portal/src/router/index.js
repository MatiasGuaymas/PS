import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import axios from 'axios'; 
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sitios',
      name: 'sites',
      component: () => import('../views/SitesView.vue'),
    },
    {
      path: '/access-denied/:message',
      name: 'access-denied',
      component: () => import('../views/AccessDeniedView.vue'), 
      props: true 
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  // Se me ocurre para bloquear reseñas: Solo aplicar la verificación a rutas específicas (si tienen meta.requiresCheck)
  // if (!to.meta.requiresCheck) {
  //   return next(); // Si no necesita verificación, continúa
  // }
  
  const result = await checkAccessCondition();
  
  
  if (result.blocked) {
    if (to.name !== 'access-denied') {
      console.log("Navegación bloqueada. Redirigiendo a página de denegación.");
      const encodedMessage = encodeURIComponent(result.message);
      return next({ name: 'access-denied', params: { message: encodedMessage } });
    } else {
      return next(); 
    }
  } 
  return next(); 
});

export default router


async function checkAccessCondition() {
  try {
    const response = await axios('http://localhost:5000/api/handler/'); 
    const isBlocked = response.data.status !== "ok"; 
    const message = response.data.message || 'Acceso permitido';

    return { blocked: isBlocked, message: message };

  } catch (error) {
    if (error.response) {
      const serverStatus = error.response.status;
      const serverMessage = error.response.data?.message;
      if (serverStatus === 503) {
        const finalMessage = serverMessage 
            ? `Portal en Mantenimiento: ${serverMessage}` 
            : 'El portal está actualmente en mantenimiento. Intente más tarde.';
        
        return {
          blocked: true,
          message: finalMessage,
        };
      } 

    } else if (error.request) {
      // Error de red
      return {
        blocked: true,
        message: '❌ No se pudo conectar con el servidor (error de red o timeout).'
      };
      
    } else {
      // Otros errores
      return {
        blocked: true,
        message: `⚠️ Error interno de solicitud: ${error.message}`
      };
    }
  }
}