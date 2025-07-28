#!/usr/bin/env python3
# add_stock_and_employees_v2.py
# Version améliorée du script pour ajouter du stock de téléphones, de nouveaux salariés et les affecter

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

def add_sim_cards_safe(cursor):
    """Ajoute des cartes SIM à la base de données de manière sécurisée."""
    print("\n📡 Ajout des cartes SIM...")
    
    carriers = ["Orange", "SFR", "Bouygues Telecom", "Free Mobile"]
    sims_added = 0
    
    # Vérifier les ICCIDs existants
    cursor.execute("SELECT iccid FROM sim_cards;")
    existing_iccids = {row['iccid'] for row in cursor.fetchall()}
    
    # Vérifier les numéros de téléphone existants
    cursor.execute("SELECT phone_number FROM phone_numbers;")
    existing_numbers = {row['phone_number'] for row in cursor.fetchall()}
    
    for i in range(60):  # Essayer d'ajouter 60 cartes SIM
        # Générer un ICCID unique
        attempts = 0
        while attempts < 10:  # Maximum 10 tentatives
            iccid = f"8933100000000{random.randint(1000000, 9999999)}"
            if iccid not in existing_iccids:
                break
            attempts += 1
        
        if attempts >= 10:
            continue  # Passer à la suivante si on ne trouve pas d'ICCID unique
        
        carrier = random.choice(carriers)
        
        try:
            # Insérer la carte SIM
            sim_query = """
                INSERT INTO sim_cards (iccid, carrier, plan_details, status)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """
            
            cursor.execute(sim_query, (
                iccid, carrier, f"Plan professionnel {carrier}", "Available"
            ))
            
            sim_id = cursor.fetchone()['id']
            existing_iccids.add(iccid)
            sims_added += 1
            
            # Générer un numéro de téléphone unique
            phone_attempts = 0
            while phone_attempts < 10:
                phone_number = f"0{random.randint(6, 7)}{random.randint(10000000, 99999999)}"
                if phone_number not in existing_numbers:
                    break
                phone_attempts += 1
            
            if phone_attempts < 10:
                # Ajouter le numéro de téléphone
                phone_number_query = """
                    INSERT INTO phone_numbers (phone_number, sim_card_id, status)
                    VALUES (%s, %s, %s);
                """
                
                cursor.execute(phone_number_query, (phone_number, sim_id, "Active"))
                existing_numbers.add(phone_number)
                print(f"   ✅ Ajouté: SIM {carrier} - {phone_number}")
            else:
                print(f"   ✅ Ajouté: SIM {carrier} - {iccid} (sans numéro)")
        
        except psycopg2.IntegrityError as e:
            print(f"   ⚠️  Erreur d'intégrité pour {iccid}: {e}")
            continue
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {e}")
            continue
    
    print(f"📡 {sims_added} cartes SIM ajoutées.")

def add_employees_safe(cursor):
    """Ajoute de nouveaux salariés à la base de données de manière sécurisée."""
    print("\n👥 Ajout de nouveaux salariés...")
    
    # Récupérer les secteurs existants
    cursor.execute("SELECT id, secteur_name FROM secteurs ORDER BY id;")
    secteurs = cursor.fetchall()
    
    if not secteurs:
        print("❌ Aucun secteur trouvé. Veuillez d'abord créer des secteurs.")
        return 0
    
    # Récupérer les worker_id existants
    cursor.execute("SELECT worker_id FROM workers;")
    existing_worker_ids = {row['worker_id'] for row in cursor.fetchall()}
    
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
        # Générer un worker_id unique
        attempts = 0
        while attempts < 10:
            worker_id = f"EMP{2024}{random.randint(100, 999)}"
            if worker_id not in existing_worker_ids:
                break
            attempts += 1
        
        if attempts >= 10:
            continue  # Passer au suivant si on ne trouve pas d'ID unique
        
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        full_name = f"{prenom} {nom}"
        
        # Assigner aléatoirement à un secteur
        secteur = random.choice(secteurs)
        
        # Status aléatoire (principalement actif)
        status_choices = ["Active"] * 8 + ["Inactive", "Congés"]  # 80% actif
        status = random.choice(status_choices)
        
        try:
            worker_query = """
                INSERT INTO workers (worker_id, full_name, secteur_id, status, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """
            
            cursor.execute(worker_query, (
                worker_id, full_name, secteur['id'], status,
                f"Salarié ajouté automatiquement - Secteur: {secteur['secteur_name']}"
            ))
            
            worker_db_id = cursor.fetchone()['id']
            existing_worker_ids.add(worker_id)
            employees_added += 1
            
            # Ajouter des données RH
            contract_types = ["CDI"] * 6 + ["CDD"] * 4  # 60% CDI, 40% CDD
            contract_type = random.choice(contract_types)
            
            contract_end_date = None
            if contract_type == "CDD":
                # CDD entre 3 mois et 2 ans
                contract_end_date = date.today() + timedelta(days=random.randint(90, 730))
            
            # Générer ID et MDP Philia uniques
            id_philia = f"PHI{random.randint(1000, 9999)}"
            mdp_philia = f"pwd{random.randint(1000, 9999)}"
            
            rh_query = """
                INSERT INTO rh_data (worker_id, id_philia, mdp_philia, contract_type, contract_end_date)
                VALUES (%s, %s, %s, %s, %s);
            """
            
            cursor.execute(rh_query, (
                worker_db_id, id_philia, mdp_philia, contract_type, contract_end_date
            ))
            
            print(f"   ✅ Ajouté: {full_name} ({worker_id}) - {secteur['secteur_name']} - {contract_type}")
        
        except psycopg2.IntegrityError as e:
            print(f"   ⚠️  Erreur d'intégrité pour {worker_id}: {e}")
            continue
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {e}")
            continue
    
    print(f"👥 {employees_added} nouveaux salariés ajoutés.")
    return employees_added

