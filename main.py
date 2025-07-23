from interfaz import App
from common_utils import limpiar_logs_antiguos  

if __name__ == "__main__":
    limpiar_logs_antiguos()  
    app = App()
    app.mainloop()
