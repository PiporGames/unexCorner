from random import Random
from time import sleep
import tkinter as tk
from PIL import Image, ImageTk
import requests
import threading
import argparse
# --------------------------------------------
# Salvapantallas de la UEX
#   Cada choque con los bordes es otra alma perdida (TM)
# --------------------------------------------

# Configurar argumentos de línea de comandos
parser = argparse.ArgumentParser(description='UEX Screensaver')
parser.add_argument('--step', type=int, default=5, help='Step size for movement')
parser.add_argument('--queue', type=int, default=5, help='Maximum queue size for images')
parser.add_argument('--min', type=int, default=2278300, help='Minimum userid for random generation')
parser.add_argument('--max', type=int, default=2278600, help='Maximum userid for random generation')
args = parser.parse_args()

isRunning = True
directionX = True
directionY = True
stepSize = args.step
queueSize = args.queue
minUserid = args.min
maxUserid = args.max
imageQueue : list = []

# Crear ventana principal
root = tk.Tk()
monitorWidth = root.winfo_screenwidth()
monitorHeight = root.winfo_screenheight()
windowWidth = 200
windowHeight = 200
root.geometry(f"{windowWidth}x{windowHeight}")
root.overrideredirect(True)  # Sin bordes
root.attributes("-topmost", True)  # Siempre encima

# Establecer fondo amarillo
img = Image.new("RGB", (windowWidth, windowHeight), (255, 255, 0))
bg = ImageTk.PhotoImage(img)
label = tk.Label(root, image = bg)
label.place(x = -2, y = -2)

# centrar ventana
root.eval('tk::PlaceWindow . center')
x = root.winfo_x()
y = root.winfo_y()


def loop():

    while True:
        nextStep()
        sleep(0.016) # Aproximadamente 60 FPS
    

def nextStep():
    global directionX, directionY, x, y, root
    
    if (x >= monitorWidth) or (x >= monitorWidth - windowWidth):
        directionX = False
        changeImage()
    elif (x <= 0) or (x <= 0 - windowWidth):
        directionX = True
        changeImage()
    if (y <= 0) or (y <= 0 - windowHeight):
        directionY = True
        changeImage()
    elif (y >= monitorHeight) or (y >= monitorHeight - windowHeight):
        directionY = False
        changeImage()
        
    if directionX:
        x += stepSize
    else:
        x -= stepSize
    if directionY:
        y += stepSize
    else:
        y -= stepSize
        
    # Mover ventana
    root.geometry(f"+{x}+{y}")

def changeImage():
    global imageQueue
    if len(imageQueue) > 0:
        nextImage = imageQueue.pop(0)
        label.configure(image=nextImage)
        label.image = nextImage  # Mantener referencia para evitar recolección de basura
        
def fetchImage():
    global imageQueue

    while True:
        while len(imageQueue) >= queueSize:
            sleep(1)
        
        rnd = Random()
        userid = rnd.randint(minUserid, maxUserid)
        url = f"https://campusvirtual.unex.es/zonauex/avuex/pluginfile.php/{userid}/user/icon/"
        try:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            }
            req = requests.get(url, headers=headers, stream=True)
            if req.status_code == 200:
                img: Image = Image.open(req.raw)
                img = img.resize((windowWidth, windowHeight))
                imageQueue.append(ImageTk.PhotoImage(img))
                
                print(f"fetched image from {userid}")
            else:
                print(f"fetch for {userid} returned {req.status_code}")
        except Exception as e:
            print(f"Error fetching image: {e}")
        sleep(0.2)  # Wait
    
    

# Lanzar thread del loop
thread = threading.Thread(target=loop, daemon=True).start()
# Lanzar thread del fetchImage
thread = threading.Thread(target=fetchImage, daemon=True).start()
# Inciciar ventana
root.mainloop()