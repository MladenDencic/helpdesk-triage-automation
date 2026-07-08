# Automatizacija Trijaže Tiketa (Helpdesk Triage Automation)

## Opis projekta

Ovaj projekat predstavlja studentski rad na implementaciji mikroservisne arhitekture za automatizaciju korisničke podrške (Helpdesk). Sistem prihvata podatke sa kontakt forme, šalje ih na backend gde veštačka inteligencija (LLM) vrši analizu, kategorizaciju i određivanje prioriteta tiketa, a zatim generiše profesionalni nacrt odgovora. Podaci se trajno čuvaju u lokalnoj JSON bazi, a sistem priprema i HTML notifikaciju za slanje.

Projekat demonstrira:

1. Razdvajanje frontenda i backenda (Separation of Concerns).
2. Integraciju sa naprednim AI modelima preko API-ja.
3. Kontejnerizaciju i orkestraciju aplikacije pomoću Docker-a i Docker Compose-a.
4. Bezbedno upravljanje osetljivim podacima kroz varijable okruženja.

---

## Struktura projekta

Projekat je organizovan u tri nezavisna direktorijuma radi lakšeg održavanja i čistije arhitekture:

```text
triage-app/
│
├── docker-compose.yml         # Glavna orkestracija svih servisa
│
├── frontend/                  # Klijentska strana aplikacije
│   ├── index.html             # HTML5 forma prilagođena dizajnu mejla
│   └── style.css              # Moderni CSS stilovi sa stanjima fokusa
│
├── backend/                   # Serverska strana (Flask API)
│   ├── app.py                 # Glavna Python logika i rute
│   ├── Dockerfile             # Uputstvo za kreiranje slike backend kontejnera
│   ├── requirements.txt       # Python zavisnosti (Flask, Groq, dotenv)
│   └── .env                   # Tajni ključevi i lozinke (ne idu na GitHub!)
│
└── data/                      # Perzistentno skladište podataka
    └── database.json          # Lokalna JSON baza gde se čuvaju tiketi

```

---

## Tehnologije

* **Frontend:** HTML5, CSS3, JavaScript (Fetch API za asinhronu komunikaciju).
* **Backend:** Python 3.11, Flask framework, Flask-CORS (rešavanje cross-origin restrikcija).
* **AI Integracija:** Groq Cloud API (model: `llama-3.3-70b-versatile`) sa strukturisanim JSON izlazom.
* **Deployment & Cloud aspekt:** Docker, Docker Compose, Nginx (kao web server za statički frontend).

---

## Pokretanje projekta (Deployment)

Aplikacija je kompletno kontejnerizovana, što znači da se pokreće jednom komandom na bilo kom operativnom sistemu koji ima instaliran Docker.

### Korak 1: Podešavanje varijabli okruženja

Unutar `backend/` foldera kreirati `.env` fajl na osnovu priloženog `.env.example` šablona i uneti prave podatke:

```text
GROQ_API_KEY=gsk_tvoj_groq_api_ključ
SENDER_EMAIL=tvoj_studentski_ili_test_mejl@gmail.com
SENDER_PASSWORD=tvoja_aplikativna_lozinka_za_izabrani_mejl
RECEIVER_EMAIL=gde_stizu_notifikacije@example.com

```

### Korak 2: Pokretanje preko Docker Compose-a

Pozicionirati se u koren projekta (tamo gde je `docker-compose.yml`) i pokrenuti:

```bash
docker compose up --build

```

Docker će automatski:

1. Preuzeti Nginx i podići frontend na portu `8080`.
2. Pročitati `Dockerfile`, instalirati sve biblioteke i podići Flask backend na portu `5000` (osluškuje na `0.0.0.0` unutar mreže).
3. Kreirati `data/` folder i povezati ga (Volume) kako se podaci ne bi obrisali gašenjem kontejnera.

---

## Korišćenje aplikacije

* **Frontend pristup:** Otvoriti browser i otići na `http://localhost:8080`.
* **Slanje podatka:** Uneti ime, mejl i poruku, pa kliknuti na **Send Data**.
* **Provera baze:** Svaki uspešan tiket se automatski upisuje na kraj fajla `data/database.json` zajedno sa AI analizom (kategorija, prioritet, predložen odgovor).