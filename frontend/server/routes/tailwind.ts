import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler((event) => {
  const cssPath = path.resolve('./.output/public/_nuxt/tailwind-full.css')
  const css = fs.readFileSync(cssPath, 'utf-8')

  setHeader(event, 'Content-Type', 'text/css')
  return css
})
