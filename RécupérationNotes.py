#Importation de la bibliothèque pour récupérer la page HTML
import requests
#Importation de la bibliothèque pour parser la page HTML
from bs4 import BeautifulSoup
#Importation de la bibliothèque pour les tableau 
import numpy as np
#Importation bibliothèque pour utiliser les pattern
import re

url ='https://campusonline.inseec.net/note/note_ajax.php?AccountName=B3yyZbaV9FoX0Zh%2BznXga8elZn4c55cGnqCMe2EDACw%3D+&c=classique&mode_affichage=&version=PROD&mode_test=N'

def remplir_Tableau_Info(url_notes) : 
    #Récupération des informations de la page
    response = requests.get(url)
    
    #Test de récupération des données 
    if response.status_code == 200:
        html_content = response.text
    else:
        print(f'Erreur: {response.status_code}')
       
    #création de l'objet BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
        
    #récupération des informations des matières 
    information_gen = soup.find_all('tr', {'class': 'slave master-1'})
    
    #creation d'un tableau à trois dimension
    information_finale = np.empty((8, 15, 30), dtype=np.dtype('U100'))
    i = 0
    j=1
    pourcentage = ""
    #itère à travers les cellules pour récupérer les Modules et les notes 
    for cell in information_gen:
        text = cell.text
        cellule_separee = text.split()
        # récupère la cellule qui contient l'information
        if "Module" in cell.text:
            information_finale[i,0,0] = text
            i = i+1
            j = 1
        if cell.text.find("Module") == -1 and cell.text.find("Continu") == -1 and cell.text.find("Examen") == -1 and cell.text.find("Semestre") == -1 and cell.text.find("Projet") == -1 or ("Project" in cell.text and cell.text.find("Module") == -1 and cell.text.find("Continu") == -1 and cell.text.find("Examen") == -1 and cell.text.find("Semestre") == -1):
            if i>0:
                derniere_chaine_cellule = cellule_separee[-1]
                derniere_lettre_cellule = derniere_chaine_cellule[-1]
                information_finale[i-1,j,0]=text
                information_finale[i-1,j,1]=derniere_lettre_cellule
                j = j + 1
        if "Continu" in cell.text:
            for cellule in cellule_separee:
                if "%" in cellule:
                    for elmnt in cellule:
                        if (elmnt.isdigit() or elmnt == '.'):
                            pourcentage = pourcentage + elmnt
                        if(elmnt == "%"):
                            break
                    break
            information_finale[i-1,j-1,2]=pourcentage
            pourcentage = ""
        if "Examen" in cell.text:
             for cellule in cellule_separee:
                 if "%" in cellule:
                     for elmnt in cellule:
                         if (elmnt.isdigit() or elmnt == '.'):
                             pourcentage = pourcentage + elmnt
                         if(elmnt == "%"):
                             break
                     break
                         
             information_finale[i-1,j-1,3]=pourcentage
             pourcentage = ""
        if "Projet" in cell.text:
             for cellule in cellule_separee:
                 if "%" in cellule:
                     for elmnt in cellule:
                         if (elmnt.isdigit() or elmnt == '.'):
                             pourcentage = pourcentage + elmnt
                         if(elmnt == "%"):
                             break
                     break
                         
             information_finale[i-1,j-1,4]=pourcentage
             pourcentage = ""
    
    i = 0
    j = 0
    continu = 0
    examen = 0
    projet = 0
    last = 0
    for tr in soup.find_all('tr', class_='slave master-1'):
        libelle_list = tr.find_all('td', class_='libelle item-ev1')
        note_list = tr.find_all('td', class_='note item-ev1')
        if libelle_list and note_list:
            libelle = libelle_list[0].text
            note = note_list[0].text
            if libelle[0] == 'C':
                note_sep = note.split()
                j = j+1 
                if (information_finale[i][j][0] == '' or information_finale[i][j][0] == ' ') and i<3:
                    i = i+1
                    j = 1
                for elt in note_sep:
                    if(elt != '-'):
                        information_finale[i,j,5+continu]=elt
                        continu = continu + 1
                continu = 0
            elif libelle[0] == 'E':
                note_sep = note.split()
                j = j+1
                if(last == 'C' or last == 0):
                    i = i
                    j = j - 1
                elif (information_finale[i][j][0] == '' or information_finale[i][j][0] == ' ') and i<3:
                    i = i+1
                    j = 1
                for elt in note_sep:
                    if(elt != '-'):
                        information_finale[i,j,13+examen] = elt
                        examen = examen + 1
                examen = 0
            elif libelle[0] == 'P':
                note_sep = note.split()
                j = j+1
                if(last == 'E' or last == 0):
                    i = i
                    j = j - 1
                elif (information_finale[i][j][0] == '' or information_finale[i][j][0] == ' ') and i<3:
                    i = i+1
                    j = 1
                for elt in note_sep:
                    if(elt != '-'):
                        information_finale[i,j,24+projet] = elt
                        projet = projet + 1
                projet = 0
            last = libelle[0]
    return information_finale

