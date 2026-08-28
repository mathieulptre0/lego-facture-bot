import os
import pymupdf as fitz


def inserer_texte(
    page,
    font,
    fontname,
    fontfile,
    texte,
    taille,
    espacement,
    left_mm,
    top_mm,
    align_right=False,
    right_mm=0,
):
  """Fonction utilitaire pour insérer du texte proprement (normal ou aligné à droite)."""
  page.insert_font(fontname=fontname, fontfile=fontfile)
  left_pt = left_mm / 25.4 * 72
  top_pt = top_mm / 25.4 * 72
  y = top_pt + taille

  if align_right:
    right_pt = right_mm / 25.4 * 72
    largeur_totale = sum(
        font.text_length(c, fontsize=taille) + espacement for c in texte
    )
    x = right_pt - largeur_totale
  else:
    x = left_pt

  for c in texte:
    page.insert_text(
        (x, y), c, fontname=fontname, fontsize=taille, color=(0, 0, 0)
    )
    largeur_c = font.text_length(c, fontsize=taille)
    x += largeur_c + espacement


def inserer_image(page, image_path, largeur_mm, left_mm, top_mm):
  """Fonction utilitaire pour insérer une image avec calcul automatique du ratio."""
  left_pt = left_mm / 25.4 * 72
  top_pt = top_mm / 25.4 * 72
  largeur_pt = largeur_mm / 25.4 * 72

  img_doc = fitz.open(image_path)
  ratio = img_doc[0].rect.height / img_doc[0].rect.width
  hauteur_pt = largeur_pt * ratio

  rect = fitz.Rect(left_pt, top_pt, left_pt + largeur_pt, top_pt + hauteur_pt)
  page.insert_image(rect, filename=image_path)


def dessiner_ligne(page, left_mm, right_mm, top_mm, epaisseur=1):
  """Fonction utilitaire pour tracer des lignes de séparation vectorielles."""
  x0 = left_mm / 25.4 * 72
  x1 = right_mm / 25.4 * 72
  y = top_mm / 25.4 * 72

  shape = page.new_shape()
  shape.draw_line(fitz.Point(x0, y), fitz.Point(x1, y))
  shape.finish(color=(0, 0, 0), width=epaisseur)
  shape.commit()


