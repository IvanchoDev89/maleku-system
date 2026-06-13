#!/usr/bin/env python3
"""Servidor de desarrollo simple para Costa Rica Travel"""

import os
import subprocess

PORT = 3002
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))


def kill_existing_servers():
    """Matar servidores existentes en puertos conflictivos"""
    os.system("pkill -9 -f 'node.*3000' 2>/dev/null")
    os.system("pkill -9 -f 'nuxt.*3000' 2>/dev/null")
    os.system("fuser -k 3000/tcp 2>/dev/null")
    print("✅ Servidores anteriores detenidos")


def rebuild_css():
    """Recompilar CSS de Tailwind"""
    print("🎨 Recompilando CSS...")
    result = subprocess.run(
        [
            "npx",
            "tailwindcss",
            "-i",
            "./assets/css/main.css",
            "-o",
            "./public/css/tailwind.css",
            "--minify",
        ],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("✅ CSS recompilado")
    else:
        print(f"⚠️  Error CSS: {result.stderr}")


def start_nuxt():
    """Iniciar Nuxt en modo desarrollo"""
    print(f"🚀 Iniciando Nuxt en http://localhost:{PORT}")
    os.chdir(FRONTEND_DIR)
    os.system(f"PORT={PORT} npm run dev")


if __name__ == "__main__":
    print("=" * 50)
    print("Costa Rica Travel - Development Server")
    print("=" * 50)

    kill_existing_servers()
    rebuild_css()
    start_nuxt()
