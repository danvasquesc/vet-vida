import json
import mimetypes
import re
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "vetclinic.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
SEED_PATH = DATABASE_DIR / "seed.sql"
HOST = "127.0.0.1"
PORT = 8000


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        count = conn.execute("SELECT COUNT(*) AS total FROM animals").fetchone()["total"]
        if count == 0 and SEED_PATH.exists():
            conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
        conn.commit()


def row_to_dict(row):
    return dict(row) if row else None


class VetHandler(BaseHTTPRequestHandler):
    server_version = "VetVidaHTTP/1.0"

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} - {format % args}")

    def send_json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def read_json(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length else b"{}"
            return json.loads(raw.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/animals":
            return self.get_animals()
        if path == "/api/services":
            return self.get_services(parse_qs(parsed.query))
        if path == "/api/stats":
            return self.get_stats()

        match = re.fullmatch(r"/api/animals/(\d+)/history", path)
        if match:
            return self.get_animal_history(int(match.group(1)))

        if path.startswith("/api/"):
            return self.send_json({"error": "Rota não encontrada."}, 404)

        return self.serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/animals":
            return self.create_animal()
        if path == "/api/services":
            return self.create_service()
        return self.send_json({"error": "Rota não encontrada."}, 404)

    def get_animals(self):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM animals ORDER BY name COLLATE NOCASE"
            ).fetchall()
        self.send_json([row_to_dict(row) for row in rows])

    def get_services(self, query):
        animal_id = query.get("animal_id", [None])[0]
        sql = """
            SELECT s.*, a.name AS animal_name, a.species AS animal_species
            FROM services s
            JOIN animals a ON a.id = s.animal_id
        """
        params = []
        if animal_id:
            sql += " WHERE s.animal_id = ?"
            params.append(animal_id)
        sql += " ORDER BY s.service_date DESC, s.id DESC"
        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        self.send_json([row_to_dict(row) for row in rows])

    def get_stats(self):
        with get_connection() as conn:
            animals = conn.execute("SELECT COUNT(*) AS total FROM animals").fetchone()["total"]
            services = conn.execute("SELECT COUNT(*) AS total FROM services").fetchone()["total"]
            today = datetime.now().strftime("%Y-%m-%d")
            today_services = conn.execute(
                "SELECT COUNT(*) AS total FROM services WHERE service_date = ?", (today,)
            ).fetchone()["total"]
            revenue = conn.execute(
                "SELECT COALESCE(SUM(price), 0) AS total FROM services"
            ).fetchone()["total"]
        self.send_json({
            "animals": animals,
            "services": services,
            "today_services": today_services,
            "revenue": round(float(revenue or 0), 2),
        })

    def get_animal_history(self, animal_id):
        with get_connection() as conn:
            animal = conn.execute("SELECT * FROM animals WHERE id = ?", (animal_id,)).fetchone()
            if not animal:
                return self.send_json({"error": "Animal não encontrado."}, 404)
            services = conn.execute(
                "SELECT * FROM services WHERE animal_id = ? ORDER BY service_date DESC, id DESC",
                (animal_id,),
            ).fetchall()
        self.send_json({
            "animal": row_to_dict(animal),
            "services": [row_to_dict(row) for row in services],
        })

    def create_animal(self):
        data = self.read_json()
        if data is None:
            return self.send_json({"error": "JSON inválido."}, 400)

        name = str(data.get("name", "")).strip()
        species = str(data.get("species", "")).strip()
        owner_name = str(data.get("owner_name", "")).strip()
        if not name or not species or not owner_name:
            return self.send_json(
                {"error": "Nome do animal, espécie e tutor são obrigatórios."}, 400
            )

        values = (
            name,
            species,
            str(data.get("breed", "")).strip(),
            owner_name,
            str(data.get("owner_phone", "")).strip(),
            str(data.get("birth_date", "")).strip(),
        )
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO animals (name, species, breed, owner_name, owner_phone, birth_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            conn.commit()
            row = conn.execute("SELECT * FROM animals WHERE id = ?", (cursor.lastrowid,)).fetchone()
        self.send_json({"message": "Animal cadastrado com sucesso!", "animal": row_to_dict(row)}, 201)

    def create_service(self):
        data = self.read_json()
        if data is None:
            return self.send_json({"error": "JSON inválido."}, 400)

        try:
            animal_id = int(data.get("animal_id"))
        except (TypeError, ValueError):
            return self.send_json({"error": "Selecione um animal válido."}, 400)

        service_type = str(data.get("service_type", "")).strip()
        service_date = str(data.get("service_date", "")).strip()
        if not service_type or not service_date:
            return self.send_json({"error": "Tipo e data do serviço são obrigatórios."}, 400)

        try:
            price = float(data.get("price") or 0)
        except (TypeError, ValueError):
            return self.send_json({"error": "Valor do serviço inválido."}, 400)

        with get_connection() as conn:
            animal = conn.execute("SELECT id FROM animals WHERE id = ?", (animal_id,)).fetchone()
            if not animal:
                return self.send_json({"error": "Animal não encontrado."}, 404)
            cursor = conn.execute(
                """
                INSERT INTO services
                    (animal_id, service_type, description, service_date, veterinarian, price)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    animal_id,
                    service_type,
                    str(data.get("description", "")).strip(),
                    service_date,
                    str(data.get("veterinarian", "")).strip(),
                    price,
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM services WHERE id = ?", (cursor.lastrowid,)).fetchone()
        self.send_json({"message": "Serviço registrado com sucesso!", "service": row_to_dict(row)}, 201)

    def serve_static(self, path):
        if path in ("", "/"):
            file_path = FRONTEND_DIR / "index.html"
        else:
            relative = path.lstrip("/")
            file_path = (FRONTEND_DIR / relative).resolve()
            try:
                file_path.relative_to(FRONTEND_DIR.resolve())
            except ValueError:
                return self.send_error(403)

        if not file_path.exists() or not file_path.is_file():
            file_path = FRONTEND_DIR / "index.html"

        content = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", (content_type or "application/octet-stream") + ("; charset=utf-8" if (content_type or "").startswith("text/") else ""))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), VetHandler)
    print("=" * 58)
    print(" VetVida - Sistema de Clínica Veterinária")
    print(f" Acesse no navegador: http://{HOST}:{PORT}")
    print(" Para encerrar, pressione CTRL+C")
    print("=" * 58)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
