#!/bin/bash
cd /home/marcelo/Documents/costaricatravel.dev/frontend
pkill -9 -f "nuxt|node" 2>/dev/null
sleep 2
rm -rf .nuxt
npx tailwindcss -i ./assets/css/main.css -o ./public/css/tailwind.css --minify
PORT=3003 npm run dev
