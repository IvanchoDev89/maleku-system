export default defineEventHandler((event) => {
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://js.stripe.com",
    "worker-src blob:",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "img-src 'self' data: https: blob:",
    "media-src 'self' https:",
    "connect-src 'self' http://localhost:8000 https://api.costaricatravel.dev https://api.stripe.com https://*.sentry.io https://api.cloudinary.com https://res.cloudinary.com",
    "frame-src 'self' https://*.stripe.com https://js.stripe.com",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self' http://localhost:8000 https://*.stripe.com https://api.stripe.com",
    "frame-ancestors 'none'",
  ].join('; ')

  setHeader(event, 'Content-Security-Policy', csp)
})