def calculerMoyenneTableau(tableau,module,matiere,compteur):
    tab_moyenne = np.full((6,2), -1,float)
    ligne = 0
    pattern = r"^\d+(\,\d{1,2})?$"
    bonus_moyenne = 0
    suiteOuNon = 0
    
    #Charger les notes de controle CC
    if tableau[module][matiere][0].find("Bonus") == -1:
        
        if re.match(pattern, tableau[module][matiere][compteur]) and re.match(pattern, tableau[module][matiere][compteur+2]):
            tab_moyenne[ligne][0] = float(tableau[module][matiere][compteur].replace(",", "."))
            tab_moyenne[ligne][1] = float(tableau[module][matiere][compteur+1].replace("(", "").replace(")", "").replace("%", "").strip())
            suiteOuNon = 1
            ligne += 1
            compteur += 2
            while(suiteOuNon == 1):
                if re.match(pattern, tableau[module][matiere][compteur]):
                    tab_moyenne[ligne][0] = float(tableau[module][matiere][compteur].replace(",", "."))
                    if tableau[module][matiere][compteur+1] != '' :tab_moyenne[ligne][1] = float(tableau[module][matiere][compteur+1].replace("(", "").replace(")", "").replace("%", "").strip())
                    compteur += 2
                    ligne += 1
                else :
                    suiteOuNon = 0
                    
        elif re.match(pattern, tableau[module][matiere][compteur]) and not re.match(pattern, tableau[module][matiere][compteur+2]):
            tab_moyenne[ligne][0] = float(tableau[module][matiere][compteur].replace(",", "."))
            if tableau[module][matiere][compteur+1] != '' :tab_moyenne[ligne][1] = float(tableau[module][matiere][compteur+1].replace("(", "").replace(")", "").replace("%", "").strip())
            suiteOuNon = 0
            ligne += 1
    else:
        if tableau[module][matiere][compteur] != '' and tableau[module][matiere][compteur] != " ":
            entreeTexte = tableau[module][matiere][compteur]
            bonus_moyenne = (float(entreeTexte.replace(",", "."))-10)/10
    
    return bonus_moyenne,tab_moyenne
    
        

