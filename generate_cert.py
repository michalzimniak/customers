"""
Skrypt do generowania self-signed certyfikatu SSL dla lokalnej sieci
"""
from OpenSSL import crypto
import os

def generate_self_signed_cert():
    """Generuje self-signed certyfikat SSL"""
    
    # Tworzenie klucza
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # Tworzenie certyfikatu
    cert = crypto.X509()
    cert.get_subject().C = "PL"
    cert.get_subject().ST = "Poland"
    cert.get_subject().L = "Warsaw"
    cert.get_subject().O = "Customer Registry"
    cert.get_subject().OU = "IT"
    cert.get_subject().CN = "localhost"
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Ważny przez rok
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # Zapisywanie certyfikatu
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    # Zapisywanie klucza
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print("✓ Wygenerowano cert.pem i key.pem")
    print("✓ Certyfikat ważny przez 1 rok")
    print("\nUWAGA: To jest self-signed certyfikat.")
    print("Przeglądarka wyświetli ostrzeżenie o bezpieczeństwie.")
    print("Należy je zaakceptować aby korzystać z aplikacji.")

if __name__ == "__main__":
    generate_self_signed_cert()
