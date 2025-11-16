<template>
  <div class="not-found-view">
    <div class="container text-center py-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <h1 class="display-1 text-danger mb-4">Error 404</h1>
          <h2 class="mb-4">Página no encontrada</h2>
          <p class="lead mb-4">
            Lo sentimos, la página que estás buscando no existe o ha sido movida.
          </p>
          
          <div class="error-image-container mb-4">
            <img 
              src="/error404.png" 
              alt="Error 404"
              class="error-image"
            >
          </div>
        
          <div class="suggestions mb-4">
            <p class="text-muted">Tal vez quieras:</p>
            <div class="d-flex flex-wrap gap-2 justify-content-center">
              <router-link to="/" class="btn btn-primary">
                <i class="bi bi-house-door me-2"></i>
                Volver al inicio
              </router-link>
              <router-link to="/sitios" class="btn btn-outline-primary">
                <i class="bi bi-building me-2"></i>
                Ver sitios históricos
              </router-link>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-view {
  min-height: calc(100vh - 200px);
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 3rem 0;
}

.display-1 {
  font-size: 8rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  font-weight: 600;
  color: #495057;
}

.lead {
  font-size: 1.25rem;
  color: #6c757d;
}

.error-image-container {
  margin: 2rem auto;
}

.error-image {
  max-width: 300px;
  width: 100%;
  height: auto;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.suggestions p {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.btn {
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-outline-primary {
  border: 2px solid #667eea;
  color: #667eea;
}

.btn-outline-primary:hover {
  background-color: #667eea;
  border-color: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.alert {
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

/* Responsive */
@media (max-width: 768px) {
  .display-1 {
    font-size: 5rem;
  }
  
  .error-image {
    max-width: 200px;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  .lead {
    font-size: 1rem;
  }
  
  .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .d-flex {
    flex-direction: column;
  }
}
</style>