def calculerMoyenneMatiere(tableau,module,matiere):
    bonus,tab_moyenne_CC= calculerMoyenneTableau(tableau, module, matiere, 5)
    tab_moyenne_EX = calculerMoyenneTableau(tableau, module, matiere, 13)[1]
    tab_moyenne_PR = calculerMoyenneTableau(tableau, module, matiere, 24)[1]
    ligne = 0
    coeff_CC = tableau[module][matiere][2] if tableau[module][matiere][2] != '' else 0
    coeff_EX = tableau[module][matiere][3] if tableau[module][matiere][3] != '' else 0
    coeff_PR = tableau[module][matiere][4] if tableau[module][matiere][4] != '' else 0
    moyenne_CC = 0
    moyenne_EX = 0
    moyenne_PR = 0
    somme_Note_CC = 0
    somme_Note_PR = 0
    somme_Note_EX = 0
    somme_Coef_CC = 0
    somme_Coef_PR = 0
    somme_Coef_EX = 0
    moyenne_Generale = 0
    
    
    for ligne in range (6):
        if tab_moyenne_CC[ligne][0] != -1:
            if tab_moyenne_CC[ligne][1] != -1:
                somme_Note_CC += tab_moyenne_CC[ligne][0] * tab_moyenne_CC[ligne][1]
                somme_Coef_CC += tab_moyenne_CC[ligne][1]
            else:
                somme_Note_CC += tab_moyenne_CC[ligne][0]
                somme_Coef_CC +=1
        if tab_moyenne_EX[ligne][0] != -1:
            if tab_moyenne_EX[ligne][1] != -1:
                somme_Note_EX += tab_moyenne_EX[ligne][0] * tab_moyenne_EX[ligne][1]
                somme_Coef_EX += tab_moyenne_EX[ligne][1]
            else:
                somme_Note_EX += tab_moyenne_EX[ligne][0]
                somme_Coef_EX +=1
        if tab_moyenne_PR[ligne][0] != -1:
            if tab_moyenne_PR[ligne][1] != -1:
                somme_Note_PR += tab_moyenne_PR[ligne][0] * tab_moyenne_PR[ligne][1]
                somme_Coef_PR += tab_moyenne_PR[ligne][1]
            else:
                somme_Note_PR += tab_moyenne_PR[ligne][0]
                somme_Coef_PR +=1
        
        if somme_Coef_CC and somme_Coef_EX and somme_Coef_PR:
            moyenne_CC = somme_Note_CC / somme_Coef_CC
            moyenne_EX = somme_Note_EX / somme_Coef_EX
            moyenne_PR = somme_Note_PR / somme_Coef_PR
            moyenne_Generale = ((float(moyenne_CC )* float(coeff_CC)) + (float(moyenne_EX )* float(coeff_EX)) + (float(moyenne_PR )* float(coeff_PR))) / (float(coeff_CC) + float(coeff_EX )+ float(coeff_PR))
        elif somme_Coef_CC and somme_Coef_EX and not somme_Coef_PR:
            moyenne_CC = somme_Note_CC / somme_Coef_CC
            moyenne_EX = somme_Note_EX / somme_Coef_EX
            moyenne_Generale = ((float(moyenne_CC )* float(coeff_CC)) + (float(moyenne_EX )* float(coeff_EX)) + (float(moyenne_PR )* float(coeff_PR))) / (float(coeff_CC) + float(coeff_EX ))
        elif somme_Coef_CC and not somme_Coef_EX and somme_Coef_PR:
            moyenne_CC = somme_Note_CC / somme_Coef_CC
            moyenne_PR = somme_Note_PR / somme_Coef_PR
            moyenne_Generale = ((float(moyenne_CC )* float(coeff_CC)) + (float(moyenne_EX )* float(coeff_EX)) + (float(moyenne_PR )* float(coeff_PR))) / (float(coeff_CC) + float(coeff_PR))
        elif not somme_Coef_CC and somme_Coef_EX and somme_Coef_PR:
            moyenne_EX = somme_Note_EX / somme_Coef_EX
            moyenne_PR = somme_Note_PR / somme_Coef_PR
            moyenne_Generale = ((float(moyenne_CC )* float(coeff_CC)) + (float(moyenne_EX )* float(coeff_EX)) + (float(moyenne_PR )* float(coeff_PR))) / (float(coeff_EX )+ float(coeff_PR))
        elif not somme_Coef_CC and not somme_Coef_EX and somme_Coef_PR:
            moyenne_PR = somme_Note_PR / somme_Coef_PR
            moyenne_Generale = moyenne_PR
        elif not somme_Coef_CC and  somme_Coef_EX and not somme_Coef_PR:
            moyenne_EX = somme_Note_EX / somme_Coef_EX
            moyenne_Generale = moyenne_EX
        elif somme_Coef_CC and not somme_Coef_EX and not somme_Coef_PR:
            moyenne_CC = somme_Note_CC / somme_Coef_CC
            moyenne_Generale = moyenne_CC
        else :
            moyenne_Generale = -1
            
    return moyenne_Generale,bonus
    
def calculerMoyenneModule(tableau, numeroModule):
    somme_Moyenne_module = 0
    somme_Coef_module = 0
    variable_temporaire_note = 0
    variable_temporaire_Coef = 0
    moyenne_module = 0
    bonus_matiere = 0
    bonus_tmp = 0
    
    for i in range(1,15):
        variable_temporaire_note,bonus_tmp = calculerMoyenneMatiere(tableau, numeroModule, i)
        bonus_matiere += bonus_tmp
        variable_temporaire_Coef = tableau[numeroModule][i][1]
        if(variable_temporaire_note != -1):
            somme_Coef_module += float(variable_temporaire_Coef)
            somme_Moyenne_module += float(variable_temporaire_note) * float(variable_temporaire_Coef)
    
    if somme_Coef_module != 0 and somme_Coef_module != -1 :
        moyenne_module = (float(somme_Moyenne_module) / float(somme_Coef_module)) + bonus_matiere
    else:
        moyenne_module = -1
        somme_Coef_module = -1
        
    return moyenne_module,somme_Coef_module
        
def calculerMoyenneGenerale(tableau):
    var_tem_note = 0
    var_tem_coef = 0
    somme_moy_mod = 0
    somme_coef_mod = 0
    moyenneGenerale = 0
    bonus = 0
    for i in range(0,8):
        var_tem_note,var_tem_coef = calculerMoyenneModule(tableau, i)
        if(var_tem_note != -1):
            if "Module Sciences et Techniques" in tableau[i][0][0] : 
               somme_moy_mod += (float(var_tem_note) + bonus) * float(var_tem_coef)
               somme_coef_mod +=float(var_tem_coef)
               print('Moyenne : ' +  str(tableau[i][0][0] )+ ' ' + str(var_tem_note)) 
            else:
                somme_moy_mod += float(var_tem_note) * float(var_tem_coef)
                somme_coef_mod +=float(var_tem_coef)
                print('Moyenne : ' +  str(tableau[i][0][0] )+ ' ' + str(var_tem_note)) 
            
    if somme_coef_mod != 0 and somme_coef_mod != -1:
        moyenneGenerale = float(somme_moy_mod) / float(somme_coef_mod)
    else:
        moyenneGenerale = -1
    print('Moyenne Générale : ' + str(moyenneGenerale))
