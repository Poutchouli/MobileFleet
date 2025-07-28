#!/usr/bin/env python3
# simple_stock_script.py
# Version simplifiée pour ajouter du stock et des affectations

import os
import psycopg2
from dotenv import load_dotenv
import random
from datetime import datetime, date, timedelta

# Load environment variables
load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL."""
    try:
        conn = psycopg2.connect(DB_URL)
        print("✅ Connexion à la base de données établie.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def main():
    """Fonction principale du script."""
    print("🚀 Script simple d'ajout de stock et d'affectations...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("\n🔍 Vérification de l'état actuel...")
        
        # Vérifier l'état actuel
        cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Stock';")
        current_stock = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers WHERE status = 'Active';")
        current_workers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM workers w
            LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
            WHERE w.status = 'Active' AND a.id IS NULL;
        """)
        unassigned_workers = cursor.fetchone()[0]
        
        print(f"   📱 Stock actuel de téléphones: {current_stock}")
        print(f"   👥 Salariés actifs: {current_workers}")
        print(f"   👥 Salariés sans téléphone: {unassigned_workers}")
        
        # Ajouter quelques cartes SIM si nécessaire
        print("\n📡 Ajout de cartes SIM...")
        carriers = ["Orange", "SFR", "Bouygues Telecom", "Free Mobile"]
        sims_added = 0
        
        for i in range(20):  # Ajouter 20 cartes SIM
            iccid = f"8933100{random.randint(100000000, 999999999)}"
            carrier = random.choice(carriers)
            phone_number = f"0{random.randint(6, 7)}{random.randint(10000000, 99999999)}"
            
            try:
                # Insérer la carte SIM
                cursor.execute("""
                    INSERT INTO sim_cards (iccid, carrier, plan_details, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (iccid) DO NOTHING
                    RETURNING id;
                """, (iccid, carrier, f"Plan {carrier}", "Available"))
                
                result = cursor.fetchone()
                if result:
                    sim_id = result[0]
                    sims_added += 1
                    
                    # Ajouter le numéro de téléphone
                    cursor.execute("""
                        INSERT INTO phone_numbers (phone_number, sim_card_id, status)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (phone_number) DO NOTHING;
                    """, (phone_number, sim_id, "Active"))
                    
                    print(f"   ✅ Ajouté: SIM {carrier} - {phone_number}")
            
            except Exception as e:
                print(f"   ⚠️  Erreur: {e}")
                continue
        
        print(f"📡 {sims_added} cartes SIM ajoutées.")
        
        # Ajouter des salariés
        print("\n👥 Ajout de nouveaux salariés...")
        
        # Récupérer les secteurs
        cursor.execute("SELECT id, secteur_name FROM secteurs;")
        secteurs = cursor.fetchall()
        
        if not secteurs:
            print("❌ Aucun secteur trouvé.")
            return
        
        prenoms = ["Pierre", "Marie", "Jean", "Sophie", "Paul", "Claire", "Michel", "Anne"]
        noms = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand", "Leroy"]
        
        employees_added = 0
        
        for i in range(10):  # Ajouter 10 salariés
            prenom = random.choice(prenoms)
            nom = random.choice(noms)
            full_name = f"{prenom} {nom}"
            worker_id = f"EMP{2024}{random.randint(500, 999)}"
            secteur = random.choice(secteurs)
            
            try:
                cursor.execute("""
                    INSERT INTO workers (worker_id, full_name, secteur_id, status, notes)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (worker_id) DO NOTHING
                    RETURNING id;
                """, (worker_id, full_name, secteur[0], "Active", "Ajouté automatiquement"))
                
                result = cursor.fetchone()
                if result:
                    worker_db_id = result[0]
                    employees_added += 1
                    
                    # Ajouter des données RH
                    cursor.execute("""
                        INSERT INTO rh_data (worker_id, id_philia, mdp_philia, contract_type)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (worker_id) DO NOTHING;
                    """, (worker_db_id, f"PHI{i+2000}", f"pwd{i+2000}", "CDI"))
                    
                    print(f"   ✅ Ajouté: {full_name} ({worker_id}) - {secteur[1]}")
            
            except Exception as e:
                print(f"   ⚠️  Erreur: {e}")
                continue
        
        print(f"👥 {employees_added} nouveaux salariés ajoutés.")
        
        # Effectuer des affectations
        print("\n🔗 Affectation des téléphones...")
        
        # Récupérer les salariés sans téléphone
        cursor.execute("""
            SELECT w.id, w.worker_id, w.full_name
            FROM workers w
            LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
            WHERE w.status = 'Active' AND a.id IS NULL
            LIMIT 20;
        """)
        workers_to_assign = cursor.fetchall()
        
        # Récupérer les téléphones disponibles
        cursor.execute("""
            SELECT id, asset_tag, manufacturer, model
            FROM phones
            WHERE status = 'In Stock'
            LIMIT 20;
        """)
        available_phones = cursor.fetchall()
        
        # Récupérer les SIM disponibles
        cursor.execute("""
            SELECT sc.id, pn.phone_number, sc.carrier
            FROM sim_cards sc
            LEFT JOIN phone_numbers pn ON sc.id = pn.sim_card_id
            LEFT JOIN assignments a ON sc.id = a.sim_card_id AND a.return_date IS NULL
            WHERE sc.status = 'Available' AND a.id IS NULL
            LIMIT 20;
        """)
        available_sims = cursor.fetchall()
        
        assignments_made = 0
        max_assignments = min(len(workers_to_assign), len(available_phones), len(available_sims))
        
        print(f"📊 Affectations possibles: {max_assignments}")
        
        for i in range(max_assignments):
            worker = workers_to_assign[i]
            phone = available_phones[i]
            sim = available_sims[i]
            
            try:
                # Créer l'affectation
                cursor.execute("""
                    INSERT INTO assignments (phone_id, sim_card_id, worker_id, assignment_date)
                    VALUES (%s, %s, %s, %s);
                """, (phone[0], sim[0], worker[0], datetime.now()))
                
                # Mettre à jour les statuts
                cursor.execute("UPDATE phones SET status = 'In Use' WHERE id = %s;", (phone[0],))
                cursor.execute("UPDATE sim_cards SET status = 'In Use' WHERE id = %s;", (sim[0],))
                
                assignments_made += 1
                print(f"   ✅ {worker[2]} -> {phone[2]} {phone[3]} - {sim[1] or 'N/A'}")
            
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                continue
        
        print(f"🔗 {assignments_made} affectations créées.")
        
        # Valider les modifications
        conn.commit()
        print("\n✅ Toutes les modifications validées!")
        
        # Résumé final
        cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Stock';")
        final_stock = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phones WHERE status = 'In Use';")
        final_used = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers WHERE status = 'Active';")
        final_workers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM workers w
            LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
            WHERE w.status = 'Active' AND a.id IS NULL;
        """)
        final_unassigned = cursor.fetchone()[0]
        
        print(f"\n📊 RÉSUMÉ FINAL:")
        print(f"   📱 Téléphones en stock: {final_stock}")
        print(f"   📱 Téléphones utilisés: {final_used}")
        print(f"   👥 Salariés actifs: {final_workers}")
        print(f"   👥 Salariés sans téléphone: {final_unassigned}")
        
        if final_workers > 0:
            coverage = ((final_workers - final_unassigned) / final_workers * 100)
            print(f"   📊 Couverture mobile: {coverage:.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
        raise
    
    finally:
        if cursor:
            cursor.close()
        conn.close()
        print("\n🔚 Script terminé.")

if __name__ == "__main__":
    main()
