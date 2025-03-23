import http.server
import socketserver
import socket
import datetime
import webbrowser
import threading

# Port, auf dem der Server laufen soll
PORT = 8000

# Benutzerdefinierter Handler für Sicherheits-Header und Protokollierung
class SecureHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Sicherheits-Header hinzufügen
        self.send_header("X-Content-Type-Options", "nosniff")  # Verhindert MIME-Type-Sniffing
        self.send_header("X-Frame-Options", "DENY")  # Verhindert Clickjacking
        self.send_header("Content-Security-Policy", "default-src 'self'")  # Erlaubt nur Ressourcen von der eigenen Domain
        super().end_headers()

    def do_GET(self):
        # IP-Adresse des Clients
        client_ip = self.client_address[0]
        
        # Versuche, den Hostnamen des Clients zu ermitteln
        try:
            client_hostname = socket.gethostbyaddr(client_ip)[0]
        except socket.herror:
            client_hostname = "Unbekannt"

        # Aktuelle Zeit für das Protokoll
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Protokolliere den Zugriff
        print(f"[{current_time}] Zugriff von Gerät: IP = {client_ip}, Hostname = {client_hostname}, Pfad = {self.path}")

        # Verhindere Zugriff auf Dateien außerhalb des aktuellen Verzeichnisses
        if ".." in self.path:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden: Access to parent directories is not allowed.")
            return

        super().do_GET()

# Funktion, um die Webseite im Browser zu öffnen
def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")

# Erstelle den Server
Handler = SecureHTTPRequestHandler
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Server läuft auf http://0.0.0.0:{PORT}")
    print("Verbinde dich von einem Gerät im gleichen Netzwerk, z. B. http://192.168.x.x:8000")

    # Starte einen Thread, um die Webseite im Browser zu öffnen
    threading.Thread(target=open_browser, daemon=True).start()

    # Starte den Server und lasse ihn laufen, bis er manuell gestoppt wird
    httpd.serve_forever()