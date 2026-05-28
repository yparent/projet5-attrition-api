import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from dotenv import load_dotenv
load_dotenv()


import pandas as pd
from app.database import SessionLocal
from app.db_models import Employee


# Charger et fusionner les 3 CSV
sirh = pd.read_csv('data/extrait_sirh.csv', sep=',')
eval_df = pd.read_csv('data/extrait_eval.csv', sep=',')
sondage = pd.read_csv('data/extrait_sondage.csv', sep=',')


# Nettoyage des cles de jointure
eval_df['id_employee'] = eval_df['eval_number'].str.replace('E_','').astype(int)
sondage['id_employee'] = sondage['code_sondage'].astype(int)


# Fusion
df = sirh.merge(eval_df, on='id_employee').merge(sondage, on='id_employee')


# Insertion en base
db = SessionLocal()
count = 0
for _, row in df.iterrows():
    emp = Employee(
        employee_id=int(row['id_employee']),
        age=int(row['age']),
        genre=row['genre'],
        departement=row['departement'],
        poste=row['poste'],
        revenu_mensuel=float(row['revenu_mensuel']),
        annees_dans_l_entreprise=int(row['annees_dans_l_entreprise']),
        heure_supplementaires=row['heure_supplementaires'],
        a_quitte_l_entreprise=1 if row['a_quitte_l_entreprise'] in ['Oui', 'Yes', 1, '1'] else 0
    )
    db.add(emp)
    count += 1
db.commit()
db.close()
print(f'{count} employes inseres en base.')
