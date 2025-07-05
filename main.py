import cv2
import numpy as np
import os

def analizza_e_modifica_video(percorso_video_input, percorso_video_output, fps_analisi=1, soglia_sottoesposizione=80, soglia_sovraesposizione=180, fattore_correzione=1.2):
    """
    Analizza un video fotogramma per fotogramma per la luminosità e applica semplici correzioni.

    Args:
        percorso_video_input (str): Il percorso del file video di input.
        percorso_video_output (str): Il percorso dove salvare il video modificato.
        fps_analisi (int): Quanti fotogrammi al secondo analizzare.
                          Un valore di 1 significa 1 fotogramma ogni secondo.
        soglia_sottoesposizione (int): Valore di luminosità medio sotto cui un fotogramma è considerato sottoesposto (0-255).
        soglia_sovraesposizione (int): Valore di luminosità medio sopra cui un fotogramma è considerato sovraesposto (0-255).
        fattore_correzione (float): Fattore per aumentare/diminuire la luminosità (es. 1.2 per aumentare, 0.8 per diminuire).
    """

    # Carica il video di input
    cap = cv2.VideoCapture(percorso_video_input)

    if not cap.isOpened():
        print(f"Errore: Impossibile aprire il video al percorso {percorso_video_input}")
        return

    # Ottieni le proprietà del video
    fps = cap.get(cv2.CAP_PROP_FPS)
    larghezza = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altezza = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = cv2.VideoWriter_fourcc(*'mp4v') # Codec per file .mp4

    # Crea l'oggetto VideoWriter per salvare il video modificato
    out = cv2.VideoWriter(percorso_video_output, codec, fps, (larghezza, altezza))

    if not out.isOpened():
        print(f"Errore: Impossibile creare il file video di output al percorso {percorso_video_output}")
        return

    print(f"Inizio analisi e modifica del video: {percorso_video_input}")
    print(f"Salvataggio video modificato in: {percorso_video_output}")
    print(f"Frame rate video originale: {fps} FPS")

    frame_count = 0
    # Calcola ogni quanti fotogrammi analizzare e potenzialmente modificare
    # Ad esempio, se fps_analisi=1 e il video è a 30fps, analizzerà ogni 30 fotogrammi
    frame_interval = int(fps / fps_analisi)
    if frame_interval < 1:
        frame_interval = 1 # Assicurati di analizzare almeno ogni fotogramma se fps_analisi > fps

    while True:
        ret, frame = cap.read()

        # Se non ci sono più fotogrammi, esci dal loop
        if not ret:
            break

        # Seleziona i fotogrammi da analizzare in base a frame_interval
        if frame_count % frame_interval == 0:
            # Converti il fotogramma in scala di grigi per l'analisi della luminosità
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Calcola la luminosità media del fotogramma
            luminosita_media = np.mean(gray_frame)

            correzione_applicata = False
            if luminosita_media < soglia_sottoesposizione:
                # Il fotogramma è sottoesposto, aumenta la luminosità
                print(f"Frame {frame_count}: Sottoesposto (Luminosità media: {luminosita_media:.2f}). Aumento luminosità.")
                # Applica una trasformazione lineare per aumentare la luminosità
                # new_pixel = alpha * old_pixel + beta
                # In questo caso, alpha è il fattore_correzione e beta è 0
                frame = cv2.convertScaleAbs(frame, alpha=fattore_correzione, beta=0)
                correzione_applicata = True
            elif luminosita_media > soglia_sovraesposizione:
                # Il fotogramma è sovraesposto, diminuisci la luminosità
                print(f"Frame {frame_count}: Sovraesposto (Luminosita media: {luminosita_media:.2f}). Diminuisco luminosità.")
                # Applica una trasformazione lineare per diminuire la luminosità
                # Per diminuire, il fattore_correzione deve essere < 1 (es. 1/fattore_correzione per un effetto inverso)
                frame = cv2.convertScaleAbs(frame, alpha=(1/fattore_correzione), beta=0)
                correzione_applicata = True
            # else:
            #     print(f"Frame {frame_count}: Ben esposto (Luminosità media: {luminosita_media:.2f}).")
        
        # Scrivi il fotogramma (originale o modificato) nel video di output
        out.write(frame)
        frame_count += 1

    # Rilascia gli oggetti VideoCapture e VideoWriter
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"\nAnalisi e modifica completate. Video salvato come: {percorso_video_output}")

# --- Esempio di Utilizzo ---
if __name__ == "__main__":
    # Assicurati di avere un file video di test nella stessa directory o specifica il percorso completo
    nome_video_input = "video_originale.mp4" # Sostituisci con il nome del tuo video di input
    nome_video_output = "video_modificato.mp4"

    # Crea un video di esempio se non esiste (utile per i test rapidi)
    if not os.path.exists(nome_video_input):
        print(f"Creazione di un video di esempio '{nome_video_input}'...")
        # Creiamo un video semplice con un colore che varia per simulare esposizioni diverse
        dummy_out = cv2.VideoWriter(nome_video_input, cv2.VideoWriter_fourcc(*'mp4v'), 20, (640, 480))
        if dummy_out.isOpened():
            for i in range(100): # 100 fotogrammi
                # Crea un colore che cambia luminosità nel tempo
                brightness_val = int(abs(np.sin(i * 0.05)) * 255)
                color = (brightness_val, brightness_val, brightness_val) # Scala di grigi per semplicità
                frame = np.full((480, 640, 3), color, dtype=np.uint8)
                dummy_out.write(frame)
            dummy_out.release()
            print(f"Video di esempio '{nome_video_input}' creato con successo.")
        else:
            print(f"Errore: Impossibile creare il video di esempio '{nome_video_input}'. Assicurati che il percorso sia valido e che i codec siano disponibili.")
            exit()

    analizza_e_modifica_video(nome_video_input, nome_video_output, 
                              fps_analisi=5, # Analizza 5 fotogrammi al secondo
                              soglia_sottoesposizione=70, # Considera sottoesposto sotto 70
                              soglia_sovraesposizione=190, # Considera sovraesposto sopra 190
                              fattore_correzione=1.3) # Aumenta/diminuisci la luminosità del 30%