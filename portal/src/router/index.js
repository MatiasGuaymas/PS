import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '@/stores/authStore'
import HomeView from '../views/HomeView.vue'
import axios from 'axios'; 
const API_BASE_URL = import.meta.env.VITE_API_URL;
const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_API_URL),
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
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/perfil',
      name: 'perfil',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true } 
    },
    {
      path: '/registro',
      name: 'registro',
      component: () => import('../views/RegisterView.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/sitios/:id',
      name: 'site-details',
      component: () => import('../views/SiteDetails.vue'), 
      props: true 
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'), // O crear una vista 404
    },
  ],
})

// router.beforeEach(async (to, from, next) => {
//   // Se me ocurre para bloquear reseñas: Solo aplicar la verificación a rutas específicas (si tienen meta.requiresCheck)
//   // if (!to.meta.requiresCheck) {
//   //   return next(); // Si no necesita verificación, continúa
//   // }
  
//   const result = await checkAccessCondition();
  
  
//   if (result.blocked) {
//     if (to.name !== 'access-denied') {
//       console.log("Navegación bloqueada. Redirigiendo a página de denegación.");
//       const encodedMessage = encodeURIComponent(result.message);
//       return next({ name: 'access-denied', params: { message: encodedMessage } });
//     } else {
//       return next(); 
//     }
//   } 
//   return next(); 
// });

router.beforeEach(async (to, from, next) => {
  console.log(`🧭 Navegando a: ${to.path}`)
  
  if (authStore.loading) {
    console.log('⏳ Esperando verificación de autenticación...')
  
    let attempts = 0
    while (authStore.loading && attempts < 50) {
      await new Promise(resolve => setTimeout(resolve, 100))
      attempts++
    }
  }

  const isAuthenticated = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const guestOnly = to.matched.some(record => record.meta.guestOnly)

  // console.log(`🔐 isAuthenticated: ${isAuthenticated}`)
  // console.log(`🛡️ requiresAuth: ${requiresAuth}`)
  // console.log(`👤 guestOnly: ${guestOnly}`)

  // ✅ Si la ruta requiere autenticación y no está autenticado
  if (requiresAuth && !isAuthenticated) {
    console.log('❌ Acceso denegado, redirigiendo a /login')
    next('/login')
    return
  }

  // ✅ Si la ruta es solo para invitados y está autenticado
  if (guestOnly && isAuthenticated) {
    // console.log('✅ Usuario ya autenticado, redirigiendo a /')
    next('/')
    return
  }

  // ✅ Permitir navegación
  // console.log('✅ Navegación permitida')
  next()
})

export default router


async function checkAccessCondition() {
  try {
    const response = await axios(`${API_BASE_URL}/api/handler/`); 
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