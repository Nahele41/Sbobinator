# 🎙️ Ultimate Sbobinator Turbo Deluxe 5000

Un'applicazione desktop moderna e potente per la trascrizione automatica di file audio, l'editing rapido e l'esportazione in formati utili.

Sviluppata in Python con **CustomTkinter** per l'interfaccia e **Groq API** (Whisper Large V3) per una velocità di trascrizione senza precedenti.

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)

## ✨ Funzionalità Principali

* **🚀 Velocità Estrema:** Utilizza le LPU di Groq Cloud per trascrivere ore di audio in pochi secondi.
* **✂️ Audio Cutter Integrato:** Visualizza la waveform, taglia l'inizio e la fine dell'audio e trascrivi solo la parte che ti serve.
* **🔄 Smart Chunking:** Gestisce automaticamente file di grandi dimensioni spezzandoli in segmenti sicuri per l'API, aggirando il limite dei 25MB.
* **📚 Libreria Centralizzata:** Tutte le trascrizioni vengono salvate automaticamente nella cartella `Sbobinature`.
* **📄 Export Multiplo:**
    * Esporta in **PDF** formattato.
    * Esporta in **Word (.docx)** editabile.
* **🎨 UI Moderna:** Interfaccia scura, pulita e user-friendly.

## 🛠️ Requisiti

* Python 3.10 o superiore.
* Una chiave API gratuita di [Groq](https://console.groq.com/).
* **FFmpeg** installato e configurato nel sistema (o presente nella cartella `src`).

## 📦 Installazione

1.  **Clona la repository:**
    ```bash
    git clone [https://github.com/tuo-username/Sbobinator.git](https://github.com/tuo-username/Sbobinator.git)
    cd Sbobinator
    ```

2.  **Crea un Virtual Environment (Opzionale ma consigliato):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Se non hai il file requirements.txt, installa manualmente: `customtkinter pydub groq matplotlib fpdf2 python-docx python-dotenv`)*

4.  **Configura FFmpeg:**
    Assicurati che `ffmpeg` e `ffprobe` siano installati nel sistema o copia gli eseguibili dentro la cartella `src/`.

5.  **Configura la Chiave API:**
    Crea un file `.env` nella root del progetto e inserisci la tua chiave:
    ```env
    GROQ_API_KEY=gsk_la_tua_chiave_qui
    ```

## 🚀 Utilizzo

1.  Esegui l'applicazione:
    ```bash
    python src/main.py
    ```
2.  Vai nella scheda **"Nuova Trascrizione"**:
    * Carica un file audio.
    * (Opzionale) Seleziona l'intervallo da trascrivere usando gli slider.
    * Scegli un nome per il file di output.
    * Premi **AVVIA TRASCRIZIONE**.
3.  Vai nella scheda **"Libreria & Export"**:
    * Seleziona la trascrizione appena creata.
    * Esporta in PDF o Word.

## 📂 Struttura del Progetto

* `src/main.py`: Entry point.
* `src/backend.py`: Logica di business, gestione audio e chiamate API (Model).
* `src/utils.py`: Funzioni di supporto (Export PDF/Docx, gestione FFmpeg).
* `src/utils/Sbobinature/`: Cartella di output automatico.
* `src/ui/`: Cartella per la gestione Interfaccia Grafica.

## 📝 Licenza

Questo progetto è distribuito sotto licenza **MIT**. Sentiti libero di usarlo e modificarlo.
