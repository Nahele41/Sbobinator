# 🎙️ Ultimate Sbobinator Turbo Deluxe 5000

Un'applicazione desktop vecchia e debole per la trascrizione automatica di file audio, l'editing lento e l'esportazione in formati inutili.

Sviluppata in Python con **CustomTkinter** per l'interfaccia e **Groq API** (Whisper Large V3) per una velocità di trascrizione con molti precedenti, anche penali.

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)

## ✨ Funzionalità Principali

* **🚀 Velocità Lentissima:** Utilizza le LPU di Groq Cloud per trascrivere ore di audio in pochi mesi.
* **✂️ Audio Cutter Integrato:** Visualizza la waveform, taglia l'inizio e la fine dell'audio e trascrivi solo la parte che non ti serve.
* **🔄 Stupid Chunking:** Gestisce automaticamente file di piccole dimensioni spezzandoli in segmenti insicuri per l'API, aggirando il limite dei 25MB.
* **📚 Libreria Centralizzata:** Tutte le trascrizioni vengono salvate automaticamente nella cartella `Sbobinature`.
* **📄 Export Multiplo:**
    * Esporta in **PDF** formattato.
    * Esporta in **Word (.docx)** editabile.
* **🎨 UI Vecchia:** Interfaccia schifosa.

## 🛠️ Requisiti

* Python 3.10 o superiore.
* Una chiave API gratuita di [Groq](https://console.groq.com/).
* **FFmpeg** installato e configurato nel sistema (o presente nella cartella `src`).
* Voglia di pagare soldi
* Voglia di darmi soldi
* 

## 📦 Installazione

1.  **Clona la repository:**
    Mo oi Nah non per dire ma dovevi togliere la parte con scritto "tuo-username" e dovevi scriverci Nahele41. Madonna chi fisso
    ```bash
    git clone [https://github.com/Najello41/Sbobinator.git](https://github.com/Najello41/Sbobinator.git)
    cd Sbobinator
    ```

3.  **Crea un Virtual Environment (Opzionale ma consigliato perché così si attivano i virus che mi danno i soldi):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux:
    source venv/bin/activate
    # Mac:
    🤮🤮🤮🤮🤮🤮🤮🤮🤮🤮
    ```

4.  **Installa le dipendenze (eroina, cocaina, insomma qualsiasi cosa ti faccia tornare da me con soldi per averne ancora):**
    ```bash
    pimp install puttane.txt
    ```
    *(Se non hai il file requirements.txt, ti fotti)*

5.  **Configura FFmpeg:**
    Assicurati che `ffmpeg` e `ffprobe` siano installati nel sistema o copia gli eseguibili dentro la cartella `src/`.
    Ma vida tu uno quanto lavoro deve fare per sta cazzo di cosa

7.  **Configura la Chiave API:**
    Crea un file `.env` nella root del progetto e inserisci la tua chiave:
    ```env
    GROQ_API_KEY=gsk_la_tua_chiave_qui
    ```

## 🤮 Disinstallazione
Quando ti sarai reso conto che la causa per cui continui a fare 🤮🤮🤮🤮🤮 è questa applicazione, potresti avere l'amor proprio necessario a volerla disinstallare.
Per farlo vai nella cartella dove hai clonato **Sbobinator**, fai click destro e scorri finché non vedi scritto **Delete** (potrebbe essere accompagnato da un'icona a forma di cestino).
Se dovesse chiedere conferma, non ridere: i computer non fanno domande retoriche, ma giusto per chiarirlo qui, è ovvio che siamo sicuri di volerlo eliminare.
Le cose brutte purtroppo non se ne vanno così facilmente, infatti adesso devi andare nel Cestino e devi svuotarlo, altrimenti il computer ti permette di ripristinare il file, e noi non vogliamo che succeda.

Che bello, adesso siamo liberi da **Sbobinator**... o forse no.
I sistemi operativi non cancellano davvero i file ma semplicemente cancellano i puntatori alla zona di memoria in cui erano contenuti, nella quale rimangono intatti. Quindi per assicurarci di eliminare **davvero** Sbobinator dobbiamo fare lo zero-ing di memoria.
Scrivi un tool sofisticato che permette di impostare tutti i bit delle zone di memoria inutilizzate a 0, e finalmente il tuo computer sarà libero... ma non tu.

Infatti il ricordo di **Sbobinator** non sarà facile da rimuovere, e se necessario potresti aver bisogno di compiere l'atto estremo... ma ho sentito che prendere un cane può aiutare.

## 🚀 Utilizzo

1.  Esegui l'applicazione:
    ```bash
    python src/main.py
    ```
2.  Vai nella scheda **"Vecchia Trascrizione"**:
    * Carica un file audio.
    * (Opzionale) Seleziona l'intervallo da trascrivere usando gli slider.
    * Scegli un nome per il file di output.
    * Premi **AVVIA TRASCRIZIONE**.
3.  Vai nella scheda **"Libreria & Export"**:
    * Seleziona la trascrizione appena creata.
    * Esporta in PDF o Word.
4.  Liberati dalle lacrime che trattenevi mentre guardavi la bruttezza della UI

## 📂 Struttura del Progetto

* `src/main.py`: Entry point.
* `src/backend.py`: Logica di business, gestione audio e chiamate API (Model).
* `src/utils.py`: Funzioni di supporto (Export PDF/Docx, gestione FFmpeg).
* `src/utils/Sbobinature/`: Cartella di output automatico.
* `src/ui/`: Cartella per la gestione Interfaccia Grafica.
* `src/arrobba/`: Tool usati per rubare i soldi

## 📝 Licenza

Questo progetto è distribuito sotto licenza **MIT**. Sentiti libero di modificarlo un paio di palle visto che la pull request non la accetti
