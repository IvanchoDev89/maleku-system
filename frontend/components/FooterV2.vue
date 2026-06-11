<template>
  <footer class="bg-gray-900 text-white">
    <!-- Main Footer -->
    <div class="container mx-auto px-4 py-16">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
        <!-- Brand -->
        <div>
          <div class="flex items-center gap-3 mb-6">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-emerald-600 rounded-xl flex items-center justify-center">
              <span class="text-2xl">🌴</span>
            </div>
            <div>
              <span class="text-xl font-bold text-white">Costa Rica Travel</span>
              <p class="text-xs text-gray-400">Tu aventura te espera</p>
            </div>
          </div>
          <p class="text-gray-400 leading-relaxed">
            Tu agencia de viajes especializada en experiencias únicas por Costa Rica. Descubre playas, volcanes y selvas tropicales.
          </p>
          <div class="flex gap-4 mt-6">
            <a href="#" class="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.3 3.423-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
            </a>
            <a href="#" class="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            </a>
            <a href="#" class="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/></svg>
            </a>
          </div>
        </div>
        
        <!-- Destinations -->
        <div>
          <h4 class="text-white font-bold text-lg mb-4">Destinos Populares</h4>
          <ul class="space-y-3">
            <li><NuxtLink to="/destinos/guanacaste" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><MapPin class="w-4 h-4" /> Guanacaste</NuxtLink></li>
            <li><NuxtLink to="/destinos/la-fortuna" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><MapPin class="w-4 h-4" /> La Fortuna</NuxtLink></li>
            <li><NuxtLink to="/destinos/monteverde" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><MapPin class="w-4 h-4" /> Monteverde</NuxtLink></li>
            <li><NuxtLink to="/destinos/manuel-antonio" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><MapPin class="w-4 h-4" /> Manuel Antonio</NuxtLink></li>
            <li><NuxtLink to="/destinos" class="text-primary-400 hover:text-primary-300 transition-colors font-medium flex items-center gap-2 mt-2"><ArrowRight class="w-4 h-4" /> Ver todos</NuxtLink></li>
          </ul>
        </div>
        
        <!-- Services -->
        <div>
          <h4 class="text-white font-bold text-lg mb-4">Servicios</h4>
          <ul class="space-y-3">
            <li><NuxtLink to="/tours" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><Compass class="w-4 h-4" /> Tours Guiados</NuxtLink></li>
            <li><NuxtLink to="/hoteles" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><Building2 class="w-4 h-4" /> Hoteles</NuxtLink></li>
            <li><NuxtLink to="/paquetes" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><Package class="w-4 h-4" /> Paquetes</NuxtLink></li>
            <li><NuxtLink to="/planificador" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><FileText class="w-4 h-4" /> Planificador</NuxtLink></li>
            <li><NuxtLink to="/transfers" class="text-gray-400 hover:text-primary-400 transition-colors flex items-center gap-2"><Car class="w-4 h-4" /> Transfers</NuxtLink></li>
          </ul>
        </div>
        
        <!-- Contact -->
        <div>
          <h4 class="text-white font-bold text-lg mb-4">Contacto</h4>
          <ul class="space-y-4">
            <li class="flex items-start gap-3">
              <div class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                <Phone class="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <p class="text-gray-500 text-sm">Teléfono</p>
                <p class="text-white font-medium">+506 8000-0000</p>
              </div>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                <Mail class="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <p class="text-gray-500 text-sm">Email</p>
                <p class="text-white font-medium">info@costaricatravel.dev</p>
              </div>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                <MapPin class="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <p class="text-gray-500 text-sm">Dirección</p>
                <p class="text-white font-medium">San José, Costa Rica</p>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- Bottom Bar -->
    <div class="border-t border-gray-800">
      <div class="container mx-auto px-4 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="flex items-center gap-2">
          <p class="text-gray-500 text-sm">© {{ new Date().getFullYear() }} Costa Rica Travel. Todos los derechos reservados.</p>
        </div>
        <div class="flex gap-6 text-sm">
          <NuxtLink to="/terminos" class="text-gray-400 hover:text-primary-400 transition-colors">Términos</NuxtLink>
          <NuxtLink to="/privacidad" class="text-gray-400 hover:text-primary-400 transition-colors">Privacidad</NuxtLink>
          <NuxtLink to="/contacto" class="text-gray-400 hover:text-primary-400 transition-colors">Contacto</NuxtLink>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { MapPin, Building2, Compass, FileText, Package, Car, Phone, Mail, ArrowRight } from 'lucide-vue-next'
</script>