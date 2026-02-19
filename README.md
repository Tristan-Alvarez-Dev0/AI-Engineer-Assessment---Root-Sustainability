# Root Sustainability – AI Engineer Technical Assessment

Hey there 👋

First off, we put together this assignment especially for this interview, so if you think things
are unclear, don't hesitate to ask us questions.

This assessment represents a slice of the address matching problem we face at Root Sustainability.
Users input addresses into the tool, which need to be mapped to a coordinates for impact calculations.
In order to do so, we adopt an external API (Mapbox) to geocode the results. However, after geo-coding,
we want to give our users the possibility to review the accuracy of the match we've found. Therefore,
we want to develop a similarity score between the input address and the matched address, to support a 
human review process. By surfacing addresses that have high impact on the total company carbon footprint 
and have a low similarity score, we can support our users in only having to check the most problematic 
addresses, instead of having to review what could be hundreds of thousands of addresses.

You will extend a backend that:

- Talks to the **Mapbox** geocoding API to find candidate address matches
- Computes a **similarity score** between the original address and the best matched address
- Exposes a small HTTP API that the provided React frontend consumes

The repository is organized as:

- `frontend/` – React app (Vite + TypeScript) to visualise and manage addresses
- `backend/` – FastAPI starter backend that you will extend
- `data/` – Test data to validate your solution
- `README.md` – this file

---

## 1. Assessment goals

This assignment is not about building the perfect model. 
It's about showing how you reason about an applied AI problem and translate that reasoning into working software.

You will:

1. Build an **address similarity function** returning a score between `0.0` and `1.0`
2. Do some **experimentation** and document your reasoning
3. **Integrate** your solution into the existing frontend/backend setup

Approximate time budget: **2–3 hours**, if you run out of time, focus on 2.1/2.2

---

## 2. Assignment

### 2.1 Wire up Mapbox properly

- Get and configure a Mapbox access token  
  (Mapbox requires a credit card even for the free tier; if you prefer not to, contact us and we’ll provide a token.)
- Explore the API and decide how to select the “best” match based on any user input
- Implement your solution in `backend/mapbox_client.py`

---

### 2.2 Research and improve the address similarity function

We have provided a baseline implementation of the address similarity function in `backend/similarity.py`.

The address similarity function should:

- Return a value in `[0.0, 1.0]`
- Represent whether two addresses likely point to the same real-world entity
- Be reasonably robust to:
    - Language differences
    - Spelling variations
    - Capitalization
    - Formatting differences

We would like you to:

- Explore multiple approaches qualitatively
- Pick one final approach, explain why, and implement it in `backend/similarity.py`
- Document what you tried, what you chose, and what you would explore next in **`EXPERIMENTS.md`**

If you want, you can compare your results quantitatively using the dataset in `data/addresses.csv` which gives 
an idea, but not a guarantee, of how good your solution is. We care more about your reasoning than about your 
score versus this baseline.

---

### 2.3 Polish & explore

If you have time left, feel free to:

- Do some API or code polishing
- Play with your solution via the frontend

Pay attention to how the system behaves in practice:

- Latency, failures, or confusing behaviour
- Ambiguous input or over-confident scores

We’ll discuss any limitations you might have noticed during the interview.

---

## 3. Backend (FastAPI starter)

A minimal FastAPI backend starter is provided in `backend/`. It includes:

- Data models for addresses
- An SQLite database and SQLAlchemy ORM model
- Endpoint skeletons matching the contract below
- A naive Mapbox integration and similarity baseline

### 3.1 Data model

An address record has the following shape:

```json
{
  "id": 1,
  "address": "Parijs, Frankrijk",
  "matched_address": "Paris, France",
  "match_score": 0.98
}
```

Where:

- `address` – raw input address as entered by a user
- `matched_address` – the best match returned by Mapbox
- `match_score` – a float in `[0, 1]` indicating how likely these refer to the same real-world entity  
  (`1.0` = clearly the same, `0.0` = clearly not)

---

### 3.2 API contract

Your backend should implement the following endpoints:

1. **List all addresses**
    - `GET /addresses`
    - Response: `200 OK` with `Address[]`

2. **Create an address**
    - `POST /addresses`
    - Body:
      ```json
      {
        "address": "string"
      }
      ```
    - Behaviour:
        - Call Mapbox to find the best match
        - Calculate a similarity score
        - Store the record
        - Return `201 Created` (or `200 OK`) with the full `Address` object

3. **Get a single address**
    - `GET /addresses/{id}`
    - Response: `200 OK` with `Address`
    - `404` if not found

4. **Update an address**
    - `POST /addresses/{id}`
    - Body:
      ```json
      {
        "address": "string"
      }
      ```
    - Behaviour:
        - Recalculate Mapbox match and similarity score
        - Store the updated record
        - Return `201 Created` (or `200 OK`) with the full `Address` object

5. **Refresh scores of one or more addresses**
    - `POST /addresses/refresh`
    - Body:
      ```json
      {
        "ids": [1, 2, 3]
      }
      ```
    - Behaviour:
        - Recalculate matches and scores
        - If `ids` is `null`, refresh all records
        - Return `200 OK`

---

### 3.3 Running the backend

From the repository root:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API:

- http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 4. Frontend (React)

A small React + TypeScript frontend is provided in `frontend/`. It allows you to:

- View all addresses in a table
- Select rows via checkboxes
- Add a new address
- Inspect a single address in detail and update it
- Refresh scores for selected or all addresses

### 4.1 Running the frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 5. Deliverables

Send us a link to a Git repository on the day before your interview containing:

1. Your implementation
2. Any notebooks or extra scripts used during experimentation
3. Your **`EXPERIMENTS.md`**

---

Good luck! 🔥
