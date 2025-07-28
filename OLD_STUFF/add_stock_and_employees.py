#!/usr/bin/env python3
# add_stock_and_employees.py
# Script pour ajouter du stock de téléphones, de nouveaux salariés et les affecter

import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import random
from datetime import datetime, date, timedelta

# Load environment variables
load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL."""
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        print("✅ Connexion à la base de données établie.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def add_phone_stock(cursor):
    """Ajoute du stock de téléphones à la base de données."""
    print("\n📱 Ajout du stock de téléphones...")
    
    # Différents modèles de téléphones
    phone_models = [
        ("Samsung", "Galaxy S23", "SM-S911F"),
        ("Samsung", "Galaxy A54", "SM-A546B"),
        ("Apple", "iPhone 14", "A2884"),
        ("Apple", "iPhone 13", "A2633"),
        ("Samsung", "Galaxy S22", "SM-S901B"),
        ("Apple", "iPhone 12", "A2172"),
        ("Samsung", "Galaxy A34", "SM-A346B"),
        ("Apple", "iPhone SE", "A2296"),
        ("Samsung", "Galaxy A24", "SM-A245F"),
        ("Apple", "iPhone 14 Plus", "A2886")
    ]
    
    phones_added = 0
    
    for i in range(50):  # Ajouter 50 téléphones
        manufacturer, model, model_code = random.choice(phone_models)
        
        # Générer des données uniques
        asset_tag = f"PHONE-{2024}{i+1:03d}"
        imei = f"3500000{i+1:08d}"  # IMEI fictif mais valide
        serial_number = f"SN{manufacturer[:2].upper()}{i+1:06d}"
        
        purchase_date = date.today() - timedelta(days=random.randint(30, 365))
        warranty_end_date = purchase_date + timedelta(days=730)  # 2 ans de garantie
        
        phone_query = """
            INSERT INTO phones (asset_tag, imei, serial_number, manufacturer, model, 
                              purchase_date, warranty_end_date, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asset_tag) DO NOTHING
            RETURNING id;
        """
        
        try:
            cursor.execute(phone_query, (
                asset_tag, imei, serial_number, manufacturer, model,
                purchase_date, warranty_end_date, "In Stock", 
                f"Téléphone {manufacturer} {model} ajouté au stock"
            ))
            
            result = cursor.fetchone()
            if result:
                phones_added += 1
                print(f"   ✅ Ajouté: {manufacturer} {model} (Asset: {asset_tag})")
        
        except psycopg2.IntegrityError as e:
            print(f"   ⚠️  Téléphone {asset_tag} déjà existant, ignoré.")
            continue
    
    print(f"📱 {phones_added} téléphones ajoutés au stock.")

def add_sim_cards(cursor):
    """Ajoute des cartes SIM à la base de données."""
    print("\n📡 Ajout des cartes SIM...")
    
    carriers = ["Orange", "SFR", "Bouygues Telecom", "Free Mobile"]
    sims_added = 0
    
    for i in range(60):  # Ajouter 60 cartes SIM
        iccid = f"8933100000000{i+1:07d}"  # ICCID fictif
        carrier = random.choice(carriers)
        
        sim_query = """
            INSERT INTO sim_cards (iccid, carrier, plan_details, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (iccid) DO NOTHING
            RETURNING id;
        """
        
        try:
            cursor.execute(sim_query, (
                iccid, carrier, f"Plan professionnel {carrier}", "Available"
            ))
            
            result = cursor.fetchone()
            if result:
                sim_id = result['id']
                sims_added += 1
                
                # Ajouter un numéro de téléphone pour cette SIM
                phone_number = f"0{random.randint(6, 7)}{random.randint(10000000, 99999999)}"
                
                phone_number_query = """
                    INSERT INTO phone_numbers (phone_number, sim_card_id, status)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (phone_number) DO NOTHING;
                """
                
                cursor.execute(phone_number_query, (phone_number, sim_id, "Active"))
                print(f"   ✅ Ajouté: SIM {carrier} - {phone_number}")
        
        except psycopg2.IntegrityError:
            continue
    
    print(f"📡 {sims_added} cartes SIM ajoutées.")

def add_employees(cursor):
    """Ajoute de nouveaux salariés à la base de données."""
    print("\n👥 Ajout de nouveaux salariés...")
    
    # Récupérer les secteurs existants
    cursor.execute("SELECT id, secteur_name FROM secteurs ORDER BY id;")
    secteurs = cursor.fetchall()
    
    if not secteurs:
        print("❌ Aucun secteur trouvé. Veuillez d'abord créer des secteurs.")
        return 0
    
    # Noms fictifs pour les salariés
    prenoms = ["Pierre", "Marie", "Jean", "Sophie", "Paul", "Claire", "Michel", "Anne", 
               "François", "Isabelle", "Nicolas", "Catherine", "David", "Nathalie", "Philippe",
               "Sylvie", "Laurent", "Christine", "Pascal", "Françoise", "Thierry", "Martine",
               "Bernard", "Monique", "Alain", "Brigitte", "Stéphane", "Véronique", "Olivier",
               "Chantal", "Julien", "Patricia", "Sébastien", "Corinne", "Eric", "Sandrine"]
    
    noms = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand", "Leroy",
            "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David", "Bertrand",
            "Roux", "Vincent", "Fournier", "Morel", "Andre", "Mercier", "Blanc", "Guerin",
            "Boyer", "Girard", "Barbier", "Arnaud", "Martinez", "Gerard", "Dupont", "Lambert",
            "Bonnet", "Francois", "Martinez", "Legrand"]
    
    employees_added = 0
    
    for i in range(30):  # Ajouter 30 nouveaux salariés
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        full_name = f"{prenom} {nom}"
        
        # Worker ID unique
        worker_id = f"EMP{2024}{i+100:03d}"
        
        # Assigner aléatoirement à un secteur
        secteur = random.choice(secteurs)
        
        # Status aléatoire (principalement actif)
        status_choices = ["Active"] * 8 + ["Inactive", "Congés"]  # 80% actif
        status = random.choice(status_choices)
        
        worker_query = """
            INSERT INTO workers (worker_id, full_name, secteur_id, status, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (worker_id) DO NOTHING
            RETURNING id;
        """
        
        try:
            cursor.execute(worker_query, (
                worker_id, full_name, secteur['id'], status,
                f"Salarié ajouté automatiquement - Secteur: {secteur['secteur_name']}"
            ))
            
            result = cursor.fetchone()
            if result:
                worker_db_id = result['id']
                employees_added += 1
                
                # Ajouter des données RH
                contract_types = ["CDI"] * 6 + ["CDD"] * 4  # 60% CDI, 40% CDD
                contract_type = random.choice(contract_types)
                
                contract_end_date = None
                if contract_type == "CDD":
                    # CDD entre 3 mois et 2 ans
                    contract_end_date = date.today() + timedelta(days=random.randint(90, 730))
                
                # Générer ID et MDP Philia
                id_philia = f"PHI{i+1000:04d}"
                mdp_philia = f"pwd{random.randint(1000, 9999)}"
                
                rh_query = """
                    INSERT INTO rh_data (worker_id, id_philia, mdp_philia, contract_type, contract_end_date)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (worker_id) DO NOTHING;
                """
                
                cursor.execute(rh_query, (
                    worker_db_id, id_philia, mdp_philia, contract_type, contract_end_date
                ))
                
                print(f"   ✅ Ajouté: {full_name} ({worker_id}) - {secteur['secteur_name']} - {contract_type}")
        
        except psycopg2.IntegrityError:
            continue
    
    print(f"👥 {employees_added} nouveaux salariés ajoutés.")
    return employees_added

def assign_phones_to_employees(cursor):
    """Affecte des téléphones aux salariés qui n'en ont pas."""
    print("\n🔗 Affectation des téléphones aux salariés...")
    
    # Récupérer les salariés actifs sans téléphone
    cursor.execute("""
        SELECT w.id, w.worker_id, w.full_name, s.secteur_name
        FROM workers w
        JOIN secteurs s ON w.secteur_id = s.id
        LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
        WHERE w.status = 'Active' AND a.id IS NULL
        ORDER BY w.id;
    """)
    
    unassigned_workers = cursor.fetchall()
    
    if not unassigned_workers:
        print("✅ Tous les salariés actifs ont déjà un téléphone assigné.")
        return
    
    # Récupérer les téléphones disponibles
    cursor.execute("""
        SELECT id, asset_tag, manufacturer, model
        FROM phones
        WHERE status = 'In Stock'
        ORDER BY id;
    """)
    
    available_phones = cursor.fetchall()
    
    if not available_phones:
        print("❌ Aucun téléphone disponible en stock.")
        return
    
    # Récupérer les cartes SIM disponibles
    cursor.execute("""
        SELECT sc.id, sc.iccid, pn.phone_number, sc.carrier
        FROM sim_cards sc
        LEFT JOIN phone_numbers pn ON sc.id = pn.sim_card_id
        LEFT JOIN assignments a ON sc.id = a.sim_card_id AND a.return_date IS NULL
        WHERE sc.status = 'Available' AND a.id IS NULL
        ORDER BY sc.id;
    """)
    
    available_sims = cursor.fetchall()
    
    if not available_sims:
        print("❌ Aucune carte SIM disponible.")
        return
    
    assignments_created = 0
    max_assignments = min(len(unassigned_workers), len(available_phones), len(available_sims))
    
    for i in range(max_assignments):
        worker = unassigned_workers[i]
        phone = available_phones[i]
        sim = available_sims[i]
        
        # Créer l'affectation
        assignment_query = """
            INSERT INTO assignments (phone_id, sim_card_id, worker_id, assignment_date)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        
        try:
            cursor.execute(assignment_query, (
                phone['id'], sim['id'], worker['id'], datetime.now()
            ))
            
            assignment_id = cursor.fetchone()['id']
            
            # Mettre à jour le statut du téléphone
            cursor.execute(
                "UPDATE phones SET status = 'In Use' WHERE id = %s;",
                (phone['id'],)
            )
            
            # Mettre à jour le statut de la SIM
            cursor.execute(
                "UPDATE sim_cards SET status = 'In Use' WHERE id = %s;",
                (sim['id'],)
            )
            
            assignments_created += 1
            phone_number = sim['phone_number'] if sim['phone_number'] else "N/A"
            
            print(f"   ✅ {worker['full_name']} -> {phone['manufacturer']} {phone['model']} ({phone['asset_tag']}) - {phone_number}")
        
        except psycopg2.Error as e:
            print(f"   ❌ Erreur lors de l'affectation pour {worker['full_name']}: {e}")
            continue
    
    print(f"🔗 {assignments_created} affectations créées.")

def main():
    """Fonction principale du script."""
    print("🚀 Démarrage du script d'ajout de stock et de salariés...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            # Ajouter le stock de téléphones
            add_phone_stock(cursor)
            
            # Ajouter les cartes SIM
            add_sim_cards(cursor)
            
            # Ajouter de nouveaux salariés
            employees_added = add_employees(cursor)
            
            # Affecter les téléphones aux salariés
            assign_phones_to_employees(cursor)
            
            # Valider toutes les modifications
            conn.commit()
            print("\n✅ Toutes les modifications ont été validées avec succès!")
            
            # Afficher un résumé
            print("\n📊 RÉSUMÉ:")
            
            # Compter le stock total
            cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Stock';")
            result = cursor.fetchone()
            stock_phones = result[0] if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Use';")
            result = cursor.fetchone()
            used_phones = result[0] if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM workers WHERE status = 'Active';")
            result = cursor.fetchone()
            active_workers = result[0] if result else 0
            
            cursor.execute("""
                SELECT COUNT(*) FROM workers w
                LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
                WHERE w.status = 'Active' AND a.id IS NULL;
            """)
            result = cursor.fetchone()
            unassigned_workers = result[0] if result else 0
            
            print(f"   📱 Téléphones en stock: {stock_phones}")
            print(f"   📱 Téléphones utilisés: {used_phones}")
            print(f"   👥 Salariés actifs: {active_workers}")
            print(f"   👥 Salariés sans téléphone: {unassigned_workers}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    
    finally:
        conn.close()
        print("\n🔚 Script terminé.")

if __name__ == "__main__":
    main()
