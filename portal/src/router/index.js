import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '@/stores/authStore'
import HomeView from '../views/HomeView.vue'
import axios from 'axios'; 
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://grupo21.proyecto2025.linti.unlp.edu.ar';
import { maintenanceState, ensurePortalAvailability } from '@/utils/maintenanceState' 

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
      props: true,
      meta: { bypassMaintenance: true } // Para que no se bloquee a sí misma
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true, bypassMaintenance: true }
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
      meta: { guestOnly: true, bypassMaintenance: true }
    },
    {
      path: '/sitios/:id',
      name: 'site-details',
      component: () => import('../views/SiteDetails.vue'), 
      props: true 
    },
    {
      path: '/reviews/new',
      name: 'new-review',
      component: () => import('../views/ReviewForm.vue'), 
      meta: { requiresAuth: true } // Asumimos que se requiere autenticación para dejar una reseña
    },
    {
      path: '/sitios/:siteId/reviews/:reviewId/edit',
      name: 'edit-review',
      component: () => import('../views/ReviewForm.vue'), 
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
    },
    {
      path: '/favoritos',
      name: 'favoritos',
      component: () => import('../views/FavoritesView.vue'),
      meta: { requiresAuth: true } 
    },
    {
      path: '/reviews',
      name: 'reviews',
      component: () => import('../views/ReviewsView.vue'),
      meta: { requiresAuth: true }
    }
  ],
})


// Hook para la verificación de mantenimiento (corre antes de la autenticación)
router.beforeEach(async (to, from, next) => {
  
  // No verificar mantenimiento si la ruta permite saltarlo (ej: login, access-denied)
  const bypassMaintenance = to.matched.some(record => record.meta.bypassMaintenance)
  
  if (!bypassMaintenance) {
    // Si la aplicación está inactiva, fuerzo el refresh de la flag para ver si ya se levantó.
    const forceRefresh = maintenanceState.isActive 
    await ensurePortalAvailability(forceRefresh)

    if (maintenanceState.isActive) {
      
      // Codifica el mensaje para pasarlo como parámetro de ruta
      const encodedMessage = encodeURIComponent(maintenanceState.message || 'El portal está temporalmente no disponible.')
      
      // Si ya está en access-denied, permite la navegación
      if (to.name === 'access-denied') {
        return next();
      }
      
      // Redirige a la página de acceso denegado con el mensaje
      return next({ name: 'access-denied', params: { message: encodedMessage } });
    }
  }
  
  // Continuar al siguiente `beforeEach` (el de autenticación)
  next()
})


// Hook para la verificación de autenticación (se ejecuta después del de mantenimiento)
router.beforeEach(async (to, from, next) => {
  
  // Lógica de espera si authStore.loading
  if (authStore.loading) {
  
    let attempts = 0
    while (authStore.loading && attempts < 50) {
      await new Promise(resolve => setTimeout(resolve, 100))
      attempts++
    }
  }

  const isAuthenticated = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const guestOnly = to.matched.some(record => record.meta.guestOnly)

  // Si la ruta requiere autenticación y no está autenticado
  if (requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  // Si la ruta es solo para invitados y está autenticado
  if (guestOnly && isAuthenticated) {
    next('/')
    return
  }

  // Permitir navegación
  next()
})

// Hook para la verificación en la resolución final (opcional, para asegurar estado)
router.beforeResolve(async (to, from, next) => {
  // Siempre verifica el estado con refresh justo antes de renderizar la vista, 
  // aunque el cache evite la petición real si ya se hizo recientemente.
  if (!to.matched.some(record => record.meta.bypassMaintenance)) {
     await ensurePortalAvailability(true) // Fuerza la verificación (respetando la promesa en curso)
  }
  next()
})

export default router