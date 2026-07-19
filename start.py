import subprocess
import sys
import time
import os
from pathlib import Path


BASE_DIR = Path(__file__).parent


def iniciar_api():

    print("🚀 Iniciando API...")

    return subprocess.Popen(
        [sys.executable, "-m", "api.api"],
        cwd=BASE_DIR
    )


def iniciar_whatsapp():

    print("🚀 Iniciando WhatsApp...")

    return subprocess.Popen(
        ["node", "whatsapp/index.js"],
        cwd=BASE_DIR
    )


def main():

    print("=" * 50)
    print("            NexusBridge")
    print("=" * 50)

    api = iniciar_api()

    # Espera a API subir antes do Node começar
    time.sleep(3)

    whatsapp = iniciar_whatsapp()

    print("\n✅ NexusBridge iniciado.\n")
    print("Pressione CTRL+C para encerrar.\n")

    try:

        while True:

            time.sleep(1)

            # Se algum processo morrer, avisa e encerra tudo
            if api.poll() is not None:

                print("❌ A API foi encerrada.")
                break

            if whatsapp.poll() is not None:

                print("❌ O WhatsApp foi encerrado.")
                break

    except KeyboardInterrupt:

        print("\n🛑 Encerrando NexusBridge...")

    finally:

        if api.poll() is None:
            api.terminate()

        if whatsapp.poll() is None:
            whatsapp.terminate()

        print("✅ NexusBridge encerrado.")


if __name__ == "__main__":
    main()