def executer_generation_complete():
  # Chemins des fichiers
  dossier = r"C:\Users\leazy\Desktop\lego facture bot"
  html_path = os.path.join(dossier, "page_blanche.html")
  pdf_path = os.path.join(dossier, "Receipt.pdf")
  police_medium = os.path.join(dossier, "CeraProMedium.ttf")
  police_bold = os.path.join(dossier, "cera-pro-bold.ttf")
  image_avis_path = os.path.join(
      dossier, "73b318fc-9648-420d-b3f8-4728ee3156ee.png"
  )
  image_width200_path = os.path.join(dossier, "width200.png")
  image_width87_path = os.path.join(dossier, "width87.png")
  image_width60_path = os.path.join(dossier, "width60.png")
  image_width99_path = os.path.join(dossier, "width99.png")

  # 1. --- Conversion HTML vers PDF ---
  width_mm = 80
  height_mm = 385.8

  width_pt = width_mm / 25.4 * 72
  height_pt = height_mm / 25.4 * 72
  mediabox = fitz.Rect(0, 0, width_pt, height_pt)

  with open(html_path, encoding="utf-8") as f:
    html = f.read()

  archive = fitz.Archive(dossier)
  story = fitz.Story(html=html, archive=archive)
  writer = fitz.DocumentWriter(pdf_path)

  more = True
  while more:
    dev = writer.begin_page(mediabox)
    more, _ = story.place(mediabox)
    story.draw(dev)
    writer.end_page()

  writer.close()

  print(f"PDF créé : {pdf_path}")
  print(f"Taille : {width_mm} x {height_mm} mm")

  doc = fitz.open(pdf_path)
  page = doc[0]

  font_medium = fitz.Font(fontfile=police_medium)
  font_bold = fitz.Font(fontfile=police_bold)

  # 2. --- Insertion du texte "DUPLICATA" (en haut) ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldHaut",
      police_bold,
      "DUPLICATA",
      15,
      -0.394,
      24,
      1,
  )
  print("Texte 'DUPLICATA' (haut) inséré dans le PDF.")

  # 3. --- Insertion de l'image (width60.png) ---
  inserer_image(page, image_width60_path, 19, 28, 15.3)
  print("Image 'width60.png' insérée dans le PDF.")

  # 4. --- Insertion du texte "149 LEGO, LQT Paris, EU-FR" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumLQT",
      police_medium,
      "149 LEGO, LQT Paris, EU-FR",
      7.9,
      0.03,
      20,
      40.4,
  )
  print("Texte '149 LEGO, LQT Paris, EU-FR' inséré dans le PDF.")

  # 5. --- Insertion de la deuxième ligne d'adresse ---
  inserer_texte(
      page,
      font_medium,
      "CeraMedium2",
      police_medium,
      "15 Parv. de la Défense,",
      7.9,
      0,
      23,
      43.2,
  )
  print("Deuxième ligne d'adresse insérée dans le PDF.")

  # 6. --- Insertion de la troisième ligne d'adresse ---
  inserer_texte(
      page,
      font_medium,
      "CeraMedium3",
      police_medium,
      "92092 Puteaux, FR",
      7.9,
      0,
      25.5,
      46.2,
  )
  print("Troisième ligne d'adresse insérée dans le PDF.")

  # 6 bis. --- Insertion du texte "Transaction de vente" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldTrans",
      police_bold,
      "Transaction de vente",
      15,
      0,
      11,
      54.5,
  )
  print("Texte 'Transaction de vente' inséré dans le PDF.")

  # 7. --- Insertion de l'article "Porte-clés Miles Morales" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumArt1",
      police_medium,
      "Porte-clés Miles Morales",
      9.5,
      0,
      2,
      66,
  )
  print("Article 'Porte-clés Miles Morales' inséré dans le PDF.")

  # 8. --- Insertion du prix de l'article "5,99 €" (aligné à droite) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumPrix1",
      police_medium,
      "5,99 €",
      9.5,
      0,
      0,
      66,
      align_right=True,
      right_mm=72.5,
  )
  print("Prix '5,99 €' (aligné à droite) inséré dans le PDF.")

  # 9. --- Insertion du texte "Récapitulatif TVA Taux" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumTVA",
      police_medium,
      "Récapitulatif TVA  Taux",
      9.3,
      0,
      2.2,
      73.6,
  )
  print("Texte 'Récapitulatif TVA Taux' inséré dans le PDF.")

  # 9 bis. --- Insertion du texte "TVA" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumTVATexte",
      police_medium,
      "TVA",
      9.2,
      0,
      66.5,
      73.7,
  )
  print("Texte 'TVA' inséré dans le PDF.")

  # 10. --- Insertion du texte "20.0%" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMedium20",
      police_medium,
      "20.0%",
      9.3,
      0,
      30.8,
      77.8,
  )
  print("Texte '20.0%' inséré dans le PDF.")

  # 10 bis. --- Insertion du NOUVEAU montant "1,00 €" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumMontantTVA2",
      police_medium,
      "1,00 €",
      9.5,
      0,
      0,
      77.6,
      align_right=True,
      right_mm=72.7,
  )
  print("Second texte '1,00 €' inséré dans le PDF (emplacement TVA).")

  # 11. --- Insertion du texte "Total" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumTotalLabel",
      police_medium,
      "Total",
      9.3,
      0,
      30.8,
      81.5,
  )
  print("Texte 'Total' inséré dans le PDF.")

  # 12. --- Insertion du premier texte "1,00 €" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumTotalMontant",
      police_medium,
      "1,00 €",
      9.5,
      -0.02,
      0,
      81.4,
      align_right=True,
      right_mm=72.6,
  )
  print("Texte '1,00 €' (aligné à droite - Total) inséré dans le PDF.")

  # 13. --- Insertion du texte "Nombre d'articles : 1" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumNbArticles",
      police_medium,
      "Nombre d'articles : 1",
      9.5,
      0,
      2.2,
      91,
  )
  print("Texte 'Nombre d'articles : 1' inséré dans le PDF.")

  # 13 bis. --- Insertion du texte "Total à payer" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldTotalPayer",
      police_bold,
      "Total à payer",
      11,
      -0.1,
      2.1,
      96.5,
  )
  print("Texte 'Total à payer' inséré dans le PDF.")

  # 14. --- Insertion du texte "5,99 €" (Total à payer) ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldPrixPayer",
      police_bold,
      "5,99 €",
      11,
      0,
      0,
      96.5,
      align_right=True,
      right_mm=73,
  )
  print("Texte '5,99 €' (aligné à droite - Total à payer) inséré dans le PDF.")

  # 15. --- Insertion du texte "Payé avec Visa" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumVisa",
      police_medium,
      "Payé avec Visa",
      9.5,
      0,
      2.1,
      106.5,
  )
  print("Texte 'Payé avec Visa' inséré dans le PDF.")

  # 16. --- Insertion du montant Visa aligné à droite ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumMontantVisa",
      police_medium,
      "5,99 €",
      9.5,
      0,
      0,
      106.5,
      align_right=True,
      right_mm=72.8,
  )
  print("Texte '5,99 €' (aligné à droite) inséré dans le PDF.")

  # 17. --- Insertion de l'image (avis / code) ---
  inserer_image(page, image_avis_path, 74, 0.6, 120.3)
  print("Image avis insérée avec succès dans le PDF.")

  # 18. --- Insertion de l'image "width99.png" (QR Code) ---
  inserer_image(page, image_width99_path, 14, 23.7, 124.5)
  print("QR Code (width99.png) inséré dans le PDF.")

  # 19. --- Insertion du texte "Comment jugez-" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldJuger",
      police_bold,
      "Comment jugez-",
      10.5,
      0,
      39.8,
      124.7,
  )
  print("Texte 'Comment jugez-' inséré dans le PDF.")

  # 19 bis. --- Insertion du texte "vous votre" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldVousVotre",
      police_bold,
      "vous votre",
      10.4,
      0,
      39.8,
      129,
  )
  print("Texte 'vous votre' inséré dans le PDF.")

  # 20. --- Insertion du texte "expérience ?" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldExperience",
      police_bold,
      "expérience ?",
      10.4,
      0,
      39.8,
      133.2,
  )
  print("Texte 'expérience ?' inséré dans le PDF.")

  # 21. --- Insertion du texte "Sinon, répondez en 3 minutes à notre" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumSinon",
      police_medium,
      "Sinon, répondez en 3 minutes à notre",
      8,
      0,
      23.6,
      143.8,
  )
  print("Texte 'Sinon, répondez en 3 minutes à notre' inséré dans le PDF.")

  # 22. --- Insertion du texte "questionnaire sur LEGO.com/" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumQuestionnaire",
      police_medium,
      "questionnaire sur LEGO.com/",
      8,
      0,
      23.6,
      146.5,
  )
  print("Texte 'questionnaire sur LEGO.com/' inséré dans le PDF.")

  # 23. --- Insertion du texte "storesurvey" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumStoreSurvey",
      police_medium,
      "storesurvey",
      8,
      0,
      23.5,
      149.3,
  )
  print("Texte 'storesurvey' inséré dans le PDF.")

  # 24. --- Insertion du texte "Au besoin, utilisez ce code :" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumAuBesoin",
      police_medium,
      "Au besoin, utilisez ce code :",
      8,
      0,
      23.5,
      154.2,
  )
  print("Texte 'Au besoin, utilisez ce code :' inséré dans le PDF.")

  # 25. --- Insertion du code d'avis ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCodeBesoin",
      police_medium,
      "149-64863689-08-24-2026 ",
      8,
      0.25,
      23.5,
      157,
  )
  print("Texte '149-64863689-08-24-2026 ' inséré dans le PDF.")

  # 26. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 168, 1)
  print("Ligne de séparation vectorielle insérée dans le PDF.")

  # 27. --- Insertion du texte "Deviens un LEGO® Insider !" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldInsider",
      police_bold,
      "Deviens un LEGO® Insider !",
      10.5,
      0,
      14,
      170.8,
  )
  print("Texte 'Deviens un LEGO® Insider !' inséré dans le PDF.")

  # 28. --- Insertion du texte d'insiders (Ligne 1) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumInsider1",
      police_medium,
      "Rejoins le programme LEGO® Insiders pour",
      9.7,
      -0.1,
      4,
      177.2,
  )
  print("Texte 'Rejoins le programme LEGO® Insiders pour' inséré dans le PDF.")

  # 29. --- Insertion du texte d'insiders (Ligne 2) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumInsider2",
      police_medium,
      "profiter de formidables avantages et",
      9.7,
      -0.1,
      8.8,
      180.7,
  )
  print("Texte 'profiter de formidables avantages et' inséré dans le PDF.")

  # 30. --- Insertion du texte d'insiders (Ligne 3) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumInsider3",
      police_medium,
      "récompenses LEGO®",
      9.7,
      -0.1,
      21.3,
      184,
  )
  print("Texte 'récompenses LEGO®' inséré dans le PDF.")

  # 31. --- Insertion du texte "LEGO.com/insiders" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumInsiderUrl",
      police_medium,
      "LEGO.com/insiders",
      9.7,
      -0.24,
      22.2,
      189,
  )
  print("Texte 'LEGO.com/insiders' inséré dans le PDF.")

  # 32. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 196.2, 1)
  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 33. --- Insertion du titre "S'abonner aux e-mails" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldAbonner",
      police_bold,
      "S'abonner aux e-mails",
      10.5,
      0,
      18.3,
      198.8,
  )
  print("Texte 'S\\'abonner aux e-mails' inséré dans le PDF.")

  # 34. --- Insertion du texte d'abonnement (ligne 1) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumAbonner1",
      police_medium,
      "Suivez notre actualité en vous abonnant à",
      9.5,
      -0.02,
      4.8,
      205.5,
  )
  print("Texte 'Suivez notre actualité en vous abonnant à' inséré dans le PDF.")

  # 35. --- Insertion du texte d'abonnement (ligne 2) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumAbonner2",
      police_medium,
      "notre programme d'e-mails LEGO.com/email",
      9.5,
      -0.05,
      2.5,
      208.8,
  )
  print("Texte 'notre programme d\\'e-mails LEGO.com/email' inséré dans le PDF.")

  # 36. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 216.2, 1.3)
  print("Dernière ligne de séparation vectorielle insérée dans le PDF.")

  # 37. --- Insertion du titre "Caractéristiques de sécurité" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldSecurite",
      police_bold,
      "Caractéristiques de sécurité",
      10.5,
      0,
      12.9,
      218.8,
  )
  print("Texte 'Caractéristiques de sécurité' inséré dans le PDF.")

  # 38. --- Insertion de l'image "width200.png" ---
  inserer_image(page, image_width200_path, 38.1, 18.4, 228.8)
  print("Image 'width200.png' insérée dans le PDF.")

  # 39. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 293, 1)
  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 40. --- Insertion du texte "Duplicata" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldDuplicata",
      police_bold,
      "Duplicata",
      7.2,
      0,
      2,
      268.1,
  )
  print("Texte 'Duplicata' inséré dans le PDF.")

  # 41. --- Insertion du texte de référence ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumDuplicataRef",
      police_medium,
      "1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286",
      7.2,
      0,
      2,
      270.8,
  )
  print(
      "Texte '1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286' inséré"
      " dans le PDF."
  )

  # 42. --- Insertion du texte "Système de caisse certifié LNE" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumLNE",
      police_medium,
      "Système de caisse certifié LNE",
      7.2,
      0,
      2,
      273.1,
  )
  print("Texte 'Système de caisse certifié LNE' inséré dans le PDF.")

  # 43. --- Insertion du texte légal (1) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumLegal1",
      police_medium,
      "LEGO BRAND RETAIL S.A.S est enregistré au Registre",
      7.2,
      0,
      6.5,
      278.5,
  )
  print(
      "Texte 'LEGO BRAND RETAIL S.A.S est enregistré au Registre' inséré dans"
      " le PDF."
  )

  # 44. --- Insertion du texte légal (2) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumLegal2",
      police_medium,
      "national des metteurs sur le marché des jeux et jouets sous",
      7.2,
      0,
      2.5,
      281,
  )
  print(
      "Texte 'national des metteurs sur le marché des jeux et jouets sous'"
      " inséré dans le PDF."
  )

  # 45. --- Insertion du texte légal (3) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumLegal3",
      police_medium,
      "le numéro FR214763_12TBLL.",
      7.2,
      0,
      20.8,
      283.5,
  )
  print("Texte 'le numéro FR214763_12TBLL.' inséré dans le PDF.")

  # 46. --- Insertion du titre "Ticket de carte bancaire" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldCBTitre",
      police_bold,
      "Ticket de carte bancaire",
      10.5,
      0,
      2,
      295.2,
  )
  print("Texte 'Ticket de carte bancaire' inséré dans le PDF.")

  # 47. --- Insertion du texte "Date/Heure" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBDate",
      police_medium,
      "Date/Heure",
      9.5,
      -0.02,
      2,
      300.8,
  )
  print("Texte 'Date/Heure' inséré dans le PDF.")

  # 48. --- Insertion de la valeur de date CB ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBValeurDate",
      police_medium,
      "24/08/2026 19:35:15",
      9.5,
      -0.1,
      40.8,
      300.8,
  )
  print("Texte '24/08/2026 19:35:15' inséré dans le PDF.")

  # 49. --- Insertion du texte "Carte" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBCarte",
      police_medium,
      "Carte",
      9.5,
      -0.02,
      2,
      304,
  )
  print("Texte 'Carte' inséré dans le PDF.")

  # 50. --- Insertion du texte "**** 0777" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBNumero",
      police_medium,
      "**** 0777",
      9.5,
      0,
      59,
      304,
  )
  print("Texte '**** 0777' inséré dans le PDF.")

  # 51. --- Insertion du texte "Type de carte" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBTypeCarte",
      police_medium,
      "Type de carte",
      9.5,
      -0.02,
      2,
      307.2,
  )
  print("Texte 'Type de carte' inséré dans le PDF.")

  # 52. --- Insertion de la valeur "Visa" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBVisa",
      police_medium,
      "Visa",
      9.5,
      0,
      66.6,
      307.2,
  )
  print("Texte 'Visa' inséré dans le PDF.")

  # 53. --- Insertion du texte "Type de saisie" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBTypeSaisie",
      police_medium,
      "Type de saisie",
      9.5,
      -0.02,
      2,
      310.8,
  )
  print("Texte 'Type de saisie' inséré dans le PDF.")

  # 54. --- Insertion du texte "Puce sans contact" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBPuce",
      police_medium,
      "Puce sans contact",
      9.5,
      0,
      44.7,
      310.8,
  )
  print("Texte 'Puce sans contact' inséré dans le PDF.")

  # 55. --- Insertion du texte "AID" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBAID",
      police_medium,
      "AID",
      9.5,
      -0.02,
      2,
      314.2,
  )
  print("Texte 'AID' inséré dans le PDF.")

  # 56. --- Insertion de la valeur AID ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBAIDValeur",
      police_medium,
      "A0000000031010",
      9.5,
      0,
      45.5,
      314.2,
  )
  print("Texte 'A0000000031010' inséré dans le PDF.")

  # 57. --- Insertion du texte "Code d'autor." ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBAutor",
      police_medium,
      "Code d'autor.",
      9.5,
      -0.02,
      2,
      317.3,
  )
  print("Texte 'Code d\\'autor.' inséré dans le PDF.")

  # 58. --- Insertion de la valeur d'autorisation ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumCBAutorValeur",
      police_medium,
      "056013",
      9.5,
      0,
      62,
      317.3,
  )
  print("Texte '056013' inséré dans le PDF.")

  # 59. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 324.8, 1.3)
  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 60. --- Insertion de l'image "width87.png" ---
  inserer_image(page, image_width87_path, 13.8, 59, 328)
  print("Image 'width87.png' insérée dans le PDF.")

  # 61. --- Insertion du titre "Détails de la commande" ---
  inserer_texte(
      page,
      font_bold,
      "CeraBoldDetailsCommande",
      police_bold,
      "Détails de la commande",
      10.5,
      0,
      2,
      327.3,
  )
  print("Texte 'Détails de la commande' inséré dans le PDF.")

  # 62. --- Insertion du texte "Transaction n°:" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumDetailsTransaction",
      police_medium,
      "Transaction n°:",
      8,
      -0.02,
      2,
      332.8,
  )
  print("Texte 'Transaction n°:' inséré dans le PDF.")

  # 63. --- Insertion de la valeur transaction ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumDetailsTransactionValeur",
      police_medium,
      "LEGO0064863689",
      8,
      -0.02,
      30.5,
      332.8,
  )
  print("Texte 'LEGO0064863689' inséré dans le PDF.")

  # 64. --- Insertion du texte "Date et heure:" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumDetailsDateLabel",
      police_medium,
      "Date et heure:",
      8,
      -0.02,
      2,
      335.3,
  )
  print("Texte 'Date et heure:' inséré dans le PDF.")

  # 65. --- Insertion de la date détails ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumDetailsDateValeur",
      police_medium,
      "24 août 2026",
      8,
      -0.02,
      30.5,
      335.3,
  )
  print("Texte '24 août 2026' inséré dans le PDF.")

  # 66. --- Insertion de l'heure détails ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumDetailsHeureValeur",
      police_medium,
      "19:35:15",
      8,
      -0.02,
      30.4,
      338.2,
  )
  print("Texte '19:35:15' inséré dans le PDF.")

  # 67. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 345, 1)
  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 68. --- Insertion du texte de garantie (L1) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumGarantieL1",
      police_medium,
      "Ce bien bénéficie auprès du vendeur d’une garantie",
      8,
      -0.02,
      3.3,
      347.8,
  )
  print(
      "Texte 'Ce bien bénéficie auprès du vendeur d’une garantie' inséré dans"
      " le PDF."
  )

  # 69. --- Insertion du texte de garantie (L2) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumGarantieL2",
      police_medium,
      "légale de conformité d’une durée de deux ans à",
      8,
      -0.02,
      6,
      350.8,
  )
  print(
      "Texte 'légale de conformité d’une durée de deux ans à' inséré dans le"
      " PDF."
  )

  # 70. --- Insertion du texte de garantie (L3) ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumGarantieL3",
      police_medium,
      "compter de sa remise au consommateur.",
      8,
      -0.02,
      10.7,
      353.5,
  )
  print("Texte 'compter de sa remise au consommateur.' inséré dans le PDF.")

  # 71. --- Insertion de la ligne de séparation vectorielle ---
  dessiner_ligne(page, 2.2, 73, 360.2, 1.3)
  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 72. --- Insertion du texte "LEGO Brand Retail SAS" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumRetailL1",
      police_medium,
      "LEGO Brand Retail SAS",
      8,
      -0.02,
      22.5,
      365.8,
  )
  print("Texte 'LEGO Brand Retail SAS' inséré dans le PDF.")

  # 73. --- Insertion du texte "75 rue de Tocqueville," ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumRetailL2",
      police_medium,
      "75 rue de Tocqueville,",
      8,
      -0.02,
      23.2,
      368.8,
  )
  print("Texte '75 rue de Tocqueville,' inséré dans le PDF.")

  # 74. --- Insertion du texte "75017 Paris, FR" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumRetailL3",
      police_medium,
      "75017 Paris, FR",
      8,
      -0.02,
      28,
      371.5,
  )
  print("Texte '75017 Paris, FR' inséré dans le PDF.")

  # 75. --- Insertion du texte "FR 61752526178" ---
  inserer_texte(
      page,
      font_medium,
      "CeraMediumRetailL4",
      police_medium,
      "FR 61752526178",
      8,
      -0.02,
      27.4,
      374.2,
  )
  print("Texte 'FR 61752526178' inséré dans le PDF.")

  # --- Mise à jour du titre du document (Métadonnées) ---
  meta = doc.metadata
  meta["title"] = "Receipt"
  doc.set_metadata(meta)

  doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
  doc.close()
  print("Génération complète et fusion réussie !")


if __name__ == "__main__":
  executer_generation_complete()