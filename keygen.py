import sys
import os

# Add path to find the controller
# Path: ./ferreteria_refactor/frontend_caja/src
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ferreteria_refactor', 'frontend_caja', 'src')
sys.path.append(src_path)

from controllers.license_controller import LicenseController

def main():
    print("="*60)
    print("GENERADOR DE LICENCIAS - INVENTARIOSOFT")
    print("="*60)
    
    controller = LicenseController()
    
    while True:
        print("\n1. Generar nueva licencia")
        print("2. Resetear Demo (Para pruebas)")
        print("3. Salir")
        
        choice = input("\nOpción: ").strip()
        
        if choice == "1":
            hw_id = input("\nIngrese ID de Hardware del cliente: ").strip()
            if not hw_id:
                print("Error: ID no puede estar vacío")
                continue
                
            try:
                days = int(input("Días de validez (ej. 365): ").strip())
            except:
                print("Error: Días debe ser un número")
                continue
                
            web_enabled = input("¿Incluir Plan Web? (s/n): ").strip().lower() == 's'
            features = ['WEB'] if web_enabled else []
                
            key = controller.generate_key(hw_id, days, features=features)
            print(f"\n✅ LICENCIA GENERADA:\n{key}")
            if web_enabled:
               print("(Incluye acceso al Dashboard Web)")
            print("\nCopie esta clave y envíela al cliente.")
            
        elif choice == "2":
            confirm = input("\n¿Seguro que desea resetear la licencia/demo en ESTA máquina? (s/n): ")
            if confirm.lower() == 's':
                controller.reset_demo()
                print("\n✅ Demo reseteado. Al abrir el programa iniciará un nuevo periodo de prueba.")
                
        elif choice == "3":
            break
            
if __name__ == "__main__":
    main()