def assign_phones_to_employees_safe(cursor):
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
    
    # Récupérer les cartes SIM disponibles avec leurs numéros
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
    
    print(f"📊 Affectations possibles: {max_assignments}")
    print(f"   - Salariés sans téléphone: {len(unassigned_workers)}")
    print(f"   - Téléphones disponibles: {len(available_phones)}")
    print(f"   - Cartes SIM disponibles: {len(available_sims)}")
    
    for i in range(max_assignments):
        worker = unassigned_workers[i]
        phone = available_phones[i]
        sim = available_sims[i]
        
        try:
            # Créer l'affectation
            assignment_query = """
                INSERT INTO assignments (phone_id, sim_card_id, worker_id, assignment_date)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """
            
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
    print("🚀 Démarrage du script d'ajout de stock et de salariés (Version sécurisée)...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            print("\n🔍 Vérification de l'état actuel...")
            
            # Vérifier l'état actuel
            cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Stock';")
            result = cursor.fetchone()
            current_stock = result[0] if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM sim_cards WHERE status = 'Available';")
            result = cursor.fetchone()
            current_sims = result[0] if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM workers WHERE status = 'Active';")
            result = cursor.fetchone()
            current_workers = result[0] if result else 0
            
            print(f"   📱 Stock actuel de téléphones: {current_stock}")
            print(f"   📡 Cartes SIM disponibles: {current_sims}")
            print(f"   👥 Salariés actifs: {current_workers}")
            
            # Ajouter les cartes SIM d'abord (on en a besoin pour les affectations)
            add_sim_cards_safe(cursor)
            
            # Ajouter de nouveaux salariés
            employees_added = add_employees_safe(cursor)
            
            # Affecter les téléphones aux salariés (utilise le stock existant + nouveau)
            assign_phones_to_employees_safe(cursor)
            
            # Valider toutes les modifications
            conn.commit()
            print("\n✅ Toutes les modifications ont été validées avec succès!")
            
            # Afficher un résumé final
            print("\n📊 RÉSUMÉ FINAL:")
            
            cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Stock';")
            result = cursor.fetchone()
            final_stock = result[0] if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Use';")
            result = cursor.fetchone()
            final_used = result[0] if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM workers WHERE status = 'Active';")
            result = cursor.fetchone()
            final_workers = result[0] if result else 0
            
            cursor.execute("""
                SELECT COUNT(*) FROM workers w
                LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
                WHERE w.status = 'Active' AND a.id IS NULL;
            """)
            result = cursor.fetchone()
            final_unassigned = result[0] if result else 0
            
            print(f"   📱 Téléphones en stock: {final_stock}")
            print(f"   📱 Téléphones utilisés: {final_used}")
            print(f"   👥 Salariés actifs: {final_workers}")
            print(f"   👥 Salariés sans téléphone: {final_unassigned}")
            
            coverage = ((final_workers - final_unassigned) / final_workers * 100) if final_workers > 0 else 0
            print(f"   📊 Couverture mobile: {coverage:.1f}%")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
        print("\n🔚 Script terminé.")

if __name__ == "__main__":
    main()
